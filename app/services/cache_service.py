from typing import Optional

from app.cache.redis_client import redis_client
from app.schemas.sensor_data import SensorDataResponse


class CacheService:
    def __init__(self):
        self.redis = redis_client
        self.LATEST_DATA_KEY = "latest_sensor_data"
        self.TTL = 30  # 5초 주기로 데이터가 들어오므로 30초 TTL

    async def cache_latest_sensor_data(self, data: SensorDataResponse):
        """최신 센서 데이터를 Redis에 캐싱."""
        await self.redis.set(self.LATEST_DATA_KEY, data.model_dump_json(), ex=self.TTL)

    async def get_cached_latest_sensor_data(self) -> Optional[SensorDataResponse]:
        """Redis 캐시에서 최신 센서 데이터 조회."""
        cached_data = await self.redis.get(self.LATEST_DATA_KEY)
        if cached_data:
            return SensorDataResponse.model_validate_json(cached_data)
        return None

    async def invalidate_latest(self):
        """최신 센서 데이터 캐시 무효화."""
        await self.redis.delete(self.LATEST_DATA_KEY)
