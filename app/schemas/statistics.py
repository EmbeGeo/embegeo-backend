from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class DailyStatisticsResponse(BaseModel):
    stat_date: date
    total_count: int
    error_count: int
    error_rate: float
    avg_iso_temp_pv: Optional[float] = None
    avg_pol1_temp_pv: Optional[float] = None
    avg_pol2_temp_pv: Optional[float] = None
    max_iso_press: Optional[float] = None
    min_iso_press: Optional[float] = None
    data_points: int

    class Config:
        from_attributes = True


class DailySummaryItem(BaseModel):
    date: date
    total_count: int
    error_count: int


class WeeklySummaryResponse(BaseModel):
    period: str = "last_7_days"
    total_production: int
    total_errors: int
    error_rate: float
    daily_data: List[DailySummaryItem]
