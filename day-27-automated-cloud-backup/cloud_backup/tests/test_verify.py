import hashlib
import pytest
from unittest.mock import MagicMock

from cloud_backup.engine.backup_engine import BackupEngine
from cloud_backup.domain.file_record import FileRecord


def test_verify_pass(monkeypatch):
    engine = BackupEngine.__new__(BackupEngine)

    fake_record = FileRecord(
        relative_path="file.txt",
        size=5,
        modified_at=0,
        sha256=hashlib.sha256(b"hello").hexdigest(),
        last_backup_timestamp=0,
    )

    engine.index_store = MagicMock()
    engine.index_store.load.return_value = (
        {"file.txt": fake_record},
        [],
    )

    engine.storage = MagicMock()
    engine.storage.download.return_value = b"hello"

    engine.logger = MagicMock()

    engine.verify()


def test_verify_fail(monkeypatch):
    engine = BackupEngine.__new__(BackupEngine)

    fake_record = FileRecord(
        relative_path="file.txt",
        size=5,
        modified_at=0,
        sha256="wronghash",
        last_backup_timestamp=0,
    )

    engine.index_store = MagicMock()
    engine.index_store.load.return_value = (
        {"file.txt": fake_record},
        [],
    )

    engine.storage = MagicMock()
    engine.storage.download.return_value = b"hello"

    engine.logger = MagicMock()

    with pytest.raises(RuntimeError):
        engine.verify()