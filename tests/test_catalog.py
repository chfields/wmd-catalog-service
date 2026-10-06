from concurrent.futures import ThreadPoolExecutor


def test_lists_seeded_products_by_name_with_availability(client):
    response = client.get("/v1/products")
    assert response.status_code == 200
    products = response.json()
    assert [p["name"] for p in products] == sorted(p["name"] for p in products)
    eggs = next(p for p in products if p["id"] == "sku-eggs")
    assert eggs == {
        "id": "sku-eggs",
        "name": "Free-Range Eggs",
        "description": "One dozen large eggs",
        "priceCents": 549,
        "stock": 0,
        "available": False,
        "lowStock": False,
        "restockDate": None,
    }


def test_filters_by_name_or_description_case_insensitively(client):
    assert [p["id"] for p in client.get("/v1/products", params={"q": "BAGEL"}).json()] == [
        "sku-bagels"
    ]
    assert [p["id"] for p in client.get("/v1/products", params={"q": "pecans"}).json()] == [
        "sku-granola"
    ]
    assert client.get("/v1/products", params={"q": "caviar"}).json() == []


def test_sorts_products(client):
    expected_ids = {
        "featured": [
            "sku-coffee",
            "sku-bagels",
            "sku-eggs",
            "sku-granola",
            "sku-berries",
            "sku-oat-milk",
        ],
        "price_asc": [
            "sku-oat-milk",
            "sku-eggs",
            "sku-bagels",
            "sku-granola",
            "sku-berries",
            "sku-coffee",
        ],
        "price_desc": [
            "sku-coffee",
            "sku-berries",
            "sku-granola",
            "sku-bagels",
            "sku-eggs",
            "sku-oat-milk",
        ],
        "name_asc": [
            "sku-coffee",
            "sku-bagels",
            "sku-eggs",
            "sku-granola",
            "sku-berries",
            "sku-oat-milk",
        ],
    }

    for sort, expected in expected_ids.items():
        response = client.get("/v1/products", params={"sort": sort})
        assert response.status_code == 200
        assert [product["id"] for product in response.json()] == expected


def test_uses_featured_order_without_a_sort_or_with_an_empty_sort(client):
    featured = client.get("/v1/products", params={"sort": "featured"}).json()

    assert client.get("/v1/products").json() == featured
    assert client.get("/v1/products", params={"sort": ""}).json() == featured


def test_filters_then_sorts_products(client):
    response = client.get("/v1/products", params={"q": "b", "sort": "price_desc"})

    assert [product["id"] for product in response.json()] == [
        "sku-coffee",
        "sku-berries",
        "sku-bagels",
        "sku-oat-milk",
    ]


def test_breaks_price_ties_by_name_then_id(client, database):
    with database.connect() as conn:
        conn.execute("update products set price_cents = 100")
        conn.execute("update products set name = 'Same' where id in ('sku-coffee', 'sku-bagels')")

    response = client.get("/v1/products", params={"sort": "price_asc"})

    assert [product["id"] for product in response.json()] == [
        "sku-eggs",
        "sku-granola",
        "sku-berries",
        "sku-oat-milk",
        "sku-bagels",
        "sku-coffee",
    ]


def test_rejects_an_unknown_product_sort(client):
    response = client.get("/v1/products", params={"sort": "newest"})

    assert response.status_code == 400
    assert response.json() == {
        "error": {"code": "invalid_request", "message": "Invalid sort value: newest."}
    }


def test_gets_one_product_or_a_404_with_a_code(client):
    assert client.get("/v1/products/sku-coffee").json()["priceCents"] == 899
    missing = client.get("/v1/products/sku-caviar")
    assert missing.status_code == 404
    assert missing.json() == {
        "error": {"code": "unknown_product", "message": "No product sku-caviar."}
    }


def test_returns_restock_date_for_list_and_single_product_routes(client, database):
    assert client.get("/v1/products/sku-coffee").json()["restockDate"] is None
    assert (
        next(
            product
            for product in client.get("/v1/products").json()
            if product["id"] == "sku-coffee"
        )["restockDate"]
        is None
    )

    with database.connect() as conn:
        conn.execute(
            "update products set restock_date = %s where id = %s",
            ("2026-10-20", "sku-coffee"),
        )

    assert client.get("/v1/products/sku-coffee").json()["restockDate"] == "2026-10-20"
    assert (
        next(
            product
            for product in client.get("/v1/products").json()
            if product["id"] == "sku-coffee"
        )["restockDate"]
        == "2026-10-20"
    )


def test_reports_low_stock_boundaries_for_list_and_single_product_routes(client, database):
    stocks = {
        "sku-eggs": 0,
        "sku-coffee": 1,
        "sku-bagels": 5,
        "sku-oat-milk": 6,
        "sku-berries": 15,
        "sku-granola": 40,
    }
    with database.connect() as conn:
        for product_id, stock in stocks.items():
            conn.execute("update products set stock = %s where id = %s", (stock, product_id))

    expected = {product_id: 0 < stock <= 5 for product_id, stock in stocks.items()}
    listed = {product["id"]: product["lowStock"] for product in client.get("/v1/products").json()}
    assert listed == expected
    assert {
        product_id: client.get(f"/v1/products/{product_id}").json()["lowStock"]
        for product_id in stocks
    } == expected


def test_reserves_stock_and_prices_the_lines(client):
    response = client.post(
        "/v1/reservations",
        json={
            "orderRef": "order-1",
            "items": [
                {"productId": "sku-coffee", "quantity": 2},
                {"productId": "sku-bagels", "quantity": 1},
                {"productId": "sku-coffee", "quantity": 1},
            ],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["orderRef"] == "order-1"
    assert body["lines"] == [
        {"productId": "sku-bagels", "name": "Everything Bagels", "quantity": 1, "priceCents": 649},
        {"productId": "sku-coffee", "name": "Cold Brew Coffee", "quantity": 3, "priceCents": 899},
    ]
    assert body["totalCents"] == 649 + 3 * 899
    assert client.get("/v1/products/sku-coffee").json()["stock"] == 37


def test_reserves_nothing_when_any_item_is_short(client):
    response = client.post(
        "/v1/reservations",
        json={
            "orderRef": "order-2",
            "items": [
                {"productId": "sku-coffee", "quantity": 1},
                {"productId": "sku-eggs", "quantity": 1},
            ],
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "unavailable"
    assert client.get("/v1/products/sku-coffee").json()["stock"] == 40


def test_refuses_an_unknown_product(client):
    response = client.post(
        "/v1/reservations",
        json={"orderRef": "order-3", "items": [{"productId": "sku-caviar", "quantity": 1}]},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unknown_product"


def test_never_oversells_under_concurrent_reservations(client):
    def reserve(n: int) -> int:
        return client.post(
            "/v1/reservations",
            json={"orderRef": f"race-{n}", "items": [{"productId": "sku-berries", "quantity": 1}]},
        ).status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = list(pool.map(reserve, range(20)))
    assert statuses.count(201) == 15
    assert statuses.count(409) == 5
    assert client.get("/v1/products/sku-berries").json()["stock"] == 0
