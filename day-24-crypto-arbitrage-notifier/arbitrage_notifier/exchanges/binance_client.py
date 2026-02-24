from decimal import Decimal
from datetime import datetime, timezone
import requests

from arbitrage_notifier.domain.ticker import Ticker
from arbitrage_notifier.domain.money import Money
from arbitrage_notifier.infra.rate_limiter import RateLimiter
from arbitrage_notifier.infra.retry import retry
from .base_client import BaseExchangeClient


class BinanceClient(BaseExchangeClient):
    BASE_URL = "https://api.binance.com"

    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    def get_ticker(self, symbol: str) -> Ticker:
        if not self.rate_limiter.allow():
            raise RuntimeError("Rate limit exceeded")

        def call() -> dict[str, str]:
            url = f"{self.BASE_URL}/api/v3/ticker/bookTicker?symbol={symbol}"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                raise ValueError(f"HTTP {response.status_code}")

            return response.json()

        data = retry(
            call,
            max_attempts=3,
            base_delay=Decimal("0.5"),
            backoff_multiplier=Decimal("2"),
            retry_on=(ValueError,),
        )

        try:
            bid = Decimal(data["bidPrice"])
            ask = Decimal(data["askPrice"])
        except (KeyError, ArithmeticError) as exc:
            raise ValueError("Malformed Binance response") from exc

        return Ticker(
            exchange="binance",
            symbol=symbol,
            bid=Money(bid),
            ask=Money(ask),
            timestamp=datetime.now(timezone.utc),
        )