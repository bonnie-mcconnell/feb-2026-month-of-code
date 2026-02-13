import time
from typing import Callable

from .middleware import Middleware


class RateLimiter(Middleware):
    """
    Simple token bucket rate limiter.

    Not thread-safe. Intended for single-threaded use.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        time_fn: Callable[[], float] = time.monotonic,
        sleep_fn: Callable[[float], None] = time.sleep,
    ):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")

        if refill_rate <= 0:
            raise ValueError("refill_rate must be > 0")

        self.capacity = capacity
        self.refill_rate = refill_rate

        self.time_fn = time_fn
        self.sleep_fn = sleep_fn

        self.tokens = float(capacity)
        self.last_refill_time = self.time_fn()

        # observability (last acquire only)
        self.last_wait_time = 0.0
        self.last_acquire_loops = 0

    def __call__(self, request_fn):
        def wrapped(*args, **kwargs):
            self._acquire()
            return request_fn(*args, **kwargs)

        return wrapped

    def _acquire(self):
        self.last_wait_time = 0.0
        self.last_acquire_loops = 0

        while True:
            self.last_acquire_loops += 1
            self._refill()

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return

            needed = 1.0 - self.tokens
            wait_time = needed / self.refill_rate

            self.sleep_fn(wait_time)
            self.last_wait_time += wait_time

    def _refill(self):
        now = self.time_fn()
        elapsed = now - self.last_refill_time

        if elapsed <= 0:
            return

        self.tokens += elapsed * self.refill_rate
        if self.tokens > self.capacity:
            self.tokens = float(self.capacity)

        self.last_refill_time = now
