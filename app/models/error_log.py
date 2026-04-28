from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Enum, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class ErrorLog(Base):
    __tablename__ = "ocr_errors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    logged_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="로그 시간")
    field = Column(String(50), nullable=False, comment="에러 발생 필드")
    raw_text = Column(String(100), nullable=True, comment="원본 텍스트")
    error_type = Column(
        Enum("PARSE_FAIL", "LOW_CONFIDENCE", "OUT_OF_RANGE", "ANOMALY"),
        nullable=False,
        comment="에러 유형",
    )
    error_detail = Column(String(255), nullable=True, comment="에러 상세")
    confidence = Column(Float, nullable=True, comment="신뢰도 점수")

    __table_args__ = (
        Index("idx_ocr_errors_logged_at", logged_at),
    )

    def __repr__(self):
        return f"<ErrorLog(id={self.id}, field='{self.field}', error_type='{self.error_type}')>"
