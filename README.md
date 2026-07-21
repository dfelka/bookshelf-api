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

## Project Structure

```
my-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings via environment variables
│   ├── database.py          # DB engine, session, Base
│   ├── models/              # SQLAlchemy table models
│   │   ├── __init__.py
│   │   └── item.py          # Example: Item model
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   └── item.py
│   ├── routers/             # Route handlers grouped by resource
│   │   ├── __init__.py
│   │   └── items.py
│   └── services/            # Business logic (keeps routers thin)
│       ├── __init__.py
│       └── item_service.py
├── tests/
│   ├── conftest.py          # Shared fixtures (test DB, client)
│   ├── test_items.py        # Integration tests for /items
│   └── test_item_service.py # Unit tests for business logic
├── alembic/                 # Database migrations
│   └── versions/
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
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
-- Example: Items table (replace with your domain)
CREATE TABLE items (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(200)  NOT NULL,
    description TEXT,
    is_done     BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- Add more tables below as your project grows
-- CREATE TABLE users ( ... );
```


## CRUD Endpoints

| Method   | Path            | Description              | Request Body              | Response         |
|----------|-----------------|--------------------------|---------------------------|------------------|
| `GET`    | `/health`       | Health check             | —                         | `{ status: ok }` |
| `GET`    | `/items`        | List items (paginated)   | —                         | `Item[]`         |
| `GET`    | `/items/{id}`   | Get single item          | —                         | `Item`           |
| `POST`   | `/items`        | Create new item          | `{ title, description }`  | `Item`           |
| `PATCH`  | `/items/{id}`   | Update item              | partial `Item` fields     | `Item`           |
| `DELETE` | `/items/{id}`   | Delete item              | —                         | `204 No Content` |
