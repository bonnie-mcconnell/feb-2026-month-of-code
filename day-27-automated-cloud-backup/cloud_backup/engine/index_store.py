import json
import os
import tempfile
from typing import Dict, List

from cloud_backup.domain.file_record import FileRecord
from cloud_backup.domain.snapshot import Snapshot


INDEX_VERSION = 1


class IndexCorruptedError(Exception):
    pass


class IndexStore:
    def __init__(self, index_path: str):
        self.index_path = index_path

    # -------------------------
    # Public API
    # -------------------------

    def load(self) -> tuple[Dict[str, FileRecord], List[Snapshot]]:
        if not os.path.exists(self.index_path):
            return {}, []

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            raise IndexCorruptedError(f"Failed to load index: {e}") from e

        if raw.get("version") != INDEX_VERSION:
            raise IndexCorruptedError("Unsupported index version")

        files = {
            path: FileRecord.from_dict(path, data)
            for path, data in raw.get("files", {}).items()
        }

        snapshots = [
            Snapshot.from_dict(s)
            for s in raw.get("snapshots", [])
        ]

        return files, snapshots

    def save(
        self,
        files: Dict[str, FileRecord],
        snapshots: List[Snapshot],
        created_at: float | None = None,
    ) -> None:
        existing_created_at = created_at

        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                existing_created_at = raw.get("created_at")
            except Exception:
                pass  # do not trust corrupted index

        payload = {
            "version": INDEX_VERSION,
            "created_at": existing_created_at,
            "updated_at": self._now(),
            "files": {
                path: record.to_dict()
                for path, record in sorted(files.items())
            },
            "snapshots": [
                s.to_dict() for s in snapshots
            ],
        }

        if payload["created_at"] is None:
            payload["created_at"] = self._now()

        self._atomic_write(payload)

    # -------------------------
    # Internal
    # -------------------------

    def _atomic_write(self, payload: dict) -> None:
        directory = os.path.dirname(self.index_path) or "."
        os.makedirs(directory, exist_ok=True)

        fd, temp_path = tempfile.mkstemp(dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                json.dump(payload, tmp, indent=2, sort_keys=True)
                tmp.flush()
                os.fsync(tmp.fileno())

            os.replace(temp_path, self.index_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _now(self) -> float:
        import time
        return time.time()