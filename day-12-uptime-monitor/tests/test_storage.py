import tempfile
from src.uptime_monitor.storage import Storage
from src.uptime_monitor.models import CheckResult


def test_insert_and_fetch_last():
    with tempfile.NamedTemporaryFile() as tmp:
        storage = Storage(tmp.name)

        result = CheckResult(
            url="http://x",
            timestamp="2026-01-01T00:00:00Z",
            status="UP",
            response_time=120.5,
            error=None,
        )

        storage.insert_check(result)
        last = storage.get_last_check("http://x")

        assert last is not None
        assert last.status == "UP"
        assert last.response_time == 120.5


def test_summary_math():
    with tempfile.NamedTemporaryFile() as tmp:
        storage = Storage(tmp.name)

        storage.insert_check(CheckResult("http://x", "t1", "UP", 100, None))
        storage.insert_check(CheckResult("http://x", "t2", "DOWN", 100, None))

        summary = storage.get_summary("http://x")

        assert summary["total_checks"] == 2
        assert summary["up_count"] == 1
        assert summary["down_count"] == 1
        assert summary["uptime_pct"] == 50.0
