from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, Index, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class SensorData(Base):
    __tablename__ = "gauge_readings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    recorded_at = Column(DateTime, nullable=False, comment="측정 시간")
    ai_recognized_at = Column(
        DateTime, default=datetime.utcnow, comment="AI 처리 시간"
    )

    # ISO 원액
    iso_temp_pv = Column(Float, nullable=True, comment="ISO 원액온도(PV)")
    iso_temp_sv = Column(Float, nullable=True, comment="ISO 원액온도(SV)")
    iso_pump_speed = Column(Integer, nullable=True, comment="ISO 펌프속도(RPM)")
    iso_press = Column(Float, nullable=True, comment="ISO 압력(bar)")

    # POL1 원액
    pol1_temp_pv = Column(Float, nullable=True, comment="POL1 원액온도(PV)")
    pol1_temp_sv = Column(Float, nullable=True, comment="POL1 원액온도(SV)")
    pol1_pump_speed = Column(Integer, nullable=True, comment="POL1 펌프속도")
    pol1_press = Column(Float, nullable=True, comment="POL1 압력")

    # POL2 원액
    pol2_temp_pv = Column(Float, nullable=True, comment="POL2 원액온도(PV)")
    pol2_temp_sv = Column(Float, nullable=True, comment="POL2 원액온도(SV)")
    pol2_pump_speed = Column(Integer, nullable=True, comment="POL2 펌프속도")
    pol2_press = Column(Float, nullable=True, comment="POL2 압력")

    # 온수
    hot_water_temp_pv = Column(Float, nullable=True, comment="온수 온도(PV)")
    hot_water_temp_sv = Column(Float, nullable=True, comment="온수 온도(SV)")

    __table_args__ = (
        Index("idx_recorded_at", recorded_at.desc()),
    )

    def __repr__(self):
        return f"<SensorData(id={self.id}, recorded_at='{self.recorded_at}')>"
