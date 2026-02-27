import sys
import pytest
from unittest.mock import patch

from cloud_backup.cli.main import main


def test_main_invalid_config_exits(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["backup", "--config", "missing.json"])

    with pytest.raises(SystemExit):
        main()


def test_main_unsupported_storage(tmp_path, monkeypatch):
    config = tmp_path / "config.json"
    config.write_text("""
    {
        "source_directory": ".",
        "storage": {"type": "invalid"},
        "retention": {"retain_last": 1, "retain_days": 1},
        "retry": {"max_attempts": 1, "backoff_seconds": 0}
    }
    """)

    monkeypatch.setattr(sys, "argv", ["backup", "--config", str(config)])

    with pytest.raises(SystemExit):
        main()


def test_cli_config_error(monkeypatch, tmp_path):
    bad_config = tmp_path / "bad.json"
    bad_config.write_text("{}")

    monkeypatch.setattr(sys, "argv", ["backup", "--config", str(bad_config)])

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 1


def test_cli_success_local(tmp_path, monkeypatch):
    source = tmp_path / "data"
    source.mkdir()

    config = tmp_path / "config.json"
    config.write_text(f"""
    {{
        "source_directory": "{source}",
        "storage": {{
            "type": "local",
            "destination": "{tmp_path}/backup"
        }},
        "retention": {{"retain_last": 1, "retain_days": 1}},
        "retry": {{"max_attempts": 1, "backoff_seconds": 0}}
    }}
    """)

    monkeypatch.setattr(sys, "argv", ["backup", "--config", str(config)])

    main()


def test_cli_verify_mode(tmp_path, monkeypatch):
    source = tmp_path / "data"
    source.mkdir()

    config = tmp_path / "config.json"
    config.write_text(f"""
    {{
        "source_directory": "{source}",
        "storage": {{
            "type": "local",
            "destination": "{tmp_path}/backup"
        }},
        "retention": {{"retain_last": 1, "retain_days": 1}},
        "retry": {{"max_attempts": 1, "backoff_seconds": 0}}
    }}
    """)

    monkeypatch.setattr(sys, "argv", ["backup", "--config", str(config), "--verify"])

    main()