from decimal import Decimal
from time import monotonic
from typing import Callable


class RateLimiter:
    def __init__(
        self,
        capacity: int,
        refill_rate_per_second: Decimal,
        clock: Callable[[], float] | None = None,
    ):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        if refill_rate_per_second <= Decimal("0"):
            raise ValueError("Refill rate must be positive")

        self.capacity = Decimal(capacity)
        self.refill_rate = refill_rate_per_second
        self.tokens = Decimal(capacity)
        self.clock = clock or monotonic
        self.last_refill = Decimal(str(self.clock()))

    def allow(self) -> bool:
        now = Decimal(str(self.clock()))
        elapsed = now - self.last_refill

        if elapsed > Decimal("0"):
            refill_amount = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + refill_amount)
            self.last_refill = now

        if self.tokens >= Decimal("1"):
            self.tokens -= Decimal("1")
            return True

        return False