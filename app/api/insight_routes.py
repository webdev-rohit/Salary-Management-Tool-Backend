from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services import insight_service

router = APIRouter(prefix="/orgs/{org_id}/insights", tags=["insights"])


@router.get("/country/{country}")
def country_stats(org_id: int, country: str, db: Session = Depends(get_db)):
    return insight_service.get_country_stats(db, org_id, country)


@router.get("/job-title")
def avg_salary_by_title(org_id: int, title: str, country: str, db: Session = Depends(get_db)):
    avg = insight_service.get_avg_salary_by_title(db, org_id, title, country)
    return {"job_title": title, "country": country, "avg_salary": avg}


@router.get("/departments")
def dept_stats(org_id: int, db: Session = Depends(get_db)):
    return insight_service.get_dept_stats(db, org_id)


@router.get("/headcount")
def headcount_by_country(org_id: int, db: Session = Depends(get_db)):
    return insight_service.get_headcount_by_country(db, org_id)


@router.get("/top-earners")
def top_earners(org_id: int, n: int = 10, db: Session = Depends(get_db)):
    if n > 100:
        raise HTTPException(status_code=400, detail="n cannot exceed 100")
    data = insight_service.get_top_earners(db, org_id, n)
    return data
