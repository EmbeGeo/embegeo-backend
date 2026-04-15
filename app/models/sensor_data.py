from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, Index, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    iso_temp_pv = Column(Float, nullable=False, comment="ISO 원액온도(PV)")
    iso_temp_sv = Column(Float, nullable=False, comment="ISO 원액온도(SV)")
    iso_pump_speed = Column(Integer, nullable=False, comment="ISO 펌프속도(RPM)")
    iso_press = Column(Float, nullable=False, comment="ISO 압력(bar)")
    pol1_temp_pv = Column(Float, nullable=False, comment="POL1 원액온도(PV)")
    pol1_temp_sv = Column(Float, nullable=False, comment="POL1 원액온도(SV)")
    pol1_pump_speed = Column(Integer, nullable=False, comment="POL1 펌프속도")
    pol1_press = Column(Float, nullable=False, comment="POL1 압력")
    pol2_temp_pv = Column(Float, nullable=False, comment="POL2 원액온도(PV)")
    pol2_temp_sv = Column(Float, nullable=False, comment="POL2 원액온도(SV)")
    pol2_pump_speed = Column(Integer, nullable=False, comment="POL2 펌프속도")
    pol2_press = Column(Float, nullable=False, comment="POL2 압력")
    mix_motor_speed = Column(Integer, nullable=False, comment="믹싱 모터 속도")
    total_count = Column(Integer, nullable=False, comment="누적 생산량")
    error_count = Column(Integer, nullable=False, comment="불량 생산량")
    received_at = Column(DateTime, default=datetime.utcnow, comment="데이터 수신 시간")
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성 시간")
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="수정 시간",
    )

    error_logs = relationship(
        "ErrorLog", back_populates="sensor_data", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_timestamp", timestamp),
        Index("idx_received_at", received_at),
        Index("idx_created_at", created_at),
    )

    def __repr__(self):
        return f"<SensorData(id={self.id}, timestamp='{self.timestamp}')>"
