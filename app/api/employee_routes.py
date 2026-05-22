from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.employee_schema import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services import employee_service

router = APIRouter(prefix="/orgs/{org_id}/employees", tags=["employees"])


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(org_id: int, data: EmployeeCreate, db: Session = Depends(get_db)):
    return employee_service.create_employee(db, org_id, data)


@router.get("", response_model=list[EmployeeResponse])
def list_employees(org_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return employee_service.list_employees(db, org_id, skip=skip, limit=limit)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    return employee_service.get_employee(db, org_id, employee_id)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(org_id: int, employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db)):
    return employee_service.update_employee(db, org_id, employee_id, data)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    employee_service.delete_employee(db, org_id, employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
