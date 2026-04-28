import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db

logger = logging.getLogger(__name__)
from app.schemas.common import BaseResponse
from app.schemas.sensor_data import (OCRDataIngest, SensorDataCreate,
                                      SensorDataRangeResponse, SensorDataResponse)
from app.services.sensor_service import SensorService

router = APIRouter()


@router.post(
    "/sensor-data",
    status_code=status.HTTP_201_CREATED,
    summary="센서 데이터 수신 및 저장",
)
async def create_sensor_data(
    data: SensorDataCreate,
    db: AsyncSession = Depends(get_db),
):
    """Vision 모듈로부터 센서 데이터 수신 후 저장, 캐싱, WebSocket 브로드캐스트."""
    try:
        sensor_service = SensorService(db)
        saved = await sensor_service.save_sensor_data(data)
        return {
            "id": saved.id,
            "status": "created",
            "message": "센서 데이터가 저장되었습니다",
            "recorded_at": saved.recorded_at,
        }
    except Exception as e:
        logger.error(f"센서 데이터 저장 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="센서 데이터 저장에 실패했습니다",
        )


@router.post(
    "/ingest",
    status_code=status.HTTP_201_CREATED,
    summary="OCR 결과 수신 및 저장",
)
async def ingest_ocr_data(
    data: OCRDataIngest,
    db: AsyncSession = Depends(get_db),
):
    """Vision 모듈 OCR 결과 수신 후 저장, 캐싱, WebSocket 브로드캐스트."""
    try:
        sensor_service = SensorService(db)
        saved = await sensor_service.save_ocr_data(data)
        return {
            "id": saved.id,
            "status": "created",
            "message": "OCR 데이터가 저장되었습니다",
            "recorded_at": saved.recorded_at,
        }
    except Exception as e:
        logger.error(f"OCR 데이터 저장 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OCR 데이터 저장에 실패했습니다",
        )


@router.get(
    "/sensor-data/latest",
    response_model=BaseResponse[SensorDataResponse],
    summary="최신 센서 데이터 조회",
)
async def get_latest_sensor_data(
    db: AsyncSession = Depends(get_db),
):
    """Redis 캐시 우선 조회, 없으면 DB에서 최신 데이터 반환."""
    sensor_service = SensorService(db)
    data = await sensor_service.get_latest_sensor_data()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="센서 데이터가 없습니다",
        )

    return BaseResponse(status="success", data=data)


@router.get(
    "/sensor-data/range",
    response_model=BaseResponse[SensorDataRangeResponse],
    summary="시간 범위로 센서 데이터 조회",
)
async def get_sensor_data_range(
    start_time: datetime = Query(..., description="시작 시간 (ISO 8601)"),
    end_time: datetime = Query(..., description="종료 시간 (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="조회 건수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    db: AsyncSession = Depends(get_db),
):
    """시간 범위 내 센서 데이터 조회 (페이지네이션 지원)."""
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time은 end_time보다 이전이어야 합니다",
        )

    sensor_service = SensorService(db)
    result = await sensor_service.get_sensor_data_range(
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )
    return BaseResponse(status="success", data=result)
