from src.client import HttpClient
from src.retry import RetryPolicy
from src.rate_limiter import RateLimiter
from src.exceptions import RetryableError


class FakeClock:
    def __init__(self):
        self.current = 0.0

    def time(self):
        return self.current

    def sleep(self, seconds):
        self.current += seconds


def test_middleware_order_retry_wraps_rate_limiter():
    clock = FakeClock()

    retry_sleeps = []

    def retry_sleep(delay):
        retry_sleeps.append(delay)
        clock.sleep(delay)

    retry = RetryPolicy(
        max_attempts=3,
        base_delay=1,
        sleep_fn=retry_sleep,
    )

    limiter = RateLimiter(
        capacity=1,
        refill_rate=1,
        time_fn=clock.time,
        sleep_fn=clock.sleep,
    )

    client = HttpClient(middlewares=[retry, limiter])

    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RetryableError("temporary")
        return "ok"

    result = client.execute(flaky)

    assert result == "ok"
    assert calls["count"] == 3

    # retry happened twice
    assert retry.last_retry_count == 2

    # rate limiter should have required waits for each extra attempt
    # capacity=1, so after first call each attempt requires 1 second refill
    assert clock.current >= 2.0


def test_rate_limiter_applies_per_retry_attempt():
    clock = FakeClock()

    limiter = RateLimiter(
        capacity=2,
        refill_rate=1,
        time_fn=clock.time,
        sleep_fn=clock.sleep,
    )

    retry = RetryPolicy(
        max_attempts=3,
        base_delay=0,
        sleep_fn=clock.sleep,
    )

    client = HttpClient(middlewares=[retry, limiter])

    calls = {"count": 0}

    def always_fail():
        calls["count"] += 1
        raise RetryableError("fail")

    try:
        client.execute(always_fail)
    except RetryableError:
        pass

    # max_attempts=3 → 3 executions
    assert calls["count"] == 3

    # capacity=2 allows first two immediately
    # third must wait 1 second
    assert clock.current == 1.0
