from unittest.mock import patch, Mock
from decimal import Decimal
import pytest

from exchanges.binance_client import BinanceClient
from infra.rate_limiter import RateLimiter
from infra.retry import RetryError


def test_binance_success():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "symbol": "BTCUSDT",
        "bidPrice": "100",
        "askPrice": "101",
    }

    with patch("exchanges.binance_client.requests.get", return_value=mock_response):
        limiter = RateLimiter(10, Decimal("10"))
        client = BinanceClient(limiter)

        ticker = client.get_ticker("BTCUSDT")

        assert ticker.exchange == "binance"
        assert ticker.bid.amount == Decimal("100")
        assert ticker.ask.amount == Decimal("101")


def test_binance_retries_on_http_error():
    bad = Mock(status_code=500)
    good = Mock(status_code=200)
    good.json.return_value = {
        "symbol": "BTCUSDT",
        "bidPrice": "100",
        "askPrice": "101",
    }

    with patch(
        "exchanges.binance_client.requests.get",
        side_effect=[bad, good],
    ):
        limiter = RateLimiter(10, Decimal("10"))
        client = BinanceClient(limiter)

        ticker = client.get_ticker("BTCUSDT")

        assert ticker.exchange == "binance"


def test_binance_rate_limit_exceeded():
    mock_response = Mock(status_code=200)
    mock_response.json.return_value = {
        "symbol": "BTCUSDT",
        "bidPrice": "100",
        "askPrice": "101",
    }

    with patch("exchanges.binance_client.requests.get", return_value=mock_response):
        limiter = RateLimiter(1, Decimal("1"))  # second call fails
        client = BinanceClient(limiter)

        client.get_ticker("BTCUSDT")

        with pytest.raises(RuntimeError):
            client.get_ticker("BTCUSDT")


def test_binance_malformed_response():
    mock_response = Mock(status_code=200)
    mock_response.json.return_value = {"bad": "data"}

    with patch("exchanges.binance_client.requests.get", return_value=mock_response):
        limiter = RateLimiter(10, Decimal("10"))
        client = BinanceClient(limiter)

        with pytest.raises(ValueError):
            client.get_ticker("BTCUSDT")