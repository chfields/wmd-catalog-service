"""Every service: health, readiness, metrics and a correlation id on every response."""

import tomllib
from pathlib import Path


def test_health_returns_service_version_and_correlation_id(client):
    with (Path(__file__).parent.parent / "pyproject.toml").open("rb") as pyproject:
        version = tomllib.load(pyproject)["project"]["version"]

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "wmd-catalog",
        "version": version,
        "status": "ok",
    }
    assert response.headers["x-correlation-id"]


def test_health_and_readiness(client):
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"status": "ready"}


def test_echoes_a_valid_correlation_id_and_generates_one_otherwise(client):
    assert (
        client.get("/v1/products", headers={"x-correlation-id": "abc-123"}).headers[
            "x-correlation-id"
        ]
        == "abc-123"
    )
    generated = client.get("/v1/products", headers={"x-correlation-id": "bad id!"})
    assert generated.headers["x-correlation-id"] not in ("", "bad id!")


def test_counts_requests_by_route(client):
    client.get("/v1/products/sku-coffee")
    metrics = client.get("/metrics").text
    assert (
        'http_requests_total{method="GET",path="/v1/products/{product_id}",status="200"} 1'
        in metrics
    )
