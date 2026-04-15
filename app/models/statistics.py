from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, Index, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stat_date = Column(Date, nullable=False, comment="통계 날짜")
    total_count = Column(Integer, nullable=False, comment="일일 총 생산량")
    error_count = Column(Integer, nullable=False, comment="일일 불량량")
    avg_iso_temp_pv = Column(Float, nullable=True, comment="평균 ISO 온도(PV)")
    avg_pol1_temp_pv = Column(Float, nullable=True, comment="평균 POL1 온도(PV)")
    avg_pol2_temp_pv = Column(Float, nullable=True, comment="평균 POL2 온도(PV)")
    max_iso_press = Column(Float, nullable=True, comment="최고 ISO 압력")
    min_iso_press = Column(Float, nullable=True, comment="최저 ISO 압력")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_stat_date", stat_date),
        UniqueConstraint("stat_date", name="unique_date"),
    )

    def __repr__(self):
        return f"<Statistics(id={self.id}, stat_date='{self.stat_date}')>"
