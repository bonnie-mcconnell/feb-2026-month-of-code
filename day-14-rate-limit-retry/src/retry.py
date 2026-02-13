import time
import random
from typing import Callable

from .middleware import Middleware
from .exceptions import RetryableError


class RetryPolicy(Middleware):
    def __init__(
        self,
        max_attempts: int,
        base_delay: float,
        backoff_factor: float = 2.0,
        jitter: bool = False,
        sleep_fn: Callable[[float], None] = time.sleep,
        random_fn: Callable[[], float] = random.random,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")

        if base_delay < 0:
            raise ValueError("base_delay must be >= 0")

        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

        self.sleep_fn = sleep_fn
        self.random_fn = random_fn

        # observability (last execution only)
        self.last_attempt_count = 0
        self.last_retry_count = 0
        self.last_total_wait = 0.0
        self.last_failure = None

    def __call__(self, request_fn: Callable):
        def wrapped(*args, **kwargs):
            self.last_attempt_count = 0
            self.last_retry_count = 0
            self.last_total_wait = 0.0
            self.last_failure = None

            attempt = 1

            while True:
                try:
                    self.last_attempt_count = attempt
                    return request_fn(*args, **kwargs)

                except RetryableError as exc:
                    self.last_failure = exc

                    if attempt >= self.max_attempts:
                        raise

                    delay = self._compute_backoff(attempt)

                    self.sleep_fn(delay)
                    self.last_total_wait += delay
                    self.last_retry_count += 1

                    attempt += 1

        return wrapped

    def _compute_backoff(self, attempt: int) -> float:
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))

        if self.jitter:
            delay = delay * self.random_fn()

        return delay
