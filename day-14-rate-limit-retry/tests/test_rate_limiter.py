from src.rate_limiter import RateLimiter


class FakeClock:
    def __init__(self):
        self.current = 0.0

    def time(self):
        return self.current

    def sleep(self, seconds):
        self.current += seconds


def test_allows_initial_burst():
    clock = FakeClock()

    limiter = RateLimiter(
        capacity=3,
        refill_rate=1,
        time_fn=clock.time,
        sleep_fn=clock.sleep,
    )

    calls = {"count": 0}

    def request():
        calls["count"] += 1

    wrapped = limiter(request)

    wrapped()
    wrapped()
    wrapped()

    assert calls["count"] == 3
    assert limiter.last_wait_time == 0.0


def test_blocks_when_empty_and_refills():
    clock = FakeClock()

    limiter = RateLimiter(
        capacity=1,
        refill_rate=1,  # 1 token per second
        time_fn=clock.time,
        sleep_fn=clock.sleep,
    )

    calls = {"count": 0}

    def request():
        calls["count"] += 1

    wrapped = limiter(request)

    wrapped()  # consumes initial token
    wrapped()  # must wait 1 second

    assert calls["count"] == 2
    assert limiter.last_wait_time == 1.0
    assert clock.current == 1.0


def test_partial_refill_behavior():
    clock = FakeClock()

    limiter = RateLimiter(
        capacity=2,
        refill_rate=2,  # 2 tokens per second
        time_fn=clock.time,
        sleep_fn=clock.sleep,
    )

    calls = {"count": 0}

    def request():
        calls["count"] += 1

    wrapped = limiter(request)

    wrapped()  # tokens: 1
    wrapped()  # tokens: 0

    # advance half second → 1 token refilled
    clock.current += 0.5

    wrapped()  # should not block

    assert calls["count"] == 3
    assert limiter.last_wait_time == 0.0


def test_capacity_not_exceeded():
    clock = FakeClock()

    limiter = RateLimiter(
        capacity=2,
        refill_rate=10,
        time_fn=clock.time,
        sleep_fn=clock.sleep,
    )

    # advance large time
    clock.current += 100

    limiter._refill()

    assert limiter.tokens == 2.0  # capped at capacity
