from collections.abc import AsyncGenerator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


class DummySession:
    async def rollback(self) -> None:
        return None

    async def close(self) -> None:
        return None


async def override_get_db() -> AsyncGenerator[Any, None]:
    yield DummySession()


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()