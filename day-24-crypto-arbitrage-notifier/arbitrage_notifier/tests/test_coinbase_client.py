from unittest.mock import patch, Mock
from decimal import Decimal
import pytest

from arbitrage_notifier.exchanges.coinbase_client import CoinbaseClient
from arbitrage_notifier.infra.rate_limiter import RateLimiter


def test_coinbase_success():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "bids": [["100", "1"]],
        "asks": [["101", "1"]],
    }

    with patch("arbitrage_notifier.exchanges.coinbase_client.requests.get", return_value=mock_response):
        limiter = RateLimiter(10, Decimal("10"))
        client = CoinbaseClient(limiter)

        ticker = client.get_ticker("BTC-USD")

        assert ticker.exchange == "coinbase"
        assert ticker.bid.amount == Decimal("100")
        assert ticker.ask.amount == Decimal("101")


def test_coinbase_malformed():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch("arbitrage_notifier.exchanges.coinbase_client.requests.get", return_value=mock_response):
        limiter = RateLimiter(10, Decimal("10"))
        client = CoinbaseClient(limiter)

        with pytest.raises(ValueError):
            client.get_ticker("BTC-USD")