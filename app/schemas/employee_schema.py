from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class EmployeeCreate(BaseModel):
    full_name: str
    email: str
    job_title: str
    department: str
    country: str
    salary: float

    @field_validator("full_name")
    @classmethod
    def full_name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("full_name must not be empty")
        return v

    @field_validator("salary")
    @classmethod
    def salary_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("salary must be greater than zero")
        return v


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    country: Optional[str] = None
    salary: Optional[float] = None

    @field_validator("salary")
    @classmethod
    def salary_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("salary must be greater than zero")
        return v


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    full_name: str
    email: str
    job_title: str
    department: str
    country: str
    salary: str
    created_at: datetime
    updated_at: datetime


class PaginatedEmployeeResponse(BaseModel):
    data: list[EmployeeResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
