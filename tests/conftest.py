"""Tests use a real Postgres: DATABASE_URL (a Wardby coding run sets it) or local docker."""

import os
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql

from app.db import Database
from app.main import create_app

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://wmd:wmd@localhost:55440/wmd")


@pytest.fixture
def database():
    """A fresh schema per test, dropped afterwards."""
    db = Database(DATABASE_URL, f"catalog_test_{uuid.uuid4().hex[:12]}")
    yield db
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute(sql.SQL("drop schema if exists {} cascade").format(sql.Identifier(db.schema)))


@pytest.fixture
def client(database):
    with TestClient(create_app(database)) as test_client:
        yield test_client
