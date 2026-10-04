"""Database access. Each service owns one Postgres schema; its role can't read any other."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

MIGRATIONS = Path(__file__).resolve().parent.parent / "migrations"
SCHEMA_NAME = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")


class Database:
    def __init__(self, url: str, schema: str) -> None:
        if not SCHEMA_NAME.match(schema):
            raise ValueError(f"invalid schema name: {schema!r}")
        self.url = url
        self.schema = schema

    @contextmanager
    def connect(self) -> Iterator[psycopg.Connection]:
        """A connection whose search_path is this service's schema. Commits on success."""
        with psycopg.connect(
            self.url, row_factory=dict_row, options=f"-c search_path={self.schema}"
        ) as conn:
            yield conn

    def migrate(self) -> None:
        """Create the schema if needed and apply migrations/*.sql in order, once each."""
        with psycopg.connect(self.url, autocommit=True) as conn:
            exists = conn.execute(
                "select 1 from pg_namespace where nspname = %s", (self.schema,)
            ).fetchone()
            if not exists:
                conn.execute(sql.SQL("create schema {}").format(sql.Identifier(self.schema)))
        with self.connect() as conn:
            # Replicas starting together take turns.
            conn.execute("select pg_advisory_xact_lock(hashtext(%s))", (self.schema,))
            conn.execute(
                "create table if not exists schema_migrations ("
                " name text primary key, applied_at timestamptz not null default now())"
            )
            applied = {row["name"] for row in conn.execute("select name from schema_migrations")}
            for path in sorted(MIGRATIONS.glob("*.sql")):
                if path.name in applied:
                    continue
                conn.execute(path.read_text())
                conn.execute("insert into schema_migrations (name) values (%s)", (path.name,))

    def ping(self) -> None:
        with self.connect() as conn:
            conn.execute("select 1")


def database_from_env(default_schema: str) -> Database:
    return Database(os.environ["DATABASE_URL"], os.environ.get("DB_SCHEMA", default_schema))
