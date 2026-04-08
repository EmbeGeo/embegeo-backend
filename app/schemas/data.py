from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DataLogCreate(BaseModel):
    ocr_text: str = Field(..., max_length=500)
    confidence_score: float
    image_path: str = Field(..., max_length=255)
    camera_id: int
    camera_angle_x: float
    camera_angle_y: float
    camera_angle_z: float
    frame_number: int
    frame_drop: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "ocr_text": "Example Text",
                "confidence_score": 0.98,
                "image_path": "/path/to/image.jpg",
                "camera_id": 1,
                "camera_angle_x": 0.5,
                "camera_angle_y": 0.2,
                "camera_angle_z": 0.0,
                "frame_number": 12345,
                "frame_drop": False,
                "timestamp": "2026-04-10T14:30:15Z",
            }
        }


class DataLogUpdate(BaseModel):
    ocr_text: Optional[str] = Field(None, max_length=500)
    confidence_score: Optional[float] = None
    image_path: Optional[str] = Field(None, max_length=255)
    camera_id: Optional[int] = None
    camera_angle_x: Optional[float] = None
    camera_angle_y: Optional[float] = None
    camera_angle_z: Optional[float] = None
    frame_number: Optional[int] = None
    frame_drop: Optional[bool] = None
    status: Optional[str] = None  # 'valid', 'invalid', 'pending'
    error_message: Optional[str] = None


class DataLogResponse(BaseModel):
    id: int
    timestamp: datetime
    ocr_text: str
    confidence_score: float
    image_path: str
    camera_id: int
    camera_angle_x: float
    camera_angle_y: float
    camera_angle_z: float
    frame_number: int
    frame_drop: bool
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Equivalent to orm_mode = True in Pydantic v1


class GroupedRecord(BaseModel):
    timestamp: datetime
    ocr_text: str
    confidence_score: float
    frame_drop: bool


class DataGroupedByMinute(BaseModel):
    minute: datetime
    records: List[GroupedRecord]
    frame_drop_count: int


class GroupedDataResponse(BaseModel):
    data: List[DataGroupedByMinute]
    total_records: int


class FrameDropStats(BaseModel):
    total_frames: int
    dropped_frames: int
    drop_rate: float
    stats_by_minute: List[dict]  # This could be a more specific schema if needed
