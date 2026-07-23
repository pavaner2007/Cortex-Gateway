"""
Cortex Gateway – pytest Configuration & Fixtures

Provides:
  - async_client : HTTPX AsyncClient wired to the FastAPI test app
  - override_get_db : replaces real DB dependency with a test session
  - override_get_redis : replaces real Redis dependency with a mock
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database.session import get_db
from app.main import create_app
from app.services.redis_client import get_redis


# ─────────────────────────────────────────────────────────────────────────────
# Mocks
# ─────────────────────────────────────────────────────────────────────────────

class MockRedis:
    """Minimal Redis mock that satisfies health check requirements."""

    async def ping(self) -> bool:
        return True

    async def get(self, key: str) -> None:
        return None

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        return True


class MockDBSession:
    """Minimal async DB session mock."""

    async def execute(self, query):  # noqa: ANN001
        mock_result = MagicMock()
        return mock_result

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def close(self) -> None:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_app():
    """Create a test FastAPI application instance."""
    app = create_app()

    # Override dependencies with mocks so tests don't need real infra
    async def _mock_db() -> AsyncGenerator:
        yield MockDBSession()

    async def _mock_redis() -> MockRedis:
        return MockRedis()

    app.dependency_overrides[get_db] = _mock_db
    app.dependency_overrides[get_redis] = _mock_redis

    return app


@pytest_asyncio.fixture(scope="session")
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client targeting the test application."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver",
    ) as client:
        yield client
