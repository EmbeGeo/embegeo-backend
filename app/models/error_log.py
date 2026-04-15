from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sensor_data_id = Column(
        BigInteger,
        ForeignKey("sensor_data.id", ondelete="CASCADE"),
        nullable=True,
        comment="센서 데이터 ID (FK)",
    )
    error_type = Column(String(100), comment="에러 타입")
    error_message = Column(Text, comment="에러 메시지")
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성 시간")

    sensor_data = relationship("SensorData", back_populates="error_logs")

    __table_args__ = (
        Index("idx_sensor_data_id", sensor_data_id),
        Index("idx_error_log_created_at", created_at),
    )

    def __repr__(self):
        return f"<ErrorLog(id={self.id}, sensor_data_id={self.sensor_data_id}, error_type='{self.error_type}')>"
