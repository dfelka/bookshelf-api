"""Shared test fixtures: an isolated in-memory DB and a wired-up TestClient."""

import os

# Point the app at SQLite before it is imported, so importing app.database
# does not try to construct (and import the driver for) a Postgres engine.
# The tests never use this engine directly — get_db is overridden below — but
# this keeps the suite runnable without Postgres or psycopg2 installed.
os.environ.setdefault("DATABASE_URL", "sqlite://")

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db

# Importing the model registers the `books` table on Base.metadata so that
# create_all() below knows about it.
from app.models.book import Book  # noqa: F401
from app.main import app


@pytest.fixture
def engine():
    """A fresh SQLite in-memory database per test.

    StaticPool keeps a single connection alive so the in-memory schema
    persists across sessions opened during the test.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    """A DB session bound to the per-test in-memory database."""
    TestingSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """A TestClient whose `get_db` dependency uses the test session."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
