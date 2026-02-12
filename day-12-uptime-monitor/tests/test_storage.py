import tempfile
from pathlib import Path
import pytest

from uptime_monitor.storage import Storage
from uptime_monitor.models import CheckResult, Status

def make_result(status: Status, ts: str):
    return CheckResult(
        url="http://x",
        timestamp=ts,
        status=status,
        response_time=100.0,
        error=None,
    )

def test_insert_and_get_last_check():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        storage = Storage(str(db_path))

        storage.insert_check(make_result("UP", "t1"))
        storage.insert_check(make_result("DOWN", "t2"))

        last = storage.get_last_check("http://x")

        assert last is not None
        assert last.status == "DOWN"
        assert last.timestamp == "t2"

def test_summary_calculates_uptime_percentage():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        storage = Storage(str(db_path))

        storage.insert_check(make_result("UP", "t1"))
        storage.insert_check(make_result("DOWN", "t2"))
        storage.insert_check(make_result("UP", "t3"))

        summary = storage.get_summary("http://x")

        assert summary is not None
        assert summary["total_checks"] == 3
        assert summary["up_count"] == 2
        assert summary["down_count"] == 1
        assert summary["degraded_count"] == 0
        assert summary["uptime_pct"] == (2 / 3) * 100
