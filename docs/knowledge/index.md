# Architecture knowledge

## Core

- [Each service owns one Postgres schema and nothing else](service-data-ownership.md) — A service reads and writes only its own schema through its own login role; another service's data is reached only through that service's HTTP API.
- [Every request carries one x-correlation-id end to end](correlation-id-propagation.md) — Each service accepts x-correlation-id (or makes one), logs it, returns it, and forwards it on every outbound call.
- [Errors are {"error": {"code", "message"}} with stable codes](error-contract.md) — Every API error uses this shape, and codes are stable identifiers clients branch on, so they are never renamed.
- [Orders reserve stock first and are confirmed only after notification](order-lifecycle.md) — An order exists only after catalog-service reserves all its stock in one transaction, and moves from pending to confirmed only when notification-service accepts the confirmation, which is idempotent per order and kind.
- [Only merged main reaches staging](only-merged-code-reaches-staging.md) — deploy.sh builds every service from its origin/main in a clean checkout, so staging never runs unreviewed code.

## This repository

- [Reservations lock product rows in sorted id order with a conditional decrement](reservation-lock-order.md) — reserve merges duplicate productIds, then decrements stock in sorted productId order with "stock >= quantity" in the UPDATE, which prevents deadlocks and overselling.
- [A repeated reservation request reserves stock again](reservations-not-idempotent.md) — POST /v1/reservations does not deduplicate by orderRef; reservations.order_ref has only a non-unique index, so a retried call takes stock twice.
