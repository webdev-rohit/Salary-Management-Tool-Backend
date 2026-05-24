import math

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.employees import Employee
from app.models.organisations import Organisation
from app.core.config import settings
from app.repositories import employee_repository as repo
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate, PaginatedEmployeeResponse


def _get_org_or_404(db: Session, org_id: int) -> Organisation:
    org = db.get(Organisation, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return org


def _validate_email_domain(email: str, org: Organisation) -> None:
    domain = email.split("@")[-1]
    if domain != org.domain:
        raise HTTPException(
            status_code=400,
            detail=f"Employee email must use the organisation domain '@{org.domain}'"
        )


def _check_duplicate_email(db: Session, org_id: int, email: str, exclude_employee_id: int | None = None) -> None:
    existing = repo.get_employee_by_email(db, org_id, email)
    if existing and existing.id != exclude_employee_id:
        raise HTTPException(status_code=409, detail=f"An employee with email '{email}' already exists in this organisation")


def _to_response(emp: Employee, currency: str) -> dict:
    return {
        "id": emp.id,
        "org_id": emp.org_id,
        "full_name": emp.full_name,
        "email": emp.email,
        "job_title": emp.job_title,
        "department": emp.department,
        "country": emp.country,
        "salary": f"{float(emp.salary):.2f} {currency}",
        "created_at": emp.created_at,
        "updated_at": emp.updated_at,
    }


def create_employee(db: Session, org_id: int, data: EmployeeCreate) -> dict:
    org = _get_org_or_404(db, org_id)
    _validate_email_domain(data.email, org)
    _check_duplicate_email(db, org_id, data.email)
    emp = repo.create_employee(db, org_id, data)
    return _to_response(emp, org.currency)


def get_employee(db: Session, org_id: int, employee_id: int) -> dict:
    emp = repo.get_employee_by_id(db, employee_id)
    if emp is None or emp.org_id != org_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _to_response(emp, emp.organisation.currency)


def list_employees(db: Session, org_id: int, page: int, page_size: int) -> PaginatedEmployeeResponse:
    if page_size > settings.page_size_max:
        raise HTTPException(status_code=400, detail=f"page_size cannot exceed {settings.page_size_max} per page")

    org = _get_org_or_404(db, org_id)
    total = repo.count_employees(db, org_id)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    employees = repo.get_employees_page(db, org_id, offset=offset, page_size=page_size)
    return PaginatedEmployeeResponse(
        data=[_to_response(e, org.currency) for e in employees],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


def update_employee(db: Session, org_id: int, employee_id: int, data: EmployeeUpdate) -> dict:
    emp = repo.get_employee_by_id(db, employee_id)
    if emp is None or emp.org_id != org_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    if data.email is not None:
        org = _get_org_or_404(db, org_id)
        _validate_email_domain(data.email, org)
        _check_duplicate_email(db, org_id, data.email, exclude_employee_id=emp.id)
    emp = repo.update_employee(db, emp, data)
    return _to_response(emp, emp.organisation.currency)


def delete_employee(db: Session, org_id: int, employee_id: int) -> None:
    emp = repo.get_employee_by_id(db, employee_id)
    if emp is None or emp.org_id != org_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    repo.delete_employee(db, emp)
