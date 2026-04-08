from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Index, Integer

from app.models.base import Base


class CameraCalibration(Base):
    __tablename__ = "camera_calibration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(Integer, unique=True, nullable=False)
    angle_x = Column(Float, default=0)
    angle_y = Column(Float, default=0)
    angle_z = Column(Float, default=0)
    calibration_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_camera_id", camera_id),)

    def __repr__(self):
        return f"<CameraCalibration(id={self.id}, camera_id={self.camera_id})>"
