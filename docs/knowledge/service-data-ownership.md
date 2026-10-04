---
type: invariant
title: Each service owns one Postgres schema and nothing else
description: A service reads and writes only its own schema through its own login role; another service's data is reached only through that service's HTTP API.
tags: [core, data, postgres]
status: stable
generated:
  by: wmd-catalog-builder/gpt-5.6-terra
  at: 2026-10-04T15:15:59+00:00
sources:
  - id: db-connect
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/db.py#L26-L31
  - id: db-from-env
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/db.py#L61-L62
  - id: create-app
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/main.py#L61-L62
  - id: initial-schema
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/migrations/001_init.sql#L1-L17
  - id: canonical
    url: https://github.com/chfields/wmd-deploy/blob/main/docs/knowledge/core/service-data-ownership.md
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: [app/db.py, app/main.py, migrations/**]
  citations:
    - id: db-connect
      repo: github:chfields/wmd-catalog-service
      path: app/db.py
      lines: [26, 31]
      symbol: Database.connect
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:d57aed221b405a6a53d0d597b8d1e491b25716966d16de8bca39fff906874666
    - id: db-from-env
      repo: github:chfields/wmd-catalog-service
      path: app/db.py
      lines: [61, 62]
      symbol: database_from_env
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:625ff883e43c0193322b29c227fc702dcb125af8d5051054e0e37c663a434535
    - id: create-app
      repo: github:chfields/wmd-catalog-service
      path: app/main.py
      lines: [61, 62]
      symbol: create_app
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:3bf35c353372154e1e753a770b6882430f5bf4200f28a1677cd4ee950cb5985c
    - id: initial-schema
      repo: github:chfields/wmd-catalog-service
      path: migrations/001_init.sql
      lines: [1, 17]
      symbol: initial schema
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:56f016f27304a6d3fb7ebdcd7d7aef9d783b65baeebc8c409b655be601e2e5e4
  confidence: high
---

catalog-service touches only the `catalog` schema: every connection pins search_path to it and migrations create unqualified tables there. Other services get products and stock only via its HTTP API (`/v1/products`, `/v1/reservations`), never by querying these tables.[^db-connect][^db-from-env][^create-app][^initial-schema]

Why: schema isolation keeps service data ownership enforceable.

[^db-connect]: db-connect
[^db-from-env]: db-from-env
[^create-app]: create-app
[^initial-schema]: initial-schema
