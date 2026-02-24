import pytest
from unittest.mock import AsyncMock, patch
from decimal import Decimal

from arbitrage_notifier.exchanges.binance_client import BinanceClient
from arbitrage_notifier.infra.async_rate_limiter import AsyncRateLimiter


@pytest.mark.asyncio
async def test_binance_success():
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "symbol": "BTCUSDT",
        "bidPrice": "100",
        "askPrice": "101",
    })

    with patch("arbitrage_notifier.exchanges.binance_client.aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        limiter = AsyncRateLimiter(10, Decimal("10"))
        client = BinanceClient(limiter)

        ticker = await client.get_ticker("BTCUSDT")

        assert ticker.exchange == "binance"
        assert ticker.bid.amount == Decimal("100")
        assert ticker.ask.amount == Decimal("101")