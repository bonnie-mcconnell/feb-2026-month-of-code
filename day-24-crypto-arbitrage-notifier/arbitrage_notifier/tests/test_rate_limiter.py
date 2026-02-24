from decimal import Decimal
from arbitrage_notifier.infra.rate_limiter import RateLimiter


class FakeClock:
    def __init__(self):
        self.current = 0.0

    def advance(self, seconds: float):
        self.current += seconds

    def __call__(self):
        return self.current
    

def test_rate_limiter_enforces_capacity():
    clock = FakeClock()
    limiter = RateLimiter(capacity=2, refill_rate_per_second=Decimal("1"), clock=clock)

    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is False


def test_rate_limiter_refills_over_time():
    clock = FakeClock()
    limiter = RateLimiter(capacity=2, refill_rate_per_second=Decimal("1"), clock=clock)

    assert limiter.allow()
    assert limiter.allow()
    assert not limiter.allow()

    clock.advance(1)

    assert limiter.allow()


def test_rate_limiter_does_not_exceed_capacity():
    clock = FakeClock()
    limiter = RateLimiter(capacity=2, refill_rate_per_second=Decimal("10"), clock=clock)

    clock.advance(10)
    assert limiter.allow()
    assert limiter.allow()
    assert not limiter.allow()