---
type: convention
title: Every request carries one x-correlation-id end to end
description: Each service accepts x-correlation-id (or makes one), logs it, returns it, and forwards it on every outbound call.
tags: [core, observability, logging]
status: stable
generated:
  by: wmd-catalog-builder/gpt-5.6-terra
  at: 2026-10-04T15:15:59+00:00
sources:
  - id: formatter
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/observability.py#L42-L53
  - id: outbound-headers
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/observability.py#L66-L69
  - id: observability-dispatch
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/app/observability.py#L77-L102
  - id: canonical
    url: https://github.com/chfields/wmd-deploy/blob/main/docs/knowledge/core/correlation-id-propagation.md
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: [app/observability.py, app/main.py]
  citations:
    - id: formatter
      repo: github:chfields/wmd-catalog-service
      path: app/observability.py
      lines: [42, 53]
      symbol: JsonFormatter.format
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:051ae050296ed2d90b16fc3a0ba5a493d324e69f3b0df77d2b4f2a22794f96af
    - id: outbound-headers
      repo: github:chfields/wmd-catalog-service
      path: app/observability.py
      lines: [66, 69]
      symbol: outbound_headers
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:83cc148e44b49556e89cea68855d4040da9288382f9e5c28c0516f645ad8ed93
    - id: observability-dispatch
      repo: github:chfields/wmd-catalog-service
      path: app/observability.py
      lines: [77, 102]
      symbol: _Observability.dispatch
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:14f49b922b7425db60b83f668c32ecca9cb9f7c99cbb42b1c88e962bca8d7ea3
  confidence: high
---

The middleware accepts a valid x-correlation-id or generates one, puts it in every JSON log line and on the response. Any future outbound call must send `outbound_headers()`.[^formatter][^outbound-headers][^observability-dispatch]

What to do: forward `outbound_headers()` on every outbound call.

[^formatter]: formatter
[^outbound-headers]: outbound-headers
[^observability-dispatch]: observability-dispatch
