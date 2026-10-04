---
type: invariant
title: Reservations lock product rows in sorted id order with a conditional decrement
description: reserve merges duplicate productIds, then decrements stock in sorted productId order with "stock >= quantity" in the UPDATE, which prevents deadlocks and overselling.
tags: [reservations, concurrency, postgres]
status: stable
generated:
  by: wmd-catalog-builder/gpt-5.6-terra
  at: 2026-10-04T15:15:59+00:00
sources:
  - id: reserve-lock-order
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/main.py#L100-L111
  - id: concurrent-reservation-test
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/tests/test_catalog.py#L87-L98
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: [app/main.py]
  citations:
    - id: reserve-lock-order
      repo: github:chfields/wmd-catalog-service
      path: app/main.py
      lines: [100, 111]
      symbol: reserve
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:40b74d454672fdb7ebfc9ee080e4c828d8d3b91e8a6848aaa32f029cb665184c
    - id: concurrent-reservation-test
      repo: github:chfields/wmd-catalog-service
      path: tests/test_catalog.py
      lines: [87, 98]
      symbol: test_never_oversells_under_concurrent_reservations
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:114d9986e523deaebd77a273f4a9fdec54b20aba6905855b0ea3ed69e8664b1c
  confidence: high
---

Do not replace the conditional UPDATE with a read-then-write, and keep the sorted iteration: concurrent reservations then serialize on row locks without deadlocking and never take stock below zero.[^reserve-lock-order][^concurrent-reservation-test]

What to do: merge duplicates and retain the conditional, sorted update.

[^reserve-lock-order]: reserve-lock-order
[^concurrent-reservation-test]: concurrent-reservation-test
