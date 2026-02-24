import redis.asyncio as redis
from typing import Optional

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379"):
        self._redis = redis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, expire: int = 10) -> None:
        await self._redis.set(key, value, ex=expire)

    async def close(self):
        await self._redis.close()