from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.common import BaseResponse
from app.schemas.statistics import DailyStatisticsResponse, WeeklySummaryResponse
from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get(
    "/statistics/daily",
    response_model=BaseResponse[DailyStatisticsResponse],
    summary="일일 통계 조회",
)
async def get_daily_statistics(
    date: date = Query(..., description="조회 날짜 (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 날짜의 일일 통계 조회.
    statistics 테이블에 없으면 sensor_data에서 계산 후 저장.
    """
    statistics_service = StatisticsService(db)
    result = await statistics_service.get_daily_statistics(date)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{date} 날짜의 센서 데이터가 없습니다",
        )

    return BaseResponse(status="success", data=result)


@router.get(
    "/statistics/summary",
    response_model=BaseResponse[WeeklySummaryResponse],
    summary="최근 7일 요약 통계",
)
async def get_weekly_summary(
    db: AsyncSession = Depends(get_db),
):
    """최근 7일간의 생산량, 불량량, 에러율 요약."""
    statistics_service = StatisticsService(db)
    result = await statistics_service.get_weekly_summary()
    return BaseResponse(status="success", data=result)
