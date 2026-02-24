import pytest
from unittest.mock import AsyncMock, patch
from decimal import Decimal

from arbitrage_notifier.exchanges.coinbase_client import CoinbaseClient
from arbitrage_notifier.infra.async_rate_limiter import AsyncRateLimiter


@pytest.mark.asyncio
async def test_coinbase_success():
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "bids": [["100", "1"]],
        "asks": [["101", "1"]],
    })

    with patch("arbitrage_notifier.exchanges.coinbase_client.httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        limiter = AsyncRateLimiter(10, Decimal("10"))
        client = CoinbaseClient(limiter)

        ticker = await client.get_ticker("BTC-USD")

        assert ticker.exchange == "coinbase"
        assert ticker.bid.amount == Decimal("100")
        assert ticker.ask.amount == Decimal("101")