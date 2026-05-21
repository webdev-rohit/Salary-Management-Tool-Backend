import pytest


# many_employees (from conftest):
#   India: Alice (Analyst, 60k), Carol (HR Mgr, 55k), David (SWE, 80k)
#   USA:   Bob (SWE, 90k), Eve (Analyst, 70k)


# --- COUNTRY STATS ---

def test_country_stats_values_are_correct(client, sample_org, many_employees):
    response = client.get(f"/orgs/{sample_org.id}/insights/country/India")

    body = response.json()
    assert float(body["min_salary"]) == 55000
    assert float(body["max_salary"]) == 80000
    assert body["count"] == 3


def test_country_stats_unknown_country_returns_404(client, sample_org, many_employees):
    response = client.get(f"/orgs/{sample_org.id}/insights/country/Narnia")

    assert response.status_code == 404


# --- AVG SALARY BY JOB TITLE ---

def test_avg_salary_by_title_returns_200_with_value(client, sample_org, many_employees):
    response = client.get(
        f"/orgs/{sample_org.id}/insights/job-title",
        params={"title": "Software Engineer", "country": "India"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "avg_salary" in body
    assert float(body["avg_salary"]) == pytest.approx(80000, rel=1e-2)


def test_avg_salary_by_title_no_match_returns_404(client, sample_org, many_employees):
    response = client.get(
        f"/orgs/{sample_org.id}/insights/job-title",
        params={"title": "Ghost Role", "country": "Nowhere"},
    )

    assert response.status_code == 404


# --- DEPARTMENT BREAKDOWN ---

def test_department_breakdown_returns_list_with_required_fields(client, sample_org, many_employees):
    response = client.get(f"/orgs/{sample_org.id}/insights/departments")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list) and len(body) > 0
    first = body[0]
    assert "department" in first
    assert "min_salary" in first
    assert "max_salary" in first
    assert "avg_salary" in first
    assert "count" in first


# --- HEADCOUNT BY COUNTRY ---

def test_headcount_by_country_values_are_correct(client, sample_org, many_employees):
    response = client.get(f"/orgs/{sample_org.id}/insights/headcount")
    counts = {entry["country"]: entry["count"] for entry in response.json()}

    assert counts["India"] == 3
    assert counts["USA"] == 2


# --- TOP EARNERS ---

def test_top_earners_returns_200_with_list(client, sample_org, many_employees):
    response = client.get(f"/orgs/{sample_org.id}/insights/top-earners?n=3")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 3


def test_top_earners_are_sorted_descending(client, sample_org, many_employees):
    response = client.get(f"/orgs/{sample_org.id}/insights/top-earners?n=5")
    salaries = [float(emp["salary"]) for emp in response.json()]

    assert salaries == sorted(salaries, reverse=True)


