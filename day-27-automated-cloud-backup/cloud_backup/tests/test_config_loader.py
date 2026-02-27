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


def test_valid_local_config(tmp_path):
    source = tmp_path / "data"
    source.mkdir()

    config_path = write_config({
        "source_directory": str(source),
        "storage": {
            "type": "local",
            "destination": str(tmp_path / "backup")
        },
        "retention": {
            "retain_last": 3,
            "retain_days": 7
        },
        "retry": {
            "max_attempts": 2,
            "backoff_seconds": 1
        }
    })

    config = load_config(config_path)

    assert config.storage.type == "local"
    assert config.retention.retain_last == 3