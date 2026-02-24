from decimal import Decimal
from datetime import datetime, timezone
import requests

from domain.ticker import Ticker
from domain.money import Money
from infra.rate_limiter import RateLimiter
from infra.retry import retry
from .base_client import BaseExchangeClient


class CoinbaseClient(BaseExchangeClient):
    BASE_URL = "https://api.exchange.coinbase.com"

    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    def get_ticker(self, product_id: str) -> Ticker:
        if not self.rate_limiter.allow():
            raise RuntimeError("Rate limit exceeded")

        def call() -> dict:
            url = f"{self.BASE_URL}/products/{product_id}/book?level=1"
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
            bid = Decimal(data["bids"][0][0])
            ask = Decimal(data["asks"][0][0])
        except (KeyError, IndexError, ArithmeticError) as exc:
            raise ValueError("Malformed Coinbase response") from exc

        return Ticker(
            exchange="coinbase",
            symbol=product_id,
            bid=Money(bid),
            ask=Money(ask),
            timestamp=datetime.now(timezone.utc),
        )