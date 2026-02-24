import pytest
from unittest.mock import AsyncMock

from arbitrage_notifier.infra.cache import RedisCache

@pytest.mark.asyncio
async def test_cache_set_get():
    fake_redis = AsyncMock()
    fake_redis.get.return_value = "bar"
    
    cache = RedisCache(client=fake_redis)

    await cache.set("foo", "bar")
    fake_redis.set.assert_called_with("foo", "bar", ex=10)

    value = await cache.get("foo")
    assert value == "bar"

@pytest.mark.asyncio
async def test_cache_ping():
    fake_redis = AsyncMock()
    fake_redis.ping.return_value = True
    
    cache = RedisCache(client=fake_redis)
    assert await cache.ping() is True