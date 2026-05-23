from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.employees import Employee
from app.models.organisations import Organisation


def get_org_currency(db: Session, org_id: int) -> Optional[str]:
    return db.query(Organisation.currency).filter(Organisation.id == org_id).scalar()


def get_country_stats(db: Session, org_id: int, country: str):
    return (
        db.query(
            func.min(Employee.salary).label("min_salary"),
            func.max(Employee.salary).label("max_salary"),
            func.avg(Employee.salary).label("avg_salary"),
            func.count(Employee.id).label("count"),
        )
        .filter(Employee.org_id == org_id, Employee.country == country)
        .one()
    )


def get_avg_salary_by_title(db: Session, org_id: int, job_title: str, country: str):
    return (
        db.query(func.avg(Employee.salary).label("avg_salary"))
        .filter(
            Employee.org_id == org_id,
            Employee.job_title == job_title,
            Employee.country == country,
        )
        .one()
    )


def get_dept_stats(db: Session, org_id: int):
    return (
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


def get_headcount_by_country(db: Session, org_id: int):
    return (
        db.query(Employee.country, func.count(Employee.id).label("count"))
        .filter(Employee.org_id == org_id)
        .group_by(Employee.country)
        .all()
    )


def get_top_earners(db: Session, org_id: int, n: int) -> list[Employee]:
    return (
        db.query(Employee)
        .filter(Employee.org_id == org_id)
        .order_by(Employee.salary.desc())
        .limit(n)
        .all()
    )
