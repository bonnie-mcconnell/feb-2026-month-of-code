import asyncio
from decimal import Decimal
from time import monotonic

class AsyncRateLimiter:
    def __init__(self, capacity: int, refill_rate_per_second: Decimal):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate = float(refill_rate_per_second)
        self.last_refill = monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self.lock:
            now = monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_refill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return

        await asyncio.sleep(1 / self.refill_rate)
        await self.acquire()