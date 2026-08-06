"""
Cortex Gateway – Chat Completions API Tests (Phase 2)

Tests for POST /api/v1/chat/completions covering:
  - Valid requests to all providers
  - Invalid/disabled/unconfigured providers
  - Malformed request payloads
  - Provider error normalization
  - Request ID propagation
  - Latency metadata presence
  - Token usage normalization

All tests use mocked providers — no real API keys or credits required.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.core.exceptions import (
    InvalidProviderError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.providers.registry import ProviderRegistry
from app.schemas.chat import (
    ChatCompletionChoice,
    ChatCompletionResponse,
    ChatResponseMessage,
    CompletionMetadata,
    UsageInfo,
)

pytestmark = pytest.mark.anyio

CHAT_URL = "/api/v1/chat/completions"

VALID_GROQ_PAYLOAD = {
    "provider": "groq",
    "model": "groq-default-model",
    "messages": [{"role": "user", "content": "Say Hello from Cortex Gateway."}],
}

VALID_GEMINI_PAYLOAD = {
    "provider": "gemini",
    "model": "gemini-default-model",
    "messages": [{"role": "user", "content": "Say Hello from Cortex Gateway."}],
}


# ─────────────────────────────────────────────────────────────────────────────
# Valid Requests
# ─────────────────────────────────────────────────────────────────────────────

class TestChatCompletionsValid:
    async def test_groq_returns_200(self, async_client: AsyncClient) -> None:
        response = await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)
        assert response.status_code == 200

    async def test_gemini_returns_200(self, async_client: AsyncClient) -> None:
        response = await async_client.post(CHAT_URL, json=VALID_GEMINI_PAYLOAD)
        assert response.status_code == 200

    async def test_response_schema_shape(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)).json()
        assert "id" in data
        assert "object" in data
        assert "provider" in data
        assert "model" in data
        assert "choices" in data
        assert "usage" in data
        assert "metadata" in data

    async def test_response_object_type(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)).json()
        assert data["object"] == "chat.completion"

    async def test_response_provider_matches_request(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)).json()
        assert data["provider"] == "groq"

    async def test_response_gemini_provider(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GEMINI_PAYLOAD)).json()
        assert data["provider"] == "gemini"

    async def test_choices_not_empty(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)).json()
        assert len(data["choices"]) >= 1

    async def test_choice_message_role(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)).json()
        assert data["choices"][0]["message"]["role"] == "assistant"

    async def test_choice_message_content_non_empty(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)).json()
        assert data["choices"][0]["message"]["content"] != ""

    async def test_usage_fields_present(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)).json()
        usage = data["usage"]
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert "total_tokens" in usage

    async def test_metadata_latency_ms_present(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)).json()
        assert "latency_ms" in data["metadata"]
        assert isinstance(data["metadata"]["latency_ms"], float)

    async def test_metadata_request_id_present(self, async_client: AsyncClient) -> None:
        data = (await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)).json()
        assert "request_id" in data["metadata"]
        assert data["metadata"]["request_id"] is not None

    async def test_request_id_header_in_response(self, async_client: AsyncClient) -> None:
        response = await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)
        assert "x-request-id" in response.headers

    async def test_with_system_message(self, async_client: AsyncClient) -> None:
        payload = {
            "provider": "groq",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
            ],
        }
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 200

    async def test_without_provider_uses_default(self, async_client: AsyncClient) -> None:
        payload = {"messages": [{"role": "user", "content": "Hello"}]}
        response = await async_client.post(CHAT_URL, json=payload)
        # Default provider is "groq" (set in test app), should succeed
        assert response.status_code == 200

    async def test_with_temperature(self, async_client: AsyncClient) -> None:
        payload = {**VALID_GROQ_PAYLOAD, "temperature": 0.9}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 200

    async def test_with_max_tokens(self, async_client: AsyncClient) -> None:
        payload = {**VALID_GROQ_PAYLOAD, "max_tokens": 100}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# Invalid Provider
# ─────────────────────────────────────────────────────────────────────────────

class TestChatCompletionsInvalidProvider:
    async def test_unknown_provider_returns_404(self, async_client: AsyncClient) -> None:
        payload = {**VALID_GROQ_PAYLOAD, "provider": "nonexistent"}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 404

    async def test_unknown_provider_error_code(self, async_client: AsyncClient) -> None:
        payload = {**VALID_GROQ_PAYLOAD, "provider": "nonexistent"}
        data = (await async_client.post(CHAT_URL, json=payload)).json()
        assert data["error"] == "INVALID_PROVIDER"

    async def test_disabled_provider_returns_503(
        self, async_client: AsyncClient, test_app
    ) -> None:
        """A registered-but-disabled provider should return 503."""
        from tests.conftest import MockProvider
        # Temporarily register a disabled provider
        test_app.state.provider_registry._providers["disabled_test"] = MockProvider(
            "disabled_test", enabled=False
        )
        try:
            payload = {**VALID_GROQ_PAYLOAD, "provider": "disabled_test"}
            response = await async_client.post(CHAT_URL, json=payload)
            assert response.status_code == 503
        finally:
            del test_app.state.provider_registry._providers["disabled_test"]

    async def test_disabled_provider_error_code(
        self, async_client: AsyncClient, test_app
    ) -> None:
        from tests.conftest import MockProvider
        test_app.state.provider_registry._providers["disabled_test2"] = MockProvider(
            "disabled_test2", enabled=False
        )
        try:
            payload = {**VALID_GROQ_PAYLOAD, "provider": "disabled_test2"}
            data = (await async_client.post(CHAT_URL, json=payload)).json()
            assert data["error"] == "PROVIDER_UNAVAILABLE"
        finally:
            del test_app.state.provider_registry._providers["disabled_test2"]


# ─────────────────────────────────────────────────────────────────────────────
# Validation Errors
# ─────────────────────────────────────────────────────────────────────────────

class TestChatCompletionsValidation:
    async def test_empty_messages_returns_422(self, async_client: AsyncClient) -> None:
        payload = {"provider": "groq", "messages": []}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 422

    async def test_missing_messages_returns_422(self, async_client: AsyncClient) -> None:
        payload = {"provider": "groq"}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 422

    async def test_invalid_role_returns_422(self, async_client: AsyncClient) -> None:
        payload = {"provider": "groq", "messages": [{"role": "invalid", "content": "Hi"}]}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 422

    async def test_temperature_too_high_returns_422(self, async_client: AsyncClient) -> None:
        payload = {**VALID_GROQ_PAYLOAD, "temperature": 3.0}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 422

    async def test_temperature_negative_returns_422(self, async_client: AsyncClient) -> None:
        payload = {**VALID_GROQ_PAYLOAD, "temperature": -0.1}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 422

    async def test_max_tokens_zero_returns_422(self, async_client: AsyncClient) -> None:
        payload = {**VALID_GROQ_PAYLOAD, "max_tokens": 0}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 422

    async def test_empty_message_content_returns_422(self, async_client: AsyncClient) -> None:
        payload = {"provider": "groq", "messages": [{"role": "user", "content": ""}]}
        response = await async_client.post(CHAT_URL, json=payload)
        assert response.status_code == 422

    async def test_empty_body_returns_422(self, async_client: AsyncClient) -> None:
        response = await async_client.post(CHAT_URL, json={})
        assert response.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# Provider Error Normalization (via injected exceptions)
# ─────────────────────────────────────────────────────────────────────────────

class TestProviderErrorNormalization:
    """Tests that verify provider errors are normalized to Cortex error format."""

    async def _post_with_mock_error(
        self, async_client: AsyncClient, test_app, exc: Exception
    ) -> dict:
        """Temporarily override the groq provider to raise exc, then post."""
        original_provider = test_app.state.provider_registry._providers["groq"]

        class ErrorProvider:
            name = "groq"
            is_enabled = True
            default_model = "groq-model"
            capabilities = ["chat_completions"]

            async def chat(self, request, request_id):
                raise exc

            async def health_check(self):
                return False

            async def list_models(self):
                return []

        test_app.state.provider_registry._providers["groq"] = ErrorProvider()
        try:
            response = await async_client.post(CHAT_URL, json=VALID_GROQ_PAYLOAD)
            return response
        finally:
            test_app.state.provider_registry._providers["groq"] = original_provider

    async def test_timeout_returns_504(self, async_client: AsyncClient, test_app) -> None:
        response = await self._post_with_mock_error(
            async_client, test_app, ProviderTimeoutError("groq")
        )
        assert response.status_code == 504

    async def test_timeout_error_code(self, async_client: AsyncClient, test_app) -> None:
        response = await self._post_with_mock_error(
            async_client, test_app, ProviderTimeoutError("groq")
        )
        assert response.json()["error"] == "PROVIDER_TIMEOUT"

    async def test_rate_limit_returns_429(self, async_client: AsyncClient, test_app) -> None:
        response = await self._post_with_mock_error(
            async_client, test_app, ProviderRateLimitError("groq")
        )
        assert response.status_code == 429

    async def test_rate_limit_error_code(self, async_client: AsyncClient, test_app) -> None:
        response = await self._post_with_mock_error(
            async_client, test_app, ProviderRateLimitError("groq")
        )
        assert response.json()["error"] == "PROVIDER_RATE_LIMITED"

    async def test_auth_error_returns_502(self, async_client: AsyncClient, test_app) -> None:
        response = await self._post_with_mock_error(
            async_client, test_app, ProviderAuthenticationError("groq")
        )
        assert response.status_code == 502

    async def test_auth_error_code(self, async_client: AsyncClient, test_app) -> None:
        response = await self._post_with_mock_error(
            async_client, test_app, ProviderAuthenticationError("groq")
        )
        assert response.json()["error"] == "PROVIDER_AUTH_ERROR"
