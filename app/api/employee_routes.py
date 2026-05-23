from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_org_id
from app.database.connection import get_db
from app.schemas.employee_schema import EmployeeCreate, EmployeeResponse, EmployeeUpdate, PaginatedEmployeeResponse
from app.services import employee_service

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return employee_service.create_employee(db, org_id, data)


@router.get("", response_model=PaginatedEmployeeResponse)
def list_employees(page: int = 1, page_size: int = 50, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return employee_service.list_employees(db, org_id, page=page, page_size=page_size)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return employee_service.get_employee(db, org_id, employee_id)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    return employee_service.update_employee(db, org_id, employee_id, data)


@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
def delete_employee(employee_id: int, db: Session = Depends(get_db), org_id: int = Depends(get_current_org_id)):
    employee_service.delete_employee(db, org_id, employee_id)
    return {"message": "This employee has been removed from the Employee Database"}
