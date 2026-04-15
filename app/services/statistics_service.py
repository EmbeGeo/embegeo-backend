from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sensor_data import SensorData
from app.models.statistics import Statistics
from app.schemas.statistics import (DailyStatisticsResponse, DailySummaryItem,
                                     WeeklySummaryResponse)


class StatisticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_statistics(self, stat_date: date) -> Optional[DailyStatisticsResponse]:
        """일일 통계 조회. statistics 테이블에 없으면 sensor_data에서 계산 후 저장."""
        # statistics 테이블에서 먼저 조회
        query = select(Statistics).where(Statistics.stat_date == stat_date)
        result = await self.db.execute(query)
        stats = result.scalars().first()

        if stats:
            return self._to_daily_response(stats)

        # 없으면 sensor_data에서 계산
        return await self.calculate_and_save_daily_statistics(stat_date)

    async def calculate_and_save_daily_statistics(
        self, stat_date: date
    ) -> Optional[DailyStatisticsResponse]:
        """sensor_data에서 일일 통계 계산 후 statistics 테이블에 저장."""
        start_dt = datetime.combine(stat_date, datetime.min.time())
        end_dt = datetime.combine(stat_date, datetime.max.time())

        query = select(
            func.count(SensorData.id).label("data_points"),
            func.max(SensorData.total_count).label("total_count"),
            func.max(SensorData.error_count).label("error_count"),
            func.avg(SensorData.iso_temp_pv).label("avg_iso_temp_pv"),
            func.avg(SensorData.pol1_temp_pv).label("avg_pol1_temp_pv"),
            func.avg(SensorData.pol2_temp_pv).label("avg_pol2_temp_pv"),
            func.max(SensorData.iso_press).label("max_iso_press"),
            func.min(SensorData.iso_press).label("min_iso_press"),
        ).where(
            SensorData.timestamp >= start_dt,
            SensorData.timestamp <= end_dt,
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row or row.data_points == 0:
            return None

        # statistics 테이블에 저장 (upsert 방식)
        existing = await self.db.execute(
            select(Statistics).where(Statistics.stat_date == stat_date)
        )
        stats = existing.scalars().first()

        if stats:
            stats.total_count = row.total_count or 0
            stats.error_count = row.error_count or 0
            stats.avg_iso_temp_pv = row.avg_iso_temp_pv
            stats.avg_pol1_temp_pv = row.avg_pol1_temp_pv
            stats.avg_pol2_temp_pv = row.avg_pol2_temp_pv
            stats.max_iso_press = row.max_iso_press
            stats.min_iso_press = row.min_iso_press
        else:
            stats = Statistics(
                stat_date=stat_date,
                total_count=row.total_count or 0,
                error_count=row.error_count or 0,
                avg_iso_temp_pv=row.avg_iso_temp_pv,
                avg_pol1_temp_pv=row.avg_pol1_temp_pv,
                avg_pol2_temp_pv=row.avg_pol2_temp_pv,
                max_iso_press=row.max_iso_press,
                min_iso_press=row.min_iso_press,
            )
            self.db.add(stats)

        await self.db.commit()
        await self.db.refresh(stats)

        return DailyStatisticsResponse(
            stat_date=stats.stat_date,
            total_count=stats.total_count,
            error_count=stats.error_count,
            error_rate=round(stats.error_count / stats.total_count * 100, 2)
            if stats.total_count > 0
            else 0.0,
            avg_iso_temp_pv=stats.avg_iso_temp_pv,
            avg_pol1_temp_pv=stats.avg_pol1_temp_pv,
            avg_pol2_temp_pv=stats.avg_pol2_temp_pv,
            max_iso_press=stats.max_iso_press,
            min_iso_press=stats.min_iso_press,
            data_points=row.data_points,
        )

    async def get_weekly_summary(self) -> WeeklySummaryResponse:
        """최근 7일 요약 통계 조회."""
        today = date.today()
        start_date = today - timedelta(days=6)

        query = (
            select(Statistics)
            .where(Statistics.stat_date >= start_date, Statistics.stat_date <= today)
            .order_by(Statistics.stat_date.desc())
        )
        result = await self.db.execute(query)
        stats_list = result.scalars().all()

        daily_data = [
            DailySummaryItem(
                date=s.stat_date,
                total_count=s.total_count,
                error_count=s.error_count,
            )
            for s in stats_list
        ]

        total_production = sum(s.total_count for s in stats_list)
        total_errors = sum(s.error_count for s in stats_list)
        error_rate = (
            round(total_errors / total_production * 100, 2)
            if total_production > 0
            else 0.0
        )

        return WeeklySummaryResponse(
            total_production=total_production,
            total_errors=total_errors,
            error_rate=error_rate,
            daily_data=daily_data,
        )

    def _to_daily_response(self, stats: Statistics) -> DailyStatisticsResponse:
        return DailyStatisticsResponse(
            stat_date=stats.stat_date,
            total_count=stats.total_count,
            error_count=stats.error_count,
            error_rate=round(stats.error_count / stats.total_count * 100, 2)
            if stats.total_count > 0
            else 0.0,
            avg_iso_temp_pv=stats.avg_iso_temp_pv,
            avg_pol1_temp_pv=stats.avg_pol1_temp_pv,
            avg_pol2_temp_pv=stats.avg_pol2_temp_pv,
            max_iso_press=stats.max_iso_press,
            min_iso_press=stats.min_iso_press,
            data_points=0,  # statistics 테이블엔 data_points 없음
        )
