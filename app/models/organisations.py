from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


def _now():
    return datetime.now(timezone.utc)


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True)
    org_name = Column(String(255), nullable=False)
    org_address = Column(Text, nullable=False)
    currency = Column(String(10), nullable=False)
    domain = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    employees = relationship("Employee", back_populates="organisation")
    users = relationship("User", back_populates="organisation")
