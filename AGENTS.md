# Working in wmd-catalog-service

Python 3.12, FastAPI, psycopg 3, Postgres. Owns products, availability and
reservations for WMD Shop. Other services reach it only through its HTTP API.

## Run the checks

```bash
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/pytest
```

Tests need Postgres at `DATABASE_URL`. In a Wardby coding run it is already
set (the repository declares `postgres: "16"` in `.wardby/services.yaml`).
Locally, tests default to `postgresql://wmd:wmd@localhost:55440/wmd`. Each test
gets its own schema, so tests can't see each other's data.

## Rules

- **Data:** the service owns one schema (`catalog`). Change it only with a new
  file in `migrations/` (`NNN_name.sql`); never edit an applied migration.
- **Contract:** `openapi.json` is the published API. If you change a route or
  a model, regenerate it with `python -m app.contract > openapi.json` and say
  so in the PR. `tests/test_contract.py` fails until you do.
- **Errors** use `ApiError(status, code, message)`, returned as
  `{"error": {"code", "message"}}`. Codes are stable; don't rename them.
- **Logs** are JSON with the request's `correlationId`; use `logging` and pass
  structured fields with `extra={"fields": {...}}`. Never log secrets.
- Keep `/healthz`, `/readyz` and `/metrics` working.
- Every behaviour change comes with a test.
