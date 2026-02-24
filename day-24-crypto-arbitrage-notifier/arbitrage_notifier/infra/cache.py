from typing import Optional, Any, cast, Awaitable
import redis.asyncio as redis

class RedisCache:
    def __init__(
        self,
        url: str = "redis://localhost:6379",
        client: Any = None, 
    ):
        self._redis: redis.Redis = (
            client if client is not None else redis.from_url(url, decode_responses=True)
        )

    async def get(self, key: str) -> Optional[str]:
        return await cast(Awaitable[Optional[str]], self._redis.get(key))

    async def set(self, key: str, value: str, expire: int = 10) -> None:
        await cast(Awaitable[Any], self._redis.set(key, value, ex=expire))

    async def ping(self) -> bool:
        return await cast(Awaitable[bool], self._redis.ping())

    async def close(self) -> None:
        await cast(Awaitable[None], self._redis.close())