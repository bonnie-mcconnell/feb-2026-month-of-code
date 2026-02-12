from src.uptime_monitor.checker import HealthChecker


def test_classify_up():
    checker = HealthChecker(timeout=2)

    status = checker._classify(status_code=200, response_time_ms=50)

    assert status == "UP"


def test_classify_down_on_500():
    checker = HealthChecker(timeout=2)

    status = checker._classify(status_code=500, response_time_ms=20)

    assert status == "DOWN"


def test_classify_degraded_when_slow():
    checker = HealthChecker(timeout=2, degraded_threshold_ms=100)

    status = checker._classify(status_code=200, response_time_ms=150)

    assert status == "DEGRADED"
