---
type: convention
title: Errors are {"error": {"code", "message"}} with stable codes
description: Every API error uses this shape, and codes are stable identifiers clients branch on, so they are never renamed.
tags: [core, api, errors]
status: stable
generated:
  by: wmd-catalog-builder/gpt-5.6-terra
  at: 2026-10-04T15:15:59+00:00
sources:
  - id: api-error
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/observability.py#L27-L34
  - id: error-handler
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/observability.py#L105-L114
  - id: catalog-errors
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/main.py#L86-L120
  - id: error-test
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/tests/test_catalog.py#L30-L36
  - id: canonical
    url: https://github.com/chfields/wmd-deploy/blob/main/docs/knowledge/core/error-contract.md
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: [app/observability.py, app/main.py, openapi.json]
  citations:
    - id: api-error
      repo: github:chfields/wmd-catalog-service
      path: app/observability.py
      lines: [27, 34]
      symbol: ApiError
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:005f4b5899e02f46598e72c33ce20c28d6a89769fe9f64e8b9459347f023e610
    - id: error-handler
      repo: github:chfields/wmd-catalog-service
      path: app/observability.py
      lines: [105, 114]
      symbol: install._api_error
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:0a817a3256033a06bdaa1d1748e68b1d9fc3e416777a3aa54e5b27588a9db6d6
    - id: catalog-errors
      repo: github:chfields/wmd-catalog-service
      path: app/main.py
      lines: [86, 120]
      symbol: get_product, reserve
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:d75bd83702e22513af80a793f067a6958877d488aa83934257d2f4144d3ea5a3
    - id: error-test
      repo: github:chfields/wmd-catalog-service
      path: tests/test_catalog.py
      lines: [30, 36]
      symbol: test_gets_one_product_or_a_404_with_a_code
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:fa662d8bf7a8db39d7e2114a78bbcf4366b356cc68567c67c653c3ddef683fe5
  confidence: high
---

Errors are raised as ApiError(status, code, message) and rendered as {"error": {"code", "message"}}. The codes unknown_product and unavailable are relied on by callers (order-service) and must not be renamed.[^api-error][^error-handler][^catalog-errors][^error-test]

What to do: preserve error codes and the response shape.

[^api-error]: api-error
[^error-handler]: error-handler
[^catalog-errors]: catalog-errors
[^error-test]: error-test
