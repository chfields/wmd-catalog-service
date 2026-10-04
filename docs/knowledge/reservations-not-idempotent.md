---
type: pitfall
title: A repeated reservation request reserves stock again
description: POST /v1/reservations does not deduplicate by orderRef; reservations.order_ref has only a non-unique index, so a retried call takes stock twice.
tags: [reservations, idempotency]
status: stable
generated:
  by: wmd-catalog-builder/gpt-5.6-terra
  at: 2026-10-04T15:15:59+00:00
sources:
  - id: reservation-index
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/migrations/001_init.sql#L10-L17
  - id: reservation-insert
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/main.py#L129-L132
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: [app/main.py, migrations/**]
  citations:
    - id: reservation-index
      repo: github:chfields/wmd-catalog-service
      path: migrations/001_init.sql
      lines: [10, 17]
      symbol: reservations_order_ref
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:4bb6f77cdaaf21713b6e612b2d225036effa061356810d838c5c798a81674e4e
    - id: reservation-insert
      repo: github:chfields/wmd-catalog-service
      path: app/main.py
      lines: [129, 132]
      symbol: reserve
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:d2b0c8e62449755ea5ea2134fa8a8327ed762ae3989a5a6de722f9c0bce7c3b5
  confidence: high
---

Each call inserts a new reservation and decrements stock, even for an orderRef seen before. Callers must not blindly retry; making it idempotent needs a new migration and a code change.[^reservation-index][^reservation-insert]

What to do: do not retry this endpoint blindly.

[^reservation-index]: reservation-index
[^reservation-insert]: reservation-insert
