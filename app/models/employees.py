from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


def _now():
    return datetime.now(timezone.utc)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organisations.id"), nullable=False)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False)
    job_title = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    salary = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    organisation = relationship("Organisation", back_populates="employees")
