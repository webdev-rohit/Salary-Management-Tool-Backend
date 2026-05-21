import pytest


def _employee_payload(**overrides):
    base = dict(
        full_name="New Employee",
        email="new@testcorp.com",
        job_title="Analyst",
        department="Analytics",
        country="India",
        salary=50000,
    )
    base.update(overrides)
    return base


# --- CREATE ---

def test_create_employee_returns_201_with_id(client, sample_org):
    response = client.post(
        f"/orgs/{sample_org.id}/employees",
        json=_employee_payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["full_name"] == "New Employee"
    assert body["org_id"] == sample_org.id


def test_create_employee_missing_required_field_returns_422(client, sample_org):
    response = client.post(
        f"/orgs/{sample_org.id}/employees",
        json={"full_name": "Incomplete"},
    )

    assert response.status_code == 422


def test_create_employee_negative_salary_returns_422(client, sample_org):
    response = client.post(
        f"/orgs/{sample_org.id}/employees",
        json=_employee_payload(salary=-1000),
    )

    assert response.status_code == 422


# --- LIST ---

def test_list_employees_returns_200_with_items(client, sample_org, many_employees):
    response = client.get(f"/orgs/{sample_org.id}/employees")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == len(many_employees)


def test_list_employees_pagination_skip_and_limit(client, sample_org, many_employees):
    response = client.get(f"/orgs/{sample_org.id}/employees?skip=0&limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_employees_skip_reduces_results(client, sample_org, many_employees):
    response = client.get(f"/orgs/{sample_org.id}/employees?skip=2&limit=100")

    assert len(response.json()) == len(many_employees) - 2


# --- GET SINGLE ---

def test_get_employee_by_id_returns_correct_data(client, sample_org, sample_employee):
    response = client.get(f"/orgs/{sample_org.id}/employees/{sample_employee.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == sample_employee.id
    assert body["full_name"] == sample_employee.full_name


def test_get_employee_unknown_id_returns_404(client, sample_org):
    response = client.get(f"/orgs/{sample_org.id}/employees/99999")

    assert response.status_code == 404


def test_get_employee_wrong_org_returns_404(client, sample_org, sample_employee):
    response = client.get(f"/orgs/99999/employees/{sample_employee.id}")

    assert response.status_code == 404


# --- UPDATE ---

def test_update_employee_returns_200_with_updated_values(client, sample_org, sample_employee):
    response = client.put(
        f"/orgs/{sample_org.id}/employees/{sample_employee.id}",
        json={"salary": 99000},
    )

    assert response.status_code == 200
    assert float(response.json()["salary"]) == 99000


def test_update_employee_unknown_id_returns_404(client, sample_org):
    response = client.put(
        f"/orgs/{sample_org.id}/employees/99999",
        json={"salary": 99000},
    )

    assert response.status_code == 404


# --- DELETE ---

def test_delete_employee_returns_204_no_body(client, sample_org, sample_employee):
    response = client.delete(f"/orgs/{sample_org.id}/employees/{sample_employee.id}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_employee_unknown_id_returns_404(client, sample_org):
    response = client.delete(f"/orgs/{sample_org.id}/employees/99999")

    assert response.status_code == 404


