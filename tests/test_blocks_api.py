from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.api.v1.blocks as blocks_api


def create_block() -> SimpleNamespace:
    now = datetime.now(timezone.utc)

    return SimpleNamespace(
        id=1,
        number=11309115,
        block_hash=(
            "0x99b987b581a210dbb0a967933e18940d"
            "8da801d35c81ae3963b22f9171f32b80"
        ),
        parent_hash=(
            "0x6de1c3dc27d8f72491bb0bb47e0e56be"
            "a42ccfc907750f1acec4ed18e473f769"
        ),
        timestamp=now,
        transaction_count=84,
        created_at=now,
    )


def test_list_blocks(
    client: TestClient,
    monkeypatch,
) -> None:
    block = create_block()

    async def fake_list_blocks(
        session,
        limit: int,
        offset: int,
    ):
        assert limit == 10
        assert offset == 0

        return [block], 1

    monkeypatch.setattr(
        blocks_api,
        "list_blocks",
        fake_list_blocks,
    )

    response = client.get(
        "/api/v1/blocks?limit=10&offset=0"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["limit"] == 10
    assert body["offset"] == 0
    assert body["items"][0]["number"] == 11309115
    assert body["items"][0]["transaction_count"] == 84


def test_get_block(
    client: TestClient,
    monkeypatch,
) -> None:
    block = create_block()

    async def fake_get_block_by_number(
        session,
        block_number: int,
    ):
        assert block_number == 11309115

        return block

    monkeypatch.setattr(
        blocks_api,
        "get_block_by_number",
        fake_get_block_by_number,
    )

    response = client.get(
        "/api/v1/blocks/11309115"
    )

    assert response.status_code == 200
    assert response.json()["number"] == 11309115


def test_get_missing_block(
    client: TestClient,
    monkeypatch,
) -> None:
    async def fake_get_block_by_number(
        session,
        block_number: int,
    ):
        return None

    monkeypatch.setattr(
        blocks_api,
        "get_block_by_number",
        fake_get_block_by_number,
    )

    response = client.get(
        "/api/v1/blocks/999999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Block 999999999 was not found."
    }


def test_block_limit_validation(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/blocks?limit=101"
    )

    assert response.status_code == 422