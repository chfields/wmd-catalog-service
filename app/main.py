"""catalog-service: products, availability and reservations."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from app.db import Database, database_from_env
from app.observability import ApiError, configure_logging, install

SERVICE = "catalog-service"


class Product(BaseModel):
    id: str
    name: str
    description: str
    priceCents: int
    stock: int
    available: bool


class ReservationItem(BaseModel):
    productId: str = Field(min_length=1, max_length=64)
    quantity: int = Field(ge=1, le=100)


class ReservationRequest(BaseModel):
    orderRef: str = Field(min_length=1, max_length=64)
    items: list[ReservationItem] = Field(min_length=1, max_length=50)


class ReservedLine(BaseModel):
    productId: str
    name: str
    quantity: int
    priceCents: int


class Reservation(BaseModel):
    id: str
    orderRef: str
    lines: list[ReservedLine]
    totalCents: int


def _product(row: dict) -> Product:
    return Product(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        priceCents=row["price_cents"],
        stock=row["stock"],
        available=row["stock"] > 0,
    )


def create_app(db: Database | None = None, *, migrate: bool = True) -> FastAPI:
    database = db or database_from_env("catalog")

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if migrate:
            database.migrate()
        yield

    app = FastAPI(title="wmd catalog-service", version="1.0.0", lifespan=lifespan)
    install(app, database.ping)

    @app.get("/v1/products", response_model=list[Product])
    def list_products(q: str | None = Query(default=None, max_length=100)) -> list[Product]:
        with database.connect() as conn:
            rows = conn.execute(
                "select id, name, description, price_cents, stock from products"
                " where %(q)s::text is null"
                "    or name ilike '%%' || %(q)s || '%%'"
                "    or description ilike '%%' || %(q)s || '%%'"
                " order by name",
                {"q": q or None},
            ).fetchall()
        return [_product(row) for row in rows]

    @app.get("/v1/products/{product_id}", response_model=Product)
    def get_product(product_id: str) -> Product:
        with database.connect() as conn:
            row = conn.execute(
                "select id, name, description, price_cents, stock from products where id = %s",
                (product_id,),
            ).fetchone()
        if row is None:
            raise ApiError(404, "unknown_product", f"No product {product_id}.")
        return _product(row)

    @app.post("/v1/reservations", response_model=Reservation, status_code=201)
    def reserve(request: ReservationRequest) -> Reservation:
        """Take stock for every item or none: all-or-nothing in one transaction."""
        quantities: dict[str, int] = {}
        for item in request.items:
            quantities[item.productId] = quantities.get(item.productId, 0) + item.quantity
        lines: list[ReservedLine] = []
        with database.connect() as conn:
            # Lock rows in a fixed order so concurrent reservations can't deadlock.
            for product_id in sorted(quantities):
                quantity = quantities[product_id]
                row = conn.execute(
                    "update products set stock = stock - %s"
                    " where id = %s and stock >= %s returning name, price_cents",
                    (quantity, product_id, quantity),
                ).fetchone()
                if row is None:
                    # Raising rolls back every decrement made so far.
                    exists = conn.execute(
                        "select 1 from products where id = %s", (product_id,)
                    ).fetchone()
                    if not exists:
                        raise ApiError(422, "unknown_product", f"No product {product_id}.")
                    raise ApiError(409, "unavailable", f"Not enough {product_id} in stock.")
                lines.append(
                    ReservedLine(
                        productId=product_id,
                        name=row["name"],
                        quantity=quantity,
                        priceCents=row["price_cents"],
                    )
                )
            reservation = conn.execute(
                "insert into reservations (order_ref, lines) values (%s, %s::jsonb) returning id",
                (request.orderRef, json.dumps([line.model_dump() for line in lines])),
            ).fetchone()
        return Reservation(
            id=str(reservation["id"]),
            orderRef=request.orderRef,
            lines=lines,
            totalCents=sum(line.priceCents * line.quantity for line in lines),
        )

    return app


def main() -> FastAPI:
    """uvicorn entrypoint: `uvicorn app.main:main --factory`."""
    configure_logging(SERVICE)
    return create_app()
