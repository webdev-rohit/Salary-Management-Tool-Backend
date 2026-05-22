import pytest

from app.repositories.employee_repository import (
    create_employee,
    delete_employee,
    get_all_employees,
    get_employee_by_id,
    update_employee,
)
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate


def _create_payload(**overrides):
    base = dict(
        full_name="Test User",
        email="test@example.com",
        job_title="Engineer",
        department="Engineering",
        country="India",
        salary=60000,
    )
    base.update(overrides)
    return EmployeeCreate(**base)


def test_create_employee_persists_and_returns_with_id(db_session, sample_org):
    data = _create_payload()
    emp = create_employee(db_session, sample_org.id, data)

    assert emp.id is not None
    assert isinstance(emp.id, int)
    assert emp.full_name == "Test User"
    assert emp.org_id == sample_org.id


def test_get_by_id_returns_correct_employee(db_session, sample_employee):
    result = get_employee_by_id(db_session, sample_employee.id)

    assert result is not None
    assert result.id == sample_employee.id
    assert result.full_name == sample_employee.full_name


def test_get_by_id_returns_none_for_missing_id(db_session):
    result = get_employee_by_id(db_session, 99999)

    assert result is None


def test_get_all_returns_list_scoped_to_org(db_session, sample_org, many_employees):
    results = get_all_employees(db_session, sample_org.id, skip=0, limit=100)

    assert len(results) == len(many_employees)
    assert all(emp.org_id == sample_org.id for emp in results)



def test_get_all_respects_skip_and_limit(db_session, sample_org, many_employees):
    results = get_all_employees(db_session, sample_org.id, skip=1, limit=2)

    assert len(results) == 2


def test_update_employee_changes_provided_fields(db_session, sample_employee):
    data = EmployeeUpdate(salary=99000)
    updated = update_employee(db_session, sample_employee, data)

    assert float(updated.salary) == 99000
    assert updated.full_name == sample_employee.full_name


def test_update_employee_ignores_unset_fields(db_session, sample_employee):
    original_title = sample_employee.job_title
    data = EmployeeUpdate(salary=80000)
    updated = update_employee(db_session, sample_employee, data)

    assert updated.job_title == original_title


def test_delete_employee_removes_row_from_db(db_session, sample_org):
    data = _create_payload(email="todelete@example.com")
    emp = create_employee(db_session, sample_org.id, data)
    emp_id = emp.id

    delete_employee(db_session, emp)

    assert get_employee_by_id(db_session, emp_id) is None
