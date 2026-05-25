from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import insight_repository as repo


def _get_currency(db: Session, org_id: int) -> str:
    currency = repo.get_org_currency(db, org_id)
    if currency is None:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return currency


def _fmt(amount, currency: str) -> str:
    return f"{float(amount):.2f} {currency}"


def get_country_stats(db: Session, org_id: int, country: str) -> dict:
    currency = _get_currency(db, org_id)
    row = repo.get_country_stats(db, org_id, country)
    if row.count == 0:
        raise HTTPException(status_code=404, detail=f"No employees found in country '{country}'")
    return {
        "country": country,
        "min_salary": _fmt(row.min_salary, currency),
        "max_salary": _fmt(row.max_salary, currency),
        "avg_salary": _fmt(row.avg_salary, currency),
        "count": row.count,
    }


def get_avg_salary_by_title(db: Session, org_id: int, job_title: str, country: str) -> str:
    currency = _get_currency(db, org_id)
    row = repo.get_avg_salary_by_title(db, org_id, job_title, country)
    if row.avg_salary is None:
        raise HTTPException(
            status_code=404,
            detail=f"No employees found for job title '{job_title}' in '{country}'",
        )
    return _fmt(row.avg_salary, currency)


def get_dept_stats(db: Session, org_id: int) -> list[dict]:
    currency = _get_currency(db, org_id)
    rows = repo.get_dept_stats(db, org_id)
    return [
        {
            "department": r.department,
            "min_salary": _fmt(r.min_salary, currency),
            "max_salary": _fmt(r.max_salary, currency),
            "avg_salary": _fmt(r.avg_salary, currency),
            "count": r.count,
        }
        for r in rows
    ]


def get_org_salary_range(db: Session, org_id: int) -> dict:
    currency = _get_currency(db, org_id)
    row = repo.get_org_salary_range(db, org_id)
    if row.min_salary is None:
        raise HTTPException(status_code=404, detail="No employees found in this organisation")
    return {
        "min_salary": _fmt(row.min_salary, currency),
        "max_salary": _fmt(row.max_salary, currency),
        "currency": currency,
    }


def get_headcount_by_country(db: Session, org_id: int) -> list[dict]:
    rows = repo.get_headcount_by_country(db, org_id)
    return [{"country": r.country, "count": r.count} for r in rows]


def get_top_earners(db: Session, org_id: int, n: int) -> list[dict]:
    currency = _get_currency(db, org_id)
    employees = repo.get_top_earners(db, org_id, n)
    return [
        {
            "id": e.id,
            "org_id": e.org_id,
            "full_name": e.full_name,
            "email": e.email,
            "job_title": e.job_title,
            "department": e.department,
            "country": e.country,
            "salary": _fmt(e.salary, currency),
            "created_at": e.created_at,
            "updated_at": e.updated_at,
        }
        for e in employees
    ]
