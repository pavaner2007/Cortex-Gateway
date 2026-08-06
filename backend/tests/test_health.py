"""
Cortex Gateway – Health, Root, and Version Endpoint Tests

All tests are async and use the session-scoped async_client fixture
from conftest.py (no real database or Redis required).
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.anyio


# ─────────────────────────────────────────────────────────────────────────────
# GET / (Root)
# ─────────────────────────────────────────────────────────────────────────────

class TestRoot:
    async def test_root_returns_200(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/")
        assert response.status_code == 200

    async def test_root_contains_name(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/")
        data = response.json()
        assert "name" in data
        assert data["name"] == "Cortex Gateway"

    async def test_root_contains_docs_link(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/")
        data = response.json()
        assert "docs" in data
        assert "/docs" in data["docs"]

    async def test_root_contains_health_link(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/")).json()
        assert "health" in data


# ─────────────────────────────────────────────────────────────────────────────
# GET /health
# ─────────────────────────────────────────────────────────────────────────────

class TestHealth:
    async def test_health_returns_200(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/health")
        assert response.status_code == 200

    async def test_health_schema(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/health")).json()
        assert "status" in data
        assert "database" in data
        assert "redis" in data
        assert "version" in data
        assert "timestamp" in data

    async def test_health_status_values(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/health")).json()
        assert data["status"] in ("healthy", "degraded", "unhealthy")
        assert data["database"] in ("connected", "disconnected", "degraded")
        assert data["redis"] in ("connected", "disconnected", "degraded")

    async def test_health_returns_request_id_header(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/health")
        assert "x-request-id" in response.headers

    async def test_health_returns_process_time_header(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/health")
        assert "x-process-time" in response.headers


# ─────────────────────────────────────────────────────────────────────────────
# GET /version
# ─────────────────────────────────────────────────────────────────────────────

class TestVersion:
    async def test_version_returns_200(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/version")
        assert response.status_code == 200

    async def test_version_schema(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/version")).json()
        assert "name" in data
        assert "version" in data
        assert "environment" in data
        assert "python_version" in data
        assert "platform" in data
        assert "phase" in data

    async def test_version_matches_app_version(self, async_client: AsyncClient) -> None:
        from app.core.config import get_settings
        data = (await async_client.get("/version")).json()
        assert data["version"] == get_settings().app_version

    async def test_version_phase_label(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/version")).json()
        assert "Phase 2" in data["phase"]


# ─────────────────────────────────────────────────────────────────────────────
# 404 Handling
# ─────────────────────────────────────────────────────────────────────────────

class TestNotFound:
    async def test_unknown_route_returns_404(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/nonexistent-route")
        assert response.status_code == 404
