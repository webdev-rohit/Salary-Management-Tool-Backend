from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.employees import Employee
from app.models.organisations import Organisation


def _get_currency(db: Session, org_id: int) -> str:
    currency = db.query(Organisation.currency).filter(Organisation.id == org_id).scalar()
    if currency is None:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return currency


def _fmt(amount, currency: str) -> str:
    return f"{float(amount):.2f} {currency}"


def get_country_stats(db: Session, org_id: int, country: str) -> dict:
    currency = _get_currency(db, org_id)
    row = (
        db.query(
            func.min(Employee.salary).label("min_salary"),
            func.max(Employee.salary).label("max_salary"),
            func.avg(Employee.salary).label("avg_salary"),
            func.count(Employee.id).label("count"),
        )
        .filter(Employee.org_id == org_id, Employee.country == country)
        .one()
    )
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
    row = (
        db.query(func.avg(Employee.salary).label("avg_salary"))
        .filter(
            Employee.org_id == org_id,
            Employee.job_title == job_title,
            Employee.country == country,
        )
        .one()
    )
    if row.avg_salary is None:
        raise HTTPException(
            status_code=404,
            detail=f"No employees found for job title '{job_title}' in '{country}'",
        )
    return _fmt(row.avg_salary, currency)


def get_dept_stats(db: Session, org_id: int) -> list[dict]:
    currency = _get_currency(db, org_id)
    rows = (
        db.query(
            Employee.department,
            func.min(Employee.salary).label("min_salary"),
            func.max(Employee.salary).label("max_salary"),
            func.avg(Employee.salary).label("avg_salary"),
            func.count(Employee.id).label("count"),
        )
        .filter(Employee.org_id == org_id)
        .group_by(Employee.department)
        .all()
    )
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


def get_headcount_by_country(db: Session, org_id: int) -> list[dict]:
    rows = (
        db.query(Employee.country, func.count(Employee.id).label("count"))
        .filter(Employee.org_id == org_id)
        .group_by(Employee.country)
        .all()
    )
    return [{"country": r.country, "count": r.count} for r in rows]


def get_top_earners(db: Session, org_id: int, n: int) -> list[dict]:
    currency = _get_currency(db, org_id)
    employees = (
        db.query(Employee)
        .filter(Employee.org_id == org_id)
        .order_by(Employee.salary.desc())
        .limit(n)
        .all()
    )
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
