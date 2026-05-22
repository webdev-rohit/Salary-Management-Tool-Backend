from typing import Optional

from sqlalchemy.orm import Session

from app.models.employees import Employee
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, org_id: int, data: EmployeeCreate) -> Employee:
    emp = Employee(org_id=org_id, **data.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def get_employee_by_id(db: Session, employee_id: int) -> Optional[Employee]:
    return db.get(Employee, employee_id)


def get_all_employees(db: Session, org_id: int, skip: int, limit: int) -> list[Employee]:
    return (
        db.query(Employee)
        .filter(Employee.org_id == org_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_employee(db: Session, employee: Employee, data: EmployeeUpdate) -> Employee:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: Employee) -> None:
    db.delete(employee)
    db.commit()
