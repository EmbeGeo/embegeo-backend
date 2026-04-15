from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SensorDataCreate(BaseModel):
    timestamp: datetime
    iso_temp_pv: float
    iso_temp_sv: float
    iso_pump_speed: int
    iso_press: float
    pol1_temp_pv: float
    pol1_temp_sv: float
    pol1_pump_speed: int
    pol1_press: float
    pol2_temp_pv: float
    pol2_temp_sv: float
    pol2_pump_speed: int
    pol2_press: float
    mix_motor_speed: int
    total_count: int
    error_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-04-14T09:00:00Z",
                "iso_temp_pv": 180.5,
                "iso_temp_sv": 180.0,
                "iso_pump_speed": 1500,
                "iso_press": 1.55,
                "pol1_temp_pv": 175.2,
                "pol1_temp_sv": 175.0,
                "pol1_pump_speed": 1450,
                "pol1_press": 1.42,
                "pol2_temp_pv": 178.8,
                "pol2_temp_sv": 178.0,
                "pol2_pump_speed": 1480,
                "pol2_press": 1.48,
                "mix_motor_speed": 1200,
                "total_count": 550,
                "error_count": 2,
            }
        }


class SensorDataResponse(BaseModel):
    id: int
    timestamp: datetime
    iso_temp_pv: float
    iso_temp_sv: float
    iso_pump_speed: int
    iso_press: float
    pol1_temp_pv: float
    pol1_temp_sv: float
    pol1_pump_speed: int
    pol1_press: float
    pol2_temp_pv: float
    pol2_temp_sv: float
    pol2_pump_speed: int
    pol2_press: float
    mix_motor_speed: int
    total_count: int
    error_count: int
    received_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SensorDataRangeResponse(BaseModel):
    data: List[SensorDataResponse]
    total: int
    limit: int
    offset: int
