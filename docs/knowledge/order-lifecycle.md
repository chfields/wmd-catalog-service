---
type: invariant
title: Orders reserve stock first and are confirmed only after notification
description: An order exists only after catalog-service reserves all its stock in one transaction, and moves from pending to confirmed only when notification-service accepts the confirmation, which is idempotent per order and kind.
tags: [core, orders, reservations]
status: stable
generated:
  by: wmd-catalog-builder/gpt-5.6-terra
  at: 2026-10-04T15:15:59+00:00
sources:
  - id: reserve
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/main.py#L97-L138
  - id: atomic-reservation-test
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/tests/test_catalog.py#L62-L75
  - id: concurrent-reservation-test
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/tests/test_catalog.py#L87-L98
  - id: canonical
    url: https://github.com/chfields/wmd-deploy/blob/main/docs/knowledge/core/order-lifecycle.md
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: [app/main.py, migrations/**]
  citations:
    - id: reserve
      repo: github:chfields/wmd-catalog-service
      path: app/main.py
      lines: [97, 138]
      symbol: reserve
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:9532422e79e7e76152d05bad7fa3162d3073aacb883afc0d2faa5e62929ade90
    - id: atomic-reservation-test
      repo: github:chfields/wmd-catalog-service
      path: tests/test_catalog.py
      lines: [62, 75]
      symbol: test_reserves_nothing_when_any_item_is_short
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:e56a2b90926e16ebe3fe26f41be6f544d8f31235dbf045ce4b911662fe324f30
    - id: concurrent-reservation-test
      repo: github:chfields/wmd-catalog-service
      path: tests/test_catalog.py
      lines: [87, 98]
      symbol: test_never_oversells_under_concurrent_reservations
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:114d9986e523deaebd77a273f4a9fdec54b20aba6905855b0ea3ed69e8664b1c
  confidence: high
---

catalog-service's part of the lifecycle is the reservation: it decrements stock for every item or none inside a single transaction, so an order can be created only when all its stock is reserved. Confirmation and notification happen elsewhere.[^reserve][^atomic-reservation-test][^concurrent-reservation-test]

Why: a reservation must be atomic before the order lifecycle can continue.

[^reserve]: reserve
[^atomic-reservation-test]: atomic-reservation-test
[^concurrent-reservation-test]: concurrent-reservation-test
