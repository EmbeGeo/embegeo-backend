from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class OCRResults(BaseModel):
    pol1_press: str
    pol2_press: str
    pol1_pump_speed: str
    pol2_pump_speed: str
    pol1_temp_pv: str
    pol1_temp_sv: str
    pol2_temp_pv: str
    pol2_temp_sv: str
    hot_water_temp_pv: str
    hot_water_temp_sv: str
    iso_temp_pv: str
    iso_temp_sv: str
    iso_pump_speed: str
    iso_press: str


class OCRDataIngest(BaseModel):
    timestamp: str  # "2026-04-27 17:37:10"
    status: str
    results: OCRResults

    def to_sensor_data_dict(self) -> dict:
        r = self.results
        return {
            "recorded_at": datetime.strptime(self.timestamp, "%Y-%m-%d %H:%M:%S"),
            "pol1_press": float(r.pol1_press),
            "pol2_press": float(r.pol2_press),
            "pol1_pump_speed": int(float(r.pol1_pump_speed)),
            "pol2_pump_speed": int(float(r.pol2_pump_speed)),
            "pol1_temp_pv": float(r.pol1_temp_pv),
            "pol1_temp_sv": float(r.pol1_temp_sv),
            "pol2_temp_pv": float(r.pol2_temp_pv),
            "pol2_temp_sv": float(r.pol2_temp_sv),
            "hot_water_temp_pv": float(r.hot_water_temp_pv),
            "hot_water_temp_sv": float(r.hot_water_temp_sv),
            "iso_temp_pv": float(r.iso_temp_pv),
            "iso_temp_sv": float(r.iso_temp_sv),
            "iso_pump_speed": int(float(r.iso_pump_speed)),
            "iso_press": float(r.iso_press),
        }


class SensorDataCreate(BaseModel):
    recorded_at: datetime
    iso_temp_pv: Optional[float] = None
    iso_temp_sv: Optional[float] = None
    iso_pump_speed: Optional[int] = None
    iso_press: Optional[float] = None
    pol1_temp_pv: Optional[float] = None
    pol1_temp_sv: Optional[float] = None
    pol1_pump_speed: Optional[int] = None
    pol1_press: Optional[float] = None
    pol2_temp_pv: Optional[float] = None
    pol2_temp_sv: Optional[float] = None
    pol2_pump_speed: Optional[int] = None
    pol2_press: Optional[float] = None
    hot_water_temp_pv: Optional[float] = None
    hot_water_temp_sv: Optional[float] = None


class SensorDataResponse(BaseModel):
    id: int
    recorded_at: datetime
    ai_recognized_at: Optional[datetime] = None
    iso_temp_pv: Optional[float] = None
    iso_temp_sv: Optional[float] = None
    iso_pump_speed: Optional[int] = None
    iso_press: Optional[float] = None
    pol1_temp_pv: Optional[float] = None
    pol1_temp_sv: Optional[float] = None
    pol1_pump_speed: Optional[int] = None
    pol1_press: Optional[float] = None
    pol2_temp_pv: Optional[float] = None
    pol2_temp_sv: Optional[float] = None
    pol2_pump_speed: Optional[int] = None
    pol2_press: Optional[float] = None
    hot_water_temp_pv: Optional[float] = None
    hot_water_temp_sv: Optional[float] = None

    class Config:
        from_attributes = True


class SensorDataRangeResponse(BaseModel):
    data: List[SensorDataResponse]
    total: int
    limit: int
    offset: int
