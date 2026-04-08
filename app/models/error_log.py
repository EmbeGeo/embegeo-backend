from datetime import datetime

from sqlalchemy import (BigInteger, Column, DateTime, ForeignKey, Index,
                        Integer, String, Text)
from sqlalchemy.orm import relationship

from app.models.base import Base


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    data_id = Column(
        BigInteger, ForeignKey("data_logs.id", ondelete="CASCADE"), nullable=False
    )
    error_type = Column(String(100))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    data_log = relationship("DataLog", back_populates="error_logs")

    __table_args__ = (Index("idx_data_id", data_id),)

    def __repr__(self):
        return f"<ErrorLog(id={self.id}, data_id={self.data_id}, error_type='{self.error_type}')>"
