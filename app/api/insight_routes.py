from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_org_id
from app.database.connection import get_db
from app.services import insight_service

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/country/{country}")
def country_stats(country: str, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return insight_service.get_country_stats(db, org_id, country)


@router.get("/job-title")
def avg_salary_by_title(title: str, country: str, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    avg = insight_service.get_avg_salary_by_title(db, org_id, title, country)
    return {"job_title": title, "country": country, "avg_salary": avg}


@router.get("/departments")
def dept_stats(db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return insight_service.get_dept_stats(db, org_id)


@router.get("/headcount")
def headcount_by_country(db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return insight_service.get_headcount_by_country(db, org_id)


@router.get("/top-earners")
def top_earners(n: int = 10, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    if n > 100:
        raise HTTPException(status_code=400, detail="n cannot exceed 100")
    return insight_service.get_top_earners(db, org_id, n)
