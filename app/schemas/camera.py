from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CameraCalibrationBase(BaseModel):
    camera_id: int
    angle_x: float = 0.0
    angle_y: float = 0.0
    angle_z: float = 0.0
    calibration_date: Optional[datetime] = None


class CameraCalibrationCreate(CameraCalibrationBase):
    pass


class CameraCalibrationUpdate(CameraCalibrationBase):
    camera_id: Optional[int] = None  # camera_id can be updated only if it's not unique


class CameraCalibrationResponse(CameraCalibrationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Equivalent to orm_mode = True in Pydantic v1
