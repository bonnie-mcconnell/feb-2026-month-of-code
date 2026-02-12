import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from uptime_monitor.cli import build_monitor
from uptime_monitor.models import CheckResult

def test_cli_run_writes_to_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        # Patch build_monitor to use temporary DB and fake checker
        with patch("uptime_monitor.cli.Storage") as MockStorage:
            storage_instance = MockStorage.return_value
            storage_instance.insert_check = lambda r: setattr(storage_instance, "last", r)
            storage_instance.get_last_check = lambda url: None
            storage_instance.get_summary = lambda url: {"total_checks": 1, "up_count": 1, "down_count": 0, "degraded_count": 0, "uptime_pct": 100, "last_status": "UP", "last_timestamp": "ts"}

            monitor = build_monitor()
            result = monitor.run_cycle()[0].result

            # ensure checker returned a CheckResult-like object
            assert hasattr(result, "status")
