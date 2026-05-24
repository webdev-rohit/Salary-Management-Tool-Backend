# Salary Management Tool — Backend

A multi-tenant REST API for managing employee salary data, built with **FastAPI** and **PostgreSQL**.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Server | Uvicorn (ASGI) |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL (Neon serverless) |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt |
| Validation | Pydantic v2 |
| Testing | pytest + httpx |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, router registration, startup
│   ├── api/                     # Route handlers (controllers)
│   │   ├── auth_routes.py
│   │   ├── employee_routes.py
│   │   └── insight_routes.py
│   ├── core/                    # Cross-cutting concerns
│   │   ├── config.py            # Settings loaded from .env via pydantic-settings
│   │   ├── dependencies.py      # FastAPI dependency injection (auth guard)
│   │   └── security.py          # JWT creation/validation, bcrypt helpers
│   ├── database/
│   │   ├── connection.py        # SQLAlchemy engine + session factory
│   │   └── init_db.py           # create_all() called on startup
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── organisations.py
│   │   ├── users.py
│   │   └── employees.py
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── auth_schema.py
│   │   ├── employee_schema.py
│   │   └── insight_schema.py
│   ├── services/                # Business logic
│   │   ├── auth_service.py
│   │   ├── employee_service.py
│   │   └── insight_service.py
│   └── repositories/            # Database queries (data access layer)
│       ├── auth_repository.py
│       ├── employee_repository.py
│       └── insight_repository.py
├── alembic/                     # Database migration scripts
│   └── versions/
├── scripts/                     # DB seeding utilities
│   ├── seed_user.py
│   └── seed_employees.py
├── tests/                       # pytest test suite
│   ├── conftest.py
│   ├── test_employee_routes.py
│   ├── test_employee_repository.py
│   ├── test_employee_service.py
│   ├── test_insight_routes.py
│   ├── test_insight_service.py
│   └── test_schemas.py
├── .env.example
└── pyproject.toml
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL database (or a [Neon](https://neon.tech) serverless connection string)
- `uv` or `pip` for dependency management

### Installation

```bash
# Clone the repo and navigate to the backend
cd backend

# Install dependencies
pip install -e ".[dev]"
# or with uv:
uv sync
```

### Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | Long random string for JWT signing | `openssl rand -hex 32` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_VALID_TIME` | Token lifetime in minutes | `60` |
| `PAGE_SIZE_MAX` | Maximum employees per page | `100` |

### Database Setup

```bash
# Run Alembic migrations
alembic upgrade head
```

Tables are also auto-created on app startup via `init_db()`, but Alembic is the source of truth for schema changes.

### Seed Data

```bash
# Create an organisation and user interactively
python scripts/seed_user.py

# Bulk-seed employees
python scripts/seed_employees.py
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive docs: `http://127.0.0.1:8000/docs`

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login with email/password, returns a JWT bearer token |

**Request body:**
```json
{ "email": "user@example.com", "password": "secret" }
```

**Response:**
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

All other endpoints require the header:
```
Authorization: Bearer <access_token>
```

---

### Employees

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/employees` | Create a new employee |
| GET | `/employees` | List employees (paginated: `?page=1&page_size=20`) |
| GET | `/employees/{id}` | Get a single employee |
| PUT | `/employees/{id}` | Update employee fields (partial updates supported) |
| DELETE | `/employees/{id}` | Delete an employee |

**Employee fields:** `full_name`, `email`, `job_title`, `department`, `country`, `salary`

Employees are scoped to the authenticated user's organisation — cross-org access is not possible.

---

### Insights (Analytics)

| Method | Endpoint | Query Params | Description |
|--------|----------|--------------|-------------|
| GET | `/insights/country/{country}` | — | Min/max/avg salary + headcount for a country |
| GET | `/insights/job-title` | `title`, `country` | Average salary for a job title, optionally filtered by country |
| GET | `/insights/departments` | — | Salary stats grouped by department |
| GET | `/insights/headcount` | — | Employee count broken down by country |
| GET | `/insights/top-earners` | `n` (max 100) | Top N highest-paid employees |

---

## Data Model

```
Organisation
  ├── id, org_name, org_address, currency, domain
  ├── → Users (one-to-many)
  └── → Employees (one-to-many)

User
  └── id, org_id (FK), user_email, hashed_password

Employee
  └── id, org_id (FK), full_name, email, job_title,
      department, country, salary
      Unique: (org_id, email)
```

---

## Authentication & Multi-Tenancy

- Passwords are hashed with **bcrypt**.
- On login, a **JWT** is issued containing the user's `email` and `org_id` (expires in 60 min by default).
- Every protected endpoint extracts `org_id` from the token via the `get_current_org_id` dependency, ensuring queries are always scoped to the correct organisation.

---

## Running Tests

```bash
pytest
```

```bash
# With coverage report
pytest --cov=app --cov-report=term-missing
```

### Test Coverage

| Test File | Scope |
|-----------|-------|
| `test_employee_routes.py` | API integration (CRUD, pagination, error cases) |
| `test_employee_service.py` | Business logic with mocked repository |
| `test_employee_repository.py` | Database queries and persistence |
| `test_insight_routes.py` | Analytics endpoints |
| `test_insight_service.py` | Analytics aggregations and sorting |
| `test_schemas.py` | Pydantic validation rules |

---

## Architecture

The codebase follows a layered architecture with clear separation of concerns:

```
HTTP Request
    ↓
API Routes (app/api/)         — HTTP contracts, request/response shaping
    ↓
Services (app/services/)      — Business logic, validation, error handling
    ↓
Repositories (app/repositories/) — SQL queries, data access
    ↓
Models (app/models/)          — SQLAlchemy ORM definitions
```

Schemas (app/schemas/) validate input/output at the API boundary using Pydantic.
