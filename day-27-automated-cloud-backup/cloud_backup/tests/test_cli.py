import pytest
import sys
from cloud_backup.cli.main import main


def test_cli_config_error(monkeypatch, tmp_path):
    bad_config = tmp_path / "bad.json"
    bad_config.write_text("{}")

    monkeypatch.setattr(sys, "argv", ["backup", "--config", str(bad_config)])

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 1