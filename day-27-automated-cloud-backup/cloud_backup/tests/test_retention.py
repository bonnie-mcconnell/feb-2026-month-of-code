import pytest
import time
from cloud_backup.domain.snapshot import Snapshot
from cloud_backup.domain.retention import RetentionPolicy
from cloud_backup.engine.backup_engine import BackupEngine


def test_apply_retention_by_count():
    policy = RetentionPolicy(retain_last=2, retain_days=0)

    now = time.time()

    snaps = [
        Snapshot("1", now - 300, [], [], []),
        Snapshot("2", now - 200, [], [], []),
        Snapshot("3", now - 100, [], [], []),
    ]

    engine = BackupEngine.__new__(BackupEngine)

    retained = engine._apply_retention(snaps, {}, policy, now)

    ids = [s.snapshot_id for s in retained]
    assert ids == ["2", "3"]

def test_validate_accepts_valid_values():
    policy = RetentionPolicy(retain_last=5, retain_days=30)
    policy.validate()  # should not raise


def test_validate_negative_retain_last():
    policy = RetentionPolicy(retain_last=-1, retain_days=10)

    with pytest.raises(ValueError):
        policy.validate()


def test_validate_negative_retain_days():
    policy = RetentionPolicy(retain_last=5, retain_days=-1)

    with pytest.raises(ValueError):
        policy.validate()