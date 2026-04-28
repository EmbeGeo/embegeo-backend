from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_log import ErrorLog
from app.models.sensor_data import SensorData
from app.schemas.sensor_data import (OCRDataIngest, SensorDataCreate,
                                      SensorDataRangeResponse, SensorDataResponse)
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
            await self._log_error(field="unknown", error_type="PARSE_FAIL", error_detail=str(e))
            raise

        # Redis 캐싱
        response = SensorDataResponse.model_validate(sensor_data)
        await self.cache_service.cache_latest_sensor_data(response)

        # WebSocket 브로드캐스트
        await websocket_manager.broadcast(response.model_dump_json())

        return sensor_data

    async def save_ocr_data(self, data: OCRDataIngest) -> SensorData:
        """OCR 결과 데이터 저장 후 캐싱 및 WebSocket 브로드캐스트."""
        sensor_data = SensorData(**data.to_sensor_data_dict())
        self.db.add(sensor_data)

        try:
            await self.db.commit()
            await self.db.refresh(sensor_data)
        except Exception as e:
            await self.db.rollback()
            await self._log_error(field="unknown", error_type="PARSE_FAIL", error_detail=str(e))
            raise

        response = SensorDataResponse.model_validate(sensor_data)
        await self.cache_service.cache_latest_sensor_data(response)
        await websocket_manager.broadcast(response.model_dump_json())

        return sensor_data

    async def get_latest_sensor_data(self) -> Optional[SensorDataResponse]:
        """최신 센서 데이터 조회 (Redis 캐시 우선, 없으면 DB)."""
        # 캐시 먼저 확인
        cached = await self.cache_service.get_cached_latest_sensor_data()
        if cached:
            return cached

        # DB에서 최신 데이터 조회
        query = select(SensorData).order_by(SensorData.recorded_at.desc()).limit(1)
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
            SensorData.recorded_at >= start_time,
            SensorData.recorded_at <= end_time,
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # 데이터 조회
        query = (
            select(SensorData)
            .where(
                SensorData.recorded_at >= start_time,
                SensorData.recorded_at <= end_time,
            )
            .order_by(SensorData.recorded_at.asc())
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
        field: str,
        error_type: str,
        error_detail: Optional[str] = None,
    ):
        """ocr_errors 테이블에 에러 기록."""
        try:
            error_log = ErrorLog(
                field=field,
                error_type=error_type,
                error_detail=error_detail,
            )
            self.db.add(error_log)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
