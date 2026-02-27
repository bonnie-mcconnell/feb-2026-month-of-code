import os
import signal
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from cloud_backup.domain.file_record import FileRecord
from cloud_backup.domain.snapshot import Snapshot
from cloud_backup.domain.retention import RetentionPolicy
from cloud_backup.engine.scanner import scan_directory
from cloud_backup.engine.hasher import sha256_file, HashingError
from cloud_backup.engine.index_store import IndexStore
from cloud_backup.infra.retry import retry, RetryExceededError
from cloud_backup.storage.base_adapter import BaseStorageAdapter, StorageError
from cloud_backup.infra.logger import JsonLogger
from cloud_backup.infra.config_loader import AppConfig


class BackupEngine:

    def __init__(
        self,
        config: AppConfig,
        storage: BaseStorageAdapter,
        index_store: IndexStore,
        logger: JsonLogger,
    ):
        self.config = config
        self.storage = storage
        self.index_store = index_store
        self.logger = logger
        self._interrupted = False

        signal.signal(signal.SIGINT, self._handle_interrupt)

    # -------------------------------------------------

    def run(self, *, dry_run: bool = False, force_full: bool = False) -> None:
        start_time = time.time()

        files_index, snapshots = self.index_store.load()

        snapshot_id = self._generate_snapshot_id()
        timestamp = time.time()

        scanned_files = list(scan_directory(self.config.source_directory))
        scanned_set = set(scanned_files)
        indexed_set = set(files_index.keys())

        files_backed_up: List[str] = []
        files_skipped: List[str] = []
        files_deleted: List[str] = []

        # -------------------------------------------------
        # Detect deletions
        # -------------------------------------------------

        deleted_files = indexed_set - scanned_set

        for rel_path in sorted(deleted_files):
            if dry_run:
                files_deleted.append(rel_path)
                continue

            self._delete_with_retry(rel_path)
            files_deleted.append(rel_path)
            files_index.pop(rel_path, None)

        # -------------------------------------------------
        # Determine uploads
        # -------------------------------------------------

        upload_tasks: List[Tuple[str, str, FileRecord]] = []

        for rel_path in sorted(scanned_files):

            if self._interrupted:
                raise RuntimeError("Backup interrupted")

            full_path = os.path.join(self.config.source_directory, rel_path)

            try:
                sha256 = sha256_file(full_path)
            except HashingError as e:
                self.logger.log(
                    "hash_failed",
                    file=rel_path,
                    error=str(e),
                    snapshot_id=snapshot_id,
                )
                continue

            size = os.path.getsize(full_path)
            modified_at = os.path.getmtime(full_path)

            existing = files_index.get(rel_path)

            changed = (
                force_full
                or existing is None
                or existing.sha256 != sha256
            )

            if not changed:
                files_skipped.append(rel_path)
                continue

            if dry_run:
                files_backed_up.append(rel_path)
                continue

            record = FileRecord(
                relative_path=rel_path,
                size=size,
                modified_at=modified_at,
                sha256=sha256,
                last_backup_timestamp=timestamp,
            )

            upload_tasks.append((full_path, rel_path, record))

        # -------------------------------------------------
        # Parallel Upload Execution
        # -------------------------------------------------

        if not dry_run and upload_tasks:

            max_workers = 4  # safe default

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []

                for full_path, rel_path, record in upload_tasks:
                    futures.append(
                        executor.submit(
                            self._upload_with_retry,
                            full_path,
                            rel_path,
                        )
                    )

                for future, task in zip(as_completed(futures), upload_tasks):
                    future.result()
                    _, rel_path, record = task
                    files_index[rel_path] = record
                    files_backed_up.append(rel_path)

        # -------------------------------------------------
        # Snapshot
        # -------------------------------------------------

        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            files_backed_up=files_backed_up,
            files_skipped=files_skipped,
            files_deleted=files_deleted,
        )

        snapshots.append(snapshot)

        # -------------------------------------------------
        # Retention
        # -------------------------------------------------

        if not dry_run:
            snapshots = self._apply_retention(
                snapshots,
                files_index,
                self.config.retention,
                timestamp,
            )

            self.index_store.save(files_index, snapshots)

        duration_ms = int((time.time() - start_time) * 1000)

        self.logger.log(
            "backup_completed",
            snapshot_id=snapshot_id,
            files_backed_up=len(files_backed_up),
            files_skipped=len(files_skipped),
            files_deleted=len(files_deleted),
            duration_ms=duration_ms,
        )

    # -------------------------------------------------

    def _upload_with_retry(self, full_path: str, key: str) -> None:
        start = time.time()

        def op():
            self.storage.upload(full_path, key)

        try:
            retry(
                op,
                max_attempts=self.config.retry.max_attempts,
                backoff_seconds=self.config.retry.backoff_seconds,
                retry_on=(StorageError,),
            )
        except RetryExceededError as e:
            self.logger.log("upload_failed", file=key, error=str(e))
            raise

        duration = int((time.time() - start) * 1000)
        self.logger.log("file_uploaded", file=key, duration_ms=duration)

    # -------------------------------------------------

    def _delete_with_retry(self, key: str) -> None:
        def op():
            self.storage.delete(key)

        retry(
            op,
            max_attempts=self.config.retry.max_attempts,
            backoff_seconds=self.config.retry.backoff_seconds,
            retry_on=(StorageError,),
        )

        self.logger.log("file_deleted", file=key)

    # -------------------------------------------------

    def _apply_retention(
        self,
        snapshots: List[Snapshot],
        files_index: Dict[str, FileRecord],
        policy: RetentionPolicy,
        now: float,
    ) -> List[Snapshot]:

        snapshots_sorted = sorted(snapshots, key=lambda s: s.timestamp)

        retain_by_count = (
            snapshots_sorted[-policy.retain_last:]
            if policy.retain_last > 0
            else []
        )

        cutoff = now - (policy.retain_days * 86400)
        retain_by_time = [
            s for s in snapshots_sorted if s.timestamp >= cutoff
        ]

        retained_ids = {
            s.snapshot_id for s in retain_by_count + retain_by_time
        }

        pruned = [
            s for s in snapshots_sorted
            if s.snapshot_id not in retained_ids
        ]

        for snap in pruned:
            if hasattr(self, "logger") and self.logger:
                self.logger.log(
                    "snapshot_pruned",
                    snapshot_id=snap.snapshot_id,
                )

        return [
            s for s in snapshots_sorted
            if s.snapshot_id in retained_ids
        ]

    # -------------------------------------------------

    def _generate_snapshot_id(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # -------------------------------------------------

    def _handle_interrupt(self, signum, frame):
        self._interrupted = True
        if hasattr(self, "logger") and self.logger:
            self.logger.log("interrupt_received")

    # -------------------------------------------------

    def verify(self) -> None:
        files_index, _ = self.index_store.load()

        corrupted = []

        for rel_path, record in files_index.items():
            try:
                data = self.storage.download(rel_path)
            except Exception as e:
                self.logger.log(
                    "verify_download_failed",
                    file=rel_path,
                    error=str(e),
                )
                corrupted.append(rel_path)
                continue

            sha = hashlib.sha256(data).hexdigest()

            if sha != record.sha256:
                corrupted.append(rel_path)
                self.logger.log("verify_mismatch", file=rel_path)

        if corrupted:
            raise RuntimeError("Verification failed")

        self.logger.log("verification_passed")