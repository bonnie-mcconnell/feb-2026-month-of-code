from decimal import Decimal
from datetime import datetime, timezone
import httpx

from arbitrage_notifier.domain.ticker import Ticker
from arbitrage_notifier.domain.money import Money
from arbitrage_notifier.infra.async_rate_limiter import AsyncRateLimiter


class BinanceClient:
    BASE_URL = "https://api.binance.com"

    def __init__(self, rate_limiter: AsyncRateLimiter):
        self.rate_limiter = rate_limiter
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_ticker(self, symbol: str) -> Ticker:
        await self.rate_limiter.acquire()

        url = f"{self.BASE_URL}/api/v3/ticker/bookTicker"
        response = await self.client.get(url, params={"symbol": symbol})
        response.raise_for_status()

        data = response.json()

        bid = Decimal(data["bidPrice"])
        ask = Decimal(data["askPrice"])

        return Ticker(
            exchange="binance",
            symbol=symbol,
            bid=Money(bid),
            ask=Money(ask),
            timestamp=datetime.now(timezone.utc),
        )

    async def close(self):
        await self.client.aclose()