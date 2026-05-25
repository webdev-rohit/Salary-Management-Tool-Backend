from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_org_id
from app.database.connection import get_db
from app.schemas.insight_schema import (
    AvgSalaryByTitleResponse,
    CountryStatsResponse,
    DeptStatsResponse,
    HeadcountResponse,
    OrgSalaryRangeResponse,
    TopEarnerResponse,
)
from app.services import insight_service

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/salary-range", response_model=OrgSalaryRangeResponse)
def org_salary_range(db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return insight_service.get_org_salary_range(db, org_id)


@router.get("/country/{country}", response_model=CountryStatsResponse)
def country_stats(country: str, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return insight_service.get_country_stats(db, org_id, country)


@router.get("/job-title", response_model=AvgSalaryByTitleResponse)
def avg_salary_by_title(title: str, country: str, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    avg = insight_service.get_avg_salary_by_title(db, org_id, title, country)
    return AvgSalaryByTitleResponse(job_title=title, country=country, avg_salary=avg)


@router.get("/departments", response_model=list[DeptStatsResponse])
def dept_stats(db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return insight_service.get_dept_stats(db, org_id)


@router.get("/headcount", response_model=list[HeadcountResponse])
def headcount_by_country(db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return insight_service.get_headcount_by_country(db, org_id)


@router.get("/top-earners", response_model=list[TopEarnerResponse])
def top_earners(n: int = 10, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    if n > 100:
        raise HTTPException(status_code=400, detail="n cannot exceed 100")
    return insight_service.get_top_earners(db, org_id, n)
