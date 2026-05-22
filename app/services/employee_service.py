from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.employees import Employee
from app.repositories import employee_repository as repo
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, org_id: int, data: EmployeeCreate) -> Employee:
    return repo.create_employee(db, org_id, data)


def get_employee(db: Session, org_id: int, employee_id: int) -> Employee:
    emp = repo.get_employee_by_id(db, employee_id)
    if emp is None or emp.org_id != org_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


def list_employees(db: Session, org_id: int, skip: int, limit: int) -> list[Employee]:
    return repo.get_all_employees(db, org_id, skip=skip, limit=limit)


def update_employee(db: Session, org_id: int, employee_id: int, data: EmployeeUpdate) -> Employee:
    emp = get_employee(db, org_id, employee_id)
    return repo.update_employee(db, emp, data)


def delete_employee(db: Session, org_id: int, employee_id: int) -> None:
    emp = get_employee(db, org_id, employee_id)
    repo.delete_employee(db, emp)
