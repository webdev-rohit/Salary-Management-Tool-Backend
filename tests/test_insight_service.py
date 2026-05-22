import pytest
from fastapi import HTTPException

from app.services.insight_service import (
    get_avg_salary_by_title,
    get_country_stats,
    get_dept_stats,
    get_headcount_by_country,
    get_top_earners,
)


# many_employees fixture (from conftest) has:
#   India: Alice (Analyst, 60k), Carol (HR Mgr, 55k), David (SWE, 80k)  → min=55k, max=80k, avg=65k
#   USA:   Bob (SWE, 90k), Eve (Analyst, 70k)


def test_country_stats_returns_correct_min_max_avg(db_session, sample_org, many_employees):
    stats = get_country_stats(db_session, sample_org.id, "India")

    assert float(stats["min_salary"]) == 55000
    assert float(stats["max_salary"]) == 80000
    assert float(stats["avg_salary"]) == pytest.approx(65000, rel=1e-2)
    assert stats["count"] == 3


def test_country_stats_raises_404_for_unknown_country(db_session, sample_org, many_employees):
    with pytest.raises(HTTPException) as exc_info:
        get_country_stats(db_session, sample_org.id, "Narnia")

    assert exc_info.value.status_code == 404


def test_avg_salary_by_job_title_and_country_returns_correct_value(db_session, sample_org, many_employees):
    # India Software Engineers: David (80k) → avg = 80k
    avg = get_avg_salary_by_title(db_session, sample_org.id, "Software Engineer", "India")

    assert float(avg) == pytest.approx(80000, rel=1e-2)


def test_avg_salary_raises_404_when_no_match(db_session, sample_org, many_employees):
    with pytest.raises(HTTPException) as exc_info:
        get_avg_salary_by_title(db_session, sample_org.id, "Ghost Role", "Nowhere")

    assert exc_info.value.status_code == 404


def test_dept_stats_returns_entry_for_each_department(db_session, sample_org, many_employees):
    results = get_dept_stats(db_session, sample_org.id)
    dept_names = {r["department"] for r in results}

    assert "Engineering" in dept_names
    assert "Analytics" in dept_names
    assert "HR" in dept_names


def test_dept_stats_values_are_correct_for_engineering(db_session, sample_org, many_employees):
    # Engineering: Bob (USA, 90k) + David (India, 80k) → min=80k, max=90k, avg=85k, count=2
    results = get_dept_stats(db_session, sample_org.id)
    eng = next(r for r in results if r["department"] == "Engineering")

    assert float(eng["min_salary"]) == 80000
    assert float(eng["max_salary"]) == 90000
    assert float(eng["avg_salary"]) == pytest.approx(85000, rel=1e-2)
    assert eng["count"] == 2


def test_headcount_by_country_returns_correct_counts(db_session, sample_org, many_employees):
    results = get_headcount_by_country(db_session, sample_org.id)
    counts = {r["country"]: r["count"] for r in results}

    assert counts["India"] == 3
    assert counts["USA"] == 2


def test_top_earners_returns_n_employees_sorted_descending(db_session, sample_org, many_employees):
    results = get_top_earners(db_session, sample_org.id, n=3)

    assert len(results) == 3
    salaries = [float(emp.salary) for emp in results]
    assert salaries == sorted(salaries, reverse=True)


