from decimal import Decimal
from datetime import datetime, timezone
import httpx

from arbitrage_notifier.domain.ticker import Ticker
from arbitrage_notifier.domain.money import Money
from arbitrage_notifier.infra.async_rate_limiter import AsyncRateLimiter


class CoinbaseClient:
    BASE_URL = "https://api.exchange.coinbase.com"

    def __init__(self, rate_limiter: AsyncRateLimiter):
        self.rate_limiter = rate_limiter
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_ticker(self, product_id: str) -> Ticker:
        await self.rate_limiter.acquire()

        url = f"{self.BASE_URL}/products/{product_id}/book"
        response = await self.client.get(url, params={"level": 1})
        response.raise_for_status()

        data = response.json()

        bid = Decimal(data["bids"][0][0])
        ask = Decimal(data["asks"][0][0])

        return Ticker(
            exchange="coinbase",
            symbol=product_id,
            bid=Money(bid),
            ask=Money(ask),
            timestamp=datetime.now(timezone.utc),
        )

    async def close(self):
        await self.client.aclose()