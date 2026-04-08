from typing import Optional

from app.cache.redis_client import redis_client
from app.schemas.data import DataLogResponse


class CacheService:
    def __init__(self):
        self.redis = redis_client
        self.LATEST_DATA_KEY = "latest_ocr_data"

    async def cache_latest_data(self, data: DataLogResponse):
        """Caches the latest OCR data."""
        await self.redis.set(
            self.LATEST_DATA_KEY, data.model_dump_json(), ex=3600
        )  # Cache for 1 hour

    async def get_latest_data(self) -> Optional[DataLogResponse]:
        """Retrieves the latest OCR data from cache."""
        cached_data = await self.redis.get(self.LATEST_DATA_KEY)
        if cached_data:
            return DataLogResponse.model_validate_json(cached_data)
        return None

    async def invalidate_latest(self):
        """Invalidates the latest OCR data cache."""
        await self.redis.delete(self.LATEST_DATA_KEY)
