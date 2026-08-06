"""
Cortex Gateway – Provider Discovery API Tests (Phase 2)

Tests for:
  GET /api/v1/providers
  GET /api/v1/providers/{provider}
  GET /api/v1/providers/{provider}/models
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


class TestProvidersListAPI:
    async def test_list_providers_returns_200(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/providers")
        assert response.status_code == 200

    async def test_list_providers_schema(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers")).json()
        assert "providers" in data
        assert isinstance(data["providers"], list)

    async def test_list_providers_contains_registered_providers(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers")).json()
        names = [p["name"] for p in data["providers"]]
        assert "groq" in names
        assert "gemini" in names
        assert "openai" in names

    async def test_provider_has_enabled_field(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers")).json()
        for provider in data["providers"]:
            assert "enabled" in provider
            assert isinstance(provider["enabled"], bool)

    async def test_provider_has_capabilities_field(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers")).json()
        for provider in data["providers"]:
            assert "capabilities" in provider

    async def test_groq_and_gemini_enabled(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers")).json()
        provider_map = {p["name"]: p for p in data["providers"]}
        assert provider_map["groq"]["enabled"] is True
        assert provider_map["gemini"]["enabled"] is True

    async def test_openai_disabled(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers")).json()
        provider_map = {p["name"]: p for p in data["providers"]}
        assert provider_map["openai"]["enabled"] is False


class TestProviderDetailAPI:
    async def test_groq_detail_returns_200(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/providers/groq")
        assert response.status_code == 200

    async def test_detail_schema(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/groq")).json()
        assert "name" in data
        assert "enabled" in data
        assert "status" in data
        assert "capabilities" in data

    async def test_groq_detail_name(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/groq")).json()
        assert data["name"] == "groq"

    async def test_groq_detail_enabled(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/groq")).json()
        assert data["enabled"] is True

    async def test_groq_detail_status_active(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/groq")).json()
        assert data["status"] == "active"

    async def test_openai_detail_disabled(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/openai")).json()
        assert data["enabled"] is False
        assert data["status"] == "disabled"

    async def test_unknown_provider_returns_404(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/providers/nonexistent")
        assert response.status_code == 404

    async def test_unknown_provider_error_code(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/nonexistent")).json()
        assert data["error"] == "INVALID_PROVIDER"


class TestProviderModelsAPI:
    async def test_models_returns_200(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/providers/groq/models")
        assert response.status_code == 200

    async def test_models_schema(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/groq/models")).json()
        assert "provider" in data
        assert "models" in data
        assert isinstance(data["models"], list)

    async def test_models_provider_field(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/groq/models")).json()
        assert data["provider"] == "groq"

    async def test_models_list_not_empty(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/groq/models")).json()
        assert len(data["models"]) >= 1

    async def test_model_has_id(self, async_client: AsyncClient) -> None:
        data = (await async_client.get("/api/v1/providers/groq/models")).json()
        for model in data["models"]:
            assert "id" in model

    async def test_gemini_models(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/providers/gemini/models")
        assert response.status_code == 200

    async def test_unknown_provider_models_returns_404(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/providers/nonexistent/models")
        assert response.status_code == 404
