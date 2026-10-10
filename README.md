# wmd-catalog-service

Products, availability and reservations for WMD Shop, part of the Wardby
mobile demo.

| Route | Purpose |
|---|---|
| `GET /v1/products?q=&sort=` | List products, optionally filtered by name or description and sorted |
| `GET /v1/products/{id}` | One product |
| `POST /v1/reservations` | Take stock for every item or none; returns priced lines |
| `GET /health` | Service health and version |
| `GET /healthz`, `/readyz`, `/metrics` | Health, readiness, Prometheus metrics |

The full contract is [`openapi.json`](openapi.json). See [`AGENTS.md`](AGENTS.md)
for how to run and change it.

Configuration: `DATABASE_URL` (required), `DB_SCHEMA` (default `catalog`).
