import json
import os

from cloud_backup.engine.backup_engine import BackupEngine
from cloud_backup.engine.index_store import IndexStore
from cloud_backup.storage.local_adapter import LocalStorageAdapter
from cloud_backup.infra.logger import JsonLogger
from cloud_backup.infra.config_loader import AppConfig, StorageConfig, RetryConfig
from cloud_backup.domain.retention import RetentionPolicy


def build_config(src, dest):
    return AppConfig(
        source_directory=str(src),
        storage=StorageConfig(type="local", destination=str(dest)),
        retention=RetentionPolicy(retain_last=5, retain_days=30),
        retry=RetryConfig(max_attempts=2, backoff_seconds=0),
    )


def test_initial_backup(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()

    (src / "file.txt").write_text("hello")

    config = build_config(src, dest)
    storage = LocalStorageAdapter(str(dest))
    index_store = IndexStore(str(dest / "index.json"))
    logger = JsonLogger(debug=False)

    engine = BackupEngine(config, storage, index_store, logger)
    engine.run()

    assert (dest / "objects" / "file.txt").exists()

    with open(dest / "index.json") as f:
        data = json.load(f)

    assert "file.txt" in data["files"]


def test_incremental_skips_unchanged(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()

    (src / "file.txt").write_text("hello")

    config = build_config(src, dest)
    storage = LocalStorageAdapter(str(dest))
    index_store = IndexStore(str(dest / "index.json"))
    logger = JsonLogger(debug=False)

    engine = BackupEngine(config, storage, index_store, logger)
    engine.run()

    before = os.stat(dest / "objects" / "file.txt").st_mtime

    engine.run()

    after = os.stat(dest / "objects" / "file.txt").st_mtime

    assert before == after


def test_modified_file_triggers_upload(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()

    f = src / "file.txt"
    f.write_text("hello")

    config = build_config(src, dest)
    storage = LocalStorageAdapter(str(dest))
    index_store = IndexStore(str(dest / "index.json"))
    logger = JsonLogger(debug=False)

    engine = BackupEngine(config, storage, index_store, logger)
    engine.run()

    f.write_text("changed")
    engine.run()

    with open(dest / "index.json") as f:
        data = json.load(f)

    assert data["files"]["file.txt"]["sha256"] != ""