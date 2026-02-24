import pytest
from arbitrage_notifier.infra.async_rate_limiter import AsyncRateLimiter
from decimal import Decimal

@pytest.mark.asyncio
async def test_rate_limiter_acquire_wait():
    limiter = AsyncRateLimiter(1, Decimal("0.01"))
    await limiter.acquire()  # should pass without errors

@pytest.mark.asyncio
async def test_rate_limiter_branch(monkeypatch):
    limiter = AsyncRateLimiter(1, Decimal(1))
    assert limiter.capacity == 1