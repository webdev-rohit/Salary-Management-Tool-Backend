from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.employee_schema import EmployeeCreate, EmployeeResponse, EmployeeUpdate


def _valid_payload(**overrides):
    base = dict(
        full_name="John Doe",
        email="john.doe@example.com",
        job_title="Software Engineer",
        department="Engineering",
        country="India",
        salary=75000.00,
    )
    base.update(overrides)
    return base


def test_create_schema_accepts_valid_data():
    emp = EmployeeCreate(**_valid_payload())
    assert emp.full_name == "John Doe"
    assert emp.salary == 75000.00


def test_create_schema_rejects_negative_salary():
    with pytest.raises(ValidationError):
        EmployeeCreate(**_valid_payload(salary=-1000))


def test_create_schema_rejects_zero_salary():
    with pytest.raises(ValidationError):
        EmployeeCreate(**_valid_payload(salary=0))


def test_create_schema_rejects_empty_full_name():
    with pytest.raises(ValidationError):
        EmployeeCreate(**_valid_payload(full_name=""))


def test_create_schema_requires_all_mandatory_fields():
    with pytest.raises(ValidationError):
        EmployeeCreate(full_name="John Doe")


def test_update_schema_allows_partial_data():
    update = EmployeeUpdate(salary=90000)
    assert update.salary == 90000
    assert update.full_name is None
    assert update.country is None


def test_update_schema_rejects_negative_salary_if_provided():
    with pytest.raises(ValidationError):
        EmployeeUpdate(salary=-500)


def test_response_schema_includes_id_and_timestamps():
    now = datetime.now()
    response = EmployeeResponse(
        id=1,
        org_id=1,
        full_name="John Doe",
        email="john@example.com",
        job_title="Engineer",
        department="Engineering",
        country="India",
        salary=75000,
        created_at=now,
        updated_at=now,
    )
    assert response.id == 1
    assert response.created_at is not None
    assert response.updated_at is not None
