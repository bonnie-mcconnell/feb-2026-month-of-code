import pytest

from cloud_backup.domain.retention import RetentionPolicy


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