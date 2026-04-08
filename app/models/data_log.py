from datetime import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, Enum, Float,
                        ForeignKey, Index, Integer, String, Text)
from sqlalchemy.orm import relationship

from app.models.base import Base


class DataLog(Base):
    __tablename__ = "data_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ocr_text = Column(String(500))
    confidence_score = Column(Float)
    image_path = Column(String(255))
    camera_id = Column(Integer)
    camera_angle_x = Column(Float)
    camera_angle_y = Column(Float)
    camera_angle_z = Column(Float)
    frame_number = Column(Integer)
    frame_drop = Column(Boolean, default=False)
    status = Column(Enum("valid", "invalid", "pending"), default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    error_logs = relationship(
        "ErrorLog", back_populates="data_log", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_timestamp", timestamp),
        Index("idx_camera_id", camera_id),
        Index("idx_created_at", created_at),
        Index("idx_frame_drop", frame_drop),
        Index("idx_timestamp_camera", timestamp, camera_id),
    )

    def __repr__(self):
        return f"<DataLog(id={self.id}, timestamp='{self.timestamp}', camera_id={self.camera_id})>"
