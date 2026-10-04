---
type: decision
title: Only merged main reaches staging
description: deploy.sh builds every service from its origin/main in a clean checkout, so staging never runs unreviewed code.
tags: [core, deploy, ci]
status: stable
generated:
  by: wmd-catalog-builder/gpt-5.6-terra
  at: 2026-10-04T15:15:59+00:00
sources:
  - id: image-build
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/Dockerfile#L1-L11
  - id: ci-checks
    url: https://github.com/chfields/wmd-catalog-service/blob/ecf506c9a36ea53426c481fcdb7b1feed0e4f768/.github/workflows/test.yml#L1-L28
  - id: canonical
    url: https://github.com/chfields/wmd-deploy/blob/main/docs/knowledge/core/only-merged-code-reaches-staging.md
wardby:
  schema: 1
  roles: [reviewer, planner]
  affects: [Dockerfile, .github/workflows/test.yml]
  citations:
    - id: image-build
      repo: github:chfields/wmd-catalog-service
      path: Dockerfile
      lines: [1, 11]
      symbol: Dockerfile
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:1872275d6b7dd1b4610c0cff3e812abbece7998217ba51a84e1f855cb3561c99
    - id: ci-checks
      repo: github:chfields/wmd-catalog-service
      path: .github/workflows/test.yml
      lines: [1, 28]
      symbol: test workflow
      sha: ecf506c9a36ea53426c481fcdb7b1feed0e4f768
      spanHash: sha256:7cef579bba2a7f44dbd10a7ffedabc61710997d310718be8b13ee5536007053d
  confidence: medium
---

Staging runs the image built from this repository's origin/main by wmd-deploy's deploy.sh, so a change reaches staging only after it is merged; CI checks every pull request before merge.[^image-build][^ci-checks]

Why: deployment policy keeps unreviewed code out of staging.

[^image-build]: image-build
[^ci-checks]: ci-checks
