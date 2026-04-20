import logging
from typing import Optional

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    _instance: Optional["RedisClient"] = None
    _redis: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    settings.REDIS_URL, decode_responses=True
                )
                await self._redis.ping()
                logger.info("Redis connected successfully")
            except redis.ConnectionError as e:
                logger.error(f"Could not connect to Redis: {e}")
                self._redis = None

    async def disconnect(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis disconnected")

    async def get(self, key: str) -> Optional[str]:
        if not self._redis:
            await self.connect()  # Attempt to reconnect if not connected
            if not self._redis:
                return None  # If reconnect fails, return None

        return await self._redis.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        if not self._redis:
            await self.connect()  # Attempt to reconnect if not connected
            if not self._redis:
                return  # If reconnect fails, do nothing

        await self._redis.set(key, value, ex=ex)

    async def delete(self, key: str):
        if not self._redis:
            await self.connect()  # Attempt to reconnect if not connected
            if not self._redis:
                return  # If reconnect fails, do nothing

        await self._redis.delete(key)


redis_client = RedisClient()
