from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from app.services import employee_service

_REPO = "app.services.employee_service.repo"


def _mock_employee(id=1, org_id=1, full_name="Jane Doe"):
    emp = MagicMock()
    emp.id = id
    emp.org_id = org_id
    emp.full_name = full_name
    return emp


@pytest.fixture
def valid_create_data():
    return EmployeeCreate(
        full_name="John Doe",
        email="john@example.com",
        job_title="Engineer",
        department="Engineering",
        country="India",
        salary=60000,
    )


def test_create_employee_delegates_to_repository(valid_create_data):
    db = MagicMock()
    mock_emp = _mock_employee()

    with patch(f"{_REPO}.create_employee", return_value=mock_emp) as mock_create:
        result = employee_service.create_employee(db, org_id=1, data=valid_create_data)
        mock_create.assert_called_once_with(db, 1, valid_create_data)

    assert result == mock_emp


def test_get_employee_returns_employee_when_found():
    db = MagicMock()
    mock_emp = _mock_employee(id=1, org_id=1)

    with patch(f"{_REPO}.get_employee_by_id", return_value=mock_emp):
        result = employee_service.get_employee(db, org_id=1, employee_id=1)

    assert result == mock_emp


def test_get_employee_raises_404_when_not_found():
    db = MagicMock()

    with patch(f"{_REPO}.get_employee_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            employee_service.get_employee(db, org_id=1, employee_id=999)

    assert exc_info.value.status_code == 404


def test_get_employee_raises_404_for_wrong_org():
    db = MagicMock()
    mock_emp = _mock_employee(id=1, org_id=2)

    with patch(f"{_REPO}.get_employee_by_id", return_value=mock_emp):
        with pytest.raises(HTTPException) as exc_info:
            employee_service.get_employee(db, org_id=1, employee_id=1)

    assert exc_info.value.status_code == 404


def test_update_employee_raises_404_when_not_found():
    db = MagicMock()

    with patch(f"{_REPO}.get_employee_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            employee_service.update_employee(db, org_id=1, employee_id=999, data=EmployeeUpdate(salary=90000))

    assert exc_info.value.status_code == 404


def test_update_employee_calls_repo_update_when_found():
    db = MagicMock()
    mock_emp = _mock_employee(id=1, org_id=1)
    updated_emp = _mock_employee(id=1, org_id=1)
    data = EmployeeUpdate(salary=90000)

    with patch(f"{_REPO}.get_employee_by_id", return_value=mock_emp):
        with patch(f"{_REPO}.update_employee", return_value=updated_emp) as mock_update:
            result = employee_service.update_employee(db, org_id=1, employee_id=1, data=data)
            mock_update.assert_called_once_with(db, mock_emp, data)

    assert result == updated_emp


def test_delete_employee_raises_404_when_not_found():
    db = MagicMock()

    with patch(f"{_REPO}.get_employee_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            employee_service.delete_employee(db, org_id=1, employee_id=999)

    assert exc_info.value.status_code == 404


def test_delete_employee_calls_repo_delete_when_found():
    db = MagicMock()
    mock_emp = _mock_employee(id=1, org_id=1)

    with patch(f"{_REPO}.get_employee_by_id", return_value=mock_emp):
        with patch(f"{_REPO}.delete_employee") as mock_delete:
            employee_service.delete_employee(db, org_id=1, employee_id=1)
            mock_delete.assert_called_once_with(db, mock_emp)


def test_list_employees_passes_pagination_to_repo():
    db = MagicMock()
    mock_list = [_mock_employee(id=i) for i in range(3)]

    with patch(f"{_REPO}.get_all_employees", return_value=mock_list) as mock_get_all:
        result = employee_service.list_employees(db, org_id=1, skip=5, limit=3)
        mock_get_all.assert_called_once_with(db, 1, skip=5, limit=3)

    assert result == mock_list
