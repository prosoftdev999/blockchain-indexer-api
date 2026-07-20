from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert body["message"] == "Blockchain Indexer API"
    assert body["documentation"] == "/docs"


def test_openapi_schema(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    body = response.json()

    assert body["info"]["title"] == "Blockchain Indexer API"
    assert "/api/v1/blocks" in body["paths"]
    assert "/api/v1/transactions" in body["paths"]
    assert "/api/v1/indexer/status" in body["paths"]