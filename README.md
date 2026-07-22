# Bookshelf API

A production-ready backend REST API for managing a bookstore inventory. The project demonstrates the full backend lifecycle: schema design, containerization, testing, CI/CD, cloud deployment, and documentation.

## Features

- Full CRUD for the primary resource
- Input validation and error handling
- Pagination and filtering on list endpoints
- Health-check endpoint (`GET /health`)
- Dockerized local development
- Automated test suite and CI/CD pipeline via GitHub Actions
- Cloud deployment
- User registration and authentication *(optional)*

## Tech Stack

| Layer            | Choice                   |
| ---------------- | ------------------------ |
| Language         | Python 3.12+             |
| Framework        | FastAPI                  |
| Database         | PostgreSQL 16            |
| ORM              | SQLAlchemy 2.0 + Alembic |
| Validation       | Pydantic v2              |
| Testing          | pytest + httpx           |
| Containerization | Docker + docker-compose  |
| CI/CD            | GitHub Actions           |
| Deployment       | Render / Railway         |

## Getting Started

### Run with Docker (recommended)

The whole stack — the API plus a PostgreSQL 16 database — runs with one command.
On startup the app container applies Alembic migrations and then launches the server.

```bash
docker compose up --build
```

- API: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/health

Stop the stack (containers only) with `docker compose down`, or
`docker compose down -v` to also drop the database volume.

### Run locally (without Docker)

Requires Python 3.12+ and a reachable PostgreSQL instance.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit DATABASE_URL if needed
alembic upgrade head             # create the books table
uvicorn app.main:app --reload    # auto-docs at /docs
```

### Testing

The suite runs entirely against an in-memory SQLite database, so no Postgres
(or `psycopg2`) is required — just the app plus the test tools:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install fastapi sqlalchemy pydantic pydantic-settings pytest httpx pytest-cov

pytest                                       # all tests
pytest -v                                    # verbose
pytest --cov=app --cov-report=term-missing   # with coverage (currently 96%)
```

> On Python 3.12 you can instead `pip install -r requirements-dev.txt`.
> The explicit list above avoids the `psycopg2-binary` build, which has no
> wheel for newer Python versions on Windows and isn't needed for the tests.

## Project Structure

```
bookshelf-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + error-envelope handlers
│   ├── config.py            # Settings via environment variables
│   ├── database.py          # DB engine, session, Base
│   ├── errors.py            # Domain exceptions (NotFound, Conflict, ...)
│   ├── models/              # SQLAlchemy table models
│   │   ├── __init__.py
│   │   └── book.py          # Book model
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── book.py
│   │   └── common.py        # Data / list / error envelopes
│   ├── routers/             # Route handlers grouped by resource
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── books.py
│   └── services/            # Business logic (keeps routers thin)
│       ├── __init__.py
│       └── book_service.py
├── tests/                   # Test suite (pytest)
│   ├── conftest.py          # In-memory DB + TestClient fixtures
│   ├── test_book_service.py # Unit tests for the service layer
│   ├── test_books.py        # Integration tests for /books
│   ├── test_health.py       # Health-check test
│   └── test_root.py         # Root metadata endpoint test
├── alembic/                 # Database migrations
│   ├── env.py
│   └── versions/
│       └── 0001_initial.py
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt     # Test/dev deps (pytest, httpx, pytest-cov)
├── .env.example             # Template for environment variables
├── .gitignore
└── README.md
```

## Architecture Diagram

```
┌────────────┐       ┌─────────────────────────────────────────┐
│            │  HTTP │  FastAPI Application                    │
│   Client   │◄─────►│                                         │
│ (Postman / │       │  ┌──────────┐  ┌──────────┐  ┌───────┐  │     ┌────────────┐
│  curl /    │       │  │  Router  │─►│ Service  │─►│  ORM  │──┼────►│ PostgreSQL │
│  browser)  │       │  └──────────┘  └──────────┘  └───────┘  │     └────────────┘
│            │       │       ▲                                 │
└────────────┘       │  ┌────┴─────┐                           │
                     │  │ Pydantic │  (validates in/out)       │
                     │  └──────────┘                           │
                     └─────────────────────────────────────────┘
```

Request flow: Client → Router (endpoint) → Service (logic) → ORM (database) → PostgreSQL

## Database Schema

```sql
CREATE TABLE books (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(200)  NOT NULL,
    author      VARCHAR(200),
    description TEXT,
    is_done     BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

## CRUD Endpoints

| Method   | Path            | Description                        |
|----------|-----------------|-----------------------------------|
| `GET`    | `/health`       | Health check                      |
| `GET`    | `/books`        | List books (paginated, filterable)|
| `GET`    | `/books/{id}`   | Get single book                   |
| `POST`   | `/books`        | Create new book                   |
| `PATCH`  | `/books/{id}`   | Update book (partial)             |
| `DELETE` | `/books/{id}`   | Delete book                       |
