import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal

from arbitrage_notifier.exchanges.coinbase_client import CoinbaseClient
from arbitrage_notifier.infra.async_rate_limiter import AsyncRateLimiter


@pytest.mark.asyncio
async def test_coinbase_success():
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json = AsyncMock(return_value={
        "bids": [["100", "1"]],
        "asks": [["101", "1"]],
    })

    with patch("arbitrage_notifier.exchanges.coinbase_client.httpx.AsyncClient.get", return_value=mock_response):
        limiter = AsyncRateLimiter(10, Decimal("10"))
        client = CoinbaseClient(limiter)

        ticker = await client.get_ticker("BTC-USD")

        assert ticker.exchange == "coinbase"
        assert ticker.bid.amount == Decimal("100")
        assert ticker.ask.amount == Decimal("101")


@pytest.mark.asyncio
async def test_coinbase_http_error():
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock(side_effect=Exception("HTTP error"))
    mock_response.json = AsyncMock()

    with patch("arbitrage_notifier.exchanges.coinbase_client.httpx.AsyncClient.get", return_value=mock_response):
        limiter = AsyncRateLimiter(10, Decimal("10"))
        client = CoinbaseClient(limiter)

        with pytest.raises(Exception):
            await client.get_ticker("BTC-USD")