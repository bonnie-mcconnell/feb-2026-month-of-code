from unittest.mock import MagicMock

from src.uptime_monitor.monitor import Monitor
from src.uptime_monitor.models import CheckResult


def make_result(status):
    return CheckResult(
        url="http://x",
        timestamp="2026-01-01T00:00:00Z",
        status=status,
        response_time=100,
        error=None,
    )


def test_transition_detected():
    storage = MagicMock()
    checker = MagicMock()

    storage.get_last_check.return_value = make_result("UP")
    checker.check.return_value = make_result("DOWN")

    monitor = Monitor(storage, checker, ["http://x"])
    results = monitor.run_cycle()

    assert results[0].transition is not None
    assert results[0].transition["from"] == "UP"
    assert results[0].transition["to"] == "DOWN"


def test_no_transition_on_first_run():
    storage = MagicMock()
    checker = MagicMock()

    storage.get_last_check.return_value = None
    checker.check.return_value = make_result("UP")

    monitor = Monitor(storage, checker, ["http://x"])
    results = monitor.run_cycle()

    assert results[0].transition is None
