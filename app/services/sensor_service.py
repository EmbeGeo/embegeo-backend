from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_log import ErrorLog
from app.models.sensor_data import SensorData
from app.schemas.sensor_data import (SensorDataCreate, SensorDataRangeResponse,
                                      SensorDataResponse)
from app.services.cache_service import CacheService
from app.services.validation_service import ValidationService
from app.websocket.manager import websocket_manager


class SensorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_service = CacheService()

    async def save_sensor_data(self, data: SensorDataCreate) -> SensorData:
        """센서 데이터 저장 후 캐싱 및 WebSocket 브로드캐스트."""
        sensor_data = SensorData(**data.model_dump())
        self.db.add(sensor_data)

        try:
            await self.db.commit()
            await self.db.refresh(sensor_data)
        except Exception as e:
            await self.db.rollback()
            # DB 저장 실패 시 error_logs 기록
            await self._log_error(
                sensor_data_id=None,
                error_type="DB_SAVE_ERROR",
                error_message=str(e),
            )
            raise

        # 센서값 비정상 범위 체크 후 error_logs 기록
        if ValidationService.is_out_of_range(data):
            await self._log_error(
                sensor_data_id=sensor_data.id,
                error_type="OUT_OF_RANGE",
                error_message="센서값이 정상 범위를 벗어났습니다.",
            )

        # Redis 캐싱
        response = SensorDataResponse.model_validate(sensor_data)
        await self.cache_service.cache_latest_sensor_data(response)

        # WebSocket 브로드캐스트
        await websocket_manager.broadcast(response.model_dump_json())

        return sensor_data

    async def get_latest_sensor_data(self) -> Optional[SensorDataResponse]:
        """최신 센서 데이터 조회 (Redis 캐시 우선, 없으면 DB)."""
        # 캐시 먼저 확인
        cached = await self.cache_service.get_cached_latest_sensor_data()
        if cached:
            return cached

        # DB에서 최신 데이터 조회
        query = select(SensorData).order_by(SensorData.id.desc()).limit(1)
        result = await self.db.execute(query)
        sensor_data = result.scalars().first()

        if not sensor_data:
            return None

        response = SensorDataResponse.model_validate(sensor_data)
        # 캐시에 저장
        await self.cache_service.cache_latest_sensor_data(response)
        return response

    async def get_sensor_data_range(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100,
        offset: int = 0,
    ) -> SensorDataRangeResponse:
        """시간 범위로 센서 데이터 조회."""
        # 전체 건수
        count_query = select(func.count(SensorData.id)).where(
            SensorData.timestamp >= start_time,
            SensorData.timestamp <= end_time,
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # 데이터 조회
        query = (
            select(SensorData)
            .where(
                SensorData.timestamp >= start_time,
                SensorData.timestamp <= end_time,
            )
            .order_by(SensorData.timestamp.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        records = result.scalars().all()

        return SensorDataRangeResponse(
            data=[SensorDataResponse.model_validate(r) for r in records],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def _log_error(
        self,
        sensor_data_id: Optional[int],
        error_type: str,
        error_message: str,
    ):
        """error_logs 테이블에 에러 기록."""
        try:
            error_log = ErrorLog(
                sensor_data_id=sensor_data_id,
                error_type=error_type,
                error_message=error_message,
            )
            self.db.add(error_log)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
