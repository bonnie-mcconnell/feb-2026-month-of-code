import pytest
from unittest.mock import patch, MagicMock

from src.uptime_monitor.checker import HealthChecker


def test_classify_up_fast():
    checker = HealthChecker(timeout=2, degraded_threshold_ms=500)
    status = checker._classify(200, 100)
    assert status == "UP"


def test_classify_degraded():
    checker = HealthChecker(timeout=2, degraded_threshold_ms=200)
    status = checker._classify(200, 500)
    assert status == "DEGRADED"


def test_classify_down_500():
    checker = HealthChecker(timeout=2)
    status = checker._classify(500, 100)
    assert status == "DOWN"


@patch("monitor.checker.request.urlopen")
def test_check_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_urlopen.return_value.__enter__.return_value = mock_response

    checker = HealthChecker(timeout=2)
    result = checker.check("http://example.com")

    assert result.status in ("UP", "DEGRADED")
    assert result.url == "http://example.com"
    assert result.error is None


@patch("monitor.checker.request.urlopen", side_effect=Exception("boom"))
def test_check_network_error(mock_urlopen):
    checker = HealthChecker(timeout=2)
    result = checker.check("http://example.com")

    assert result.status == "DOWN"
    assert result.error is not None
