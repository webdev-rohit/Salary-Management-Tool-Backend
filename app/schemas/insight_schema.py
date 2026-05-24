from datetime import datetime
from pydantic import BaseModel


class OrgSalaryRangeResponse(BaseModel):
    min_salary: str
    max_salary: str
    currency: str


class CountryStatsResponse(BaseModel):
    country: str
    min_salary: str
    max_salary: str
    avg_salary: str
    count: int


class AvgSalaryByTitleResponse(BaseModel):
    job_title: str
    country: str
    avg_salary: str


class DeptStatsResponse(BaseModel):
    department: str
    min_salary: str
    max_salary: str
    avg_salary: str
    count: int


class HeadcountResponse(BaseModel):
    country: str
    count: int


class TopEarnerResponse(BaseModel):
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
