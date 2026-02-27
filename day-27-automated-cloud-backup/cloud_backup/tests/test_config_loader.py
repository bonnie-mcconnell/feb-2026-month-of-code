import json
import tempfile
import os
import pytest

from cloud_backup.infra.config_loader import load_config, ConfigError


def write_config(data: dict) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.write(json.dumps(data).encode())
    tmp.close()
    return tmp.name


def test_invalid_storage_type():
    path = write_config({
        "source": ".",
        "storage": {"type": "invalid"},
    })

    with pytest.raises(ConfigError):
        load_config(path)


def test_missing_bucket_for_s3():
    path = write_config({
        "source": ".",
        "storage": {"type": "s3"},
    })

    with pytest.raises(ConfigError):
        load_config(path)


def test_negative_retry():
    path = write_config({
        "source": ".",
        "storage": {"type": "local", "destination": "."},
        "retry": {"max_attempts": -1}
    })

    with pytest.raises(ConfigError):
        load_config(path)