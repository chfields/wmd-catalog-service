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
    }


def test_filters_by_name_or_description_case_insensitively(client):
    assert [p["id"] for p in client.get("/v1/products", params={"q": "BAGEL"}).json()] == [
        "sku-bagels"
    ]
    assert [p["id"] for p in client.get("/v1/products", params={"q": "pecans"}).json()] == [
        "sku-granola"
    ]
    assert client.get("/v1/products", params={"q": "caviar"}).json() == []


def test_gets_one_product_or_a_404_with_a_code(client):
    assert client.get("/v1/products/sku-coffee").json()["priceCents"] == 899
    missing = client.get("/v1/products/sku-caviar")
    assert missing.status_code == 404
    assert missing.json() == {
        "error": {"code": "unknown_product", "message": "No product sku-caviar."}
    }


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
