import math

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.employees import Employee
from app.core.config import settings
from app.repositories import employee_repository as repo
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate, PaginatedEmployeeResponse


def create_employee(db: Session, org_id: int, data: EmployeeCreate) -> Employee:
    return repo.create_employee(db, org_id, data)


def get_employee(db: Session, org_id: int, employee_id: int) -> Employee:
    emp = repo.get_employee_by_id(db, employee_id)
    if emp is None or emp.org_id != org_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


def list_employees(db: Session, org_id: int, page: int, page_size: int) -> PaginatedEmployeeResponse:
    if page_size > settings.page_size_max:
        raise HTTPException(status_code=400, detail=f"page_size cannot exceed {settings.page_size_max} per page")

    total = repo.count_employees(db, org_id)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    employees = repo.get_employees_page(db, org_id, offset=offset, page_size=page_size)
    return PaginatedEmployeeResponse(
        data=employees,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


def update_employee(db: Session, org_id: int, employee_id: int, data: EmployeeUpdate) -> Employee:
    emp = get_employee(db, org_id, employee_id)
    return repo.update_employee(db, emp, data)


def delete_employee(db: Session, org_id: int, employee_id: int) -> None:
    emp = get_employee(db, org_id, employee_id)
    repo.delete_employee(db, emp)
