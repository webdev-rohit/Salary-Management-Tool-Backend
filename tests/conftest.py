import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import get_db
from app.models.base import Base
from app.models.organisations import Organisation
from app.models.employees import Employee


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_org(db_session):
    org = Organisation(
        org_name="Test Corp",
        org_address="1 Test Lane",
        currency="USD",
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def sample_employee(db_session, sample_org):
    emp = Employee(
        org_id=sample_org.id,
        full_name="Jane Doe",
        email="jane.doe@testcorp.com",
        job_title="Software Engineer",
        department="Engineering",
        country="India",
        salary=75000.00,
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def many_employees(db_session, sample_org):
    records = [
        Employee(org_id=sample_org.id, full_name="Alice Smith", email="alice@tc.com",
                 job_title="Data Analyst", department="Analytics", country="India", salary=60000),
        Employee(org_id=sample_org.id, full_name="Bob Jones", email="bob@tc.com",
                 job_title="Software Engineer", department="Engineering", country="USA", salary=90000),
        Employee(org_id=sample_org.id, full_name="Carol White", email="carol@tc.com",
                 job_title="HR Manager", department="HR", country="India", salary=55000),
        Employee(org_id=sample_org.id, full_name="David Brown", email="david@tc.com",
                 job_title="Software Engineer", department="Engineering", country="India", salary=80000),
        Employee(org_id=sample_org.id, full_name="Eve Davis", email="eve@tc.com",
                 job_title="Data Analyst", department="Analytics", country="USA", salary=70000),
    ]
    db_session.add_all(records)
    db_session.commit()
    for emp in records:
        db_session.refresh(emp)
    return records
