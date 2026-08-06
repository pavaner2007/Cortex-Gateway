"""
Cortex Gateway – pytest Configuration & Fixtures

Provides:
  - async_client : HTTPX AsyncClient wired to the FastAPI test app
  - override_get_db : replaces real DB dependency with a test session
  - override_get_redis : replaces real Redis dependency with a mock
  - Phase 2: mock provider registry fixtures
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database.session import get_db
from app.main import create_app
from app.providers.registry import ProviderRegistry
from app.schemas.chat import (
    ChatCompletionChoice,
    ChatCompletionResponse,
    ChatResponseMessage,
    CompletionMetadata,
    UsageInfo,
)
from app.services.redis_client import get_redis


# ─────────────────────────────────────────────────────────────────────────────
# Infrastructure Mocks (Phase 1)
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
# Provider Mocks (Phase 2)
# ─────────────────────────────────────────────────────────────────────────────

def _make_chat_response(provider: str, model: str, request_id: str = "test-req-id") -> ChatCompletionResponse:
    """Build a canned ChatCompletionResponse for mocking."""
    return ChatCompletionResponse(
        id="ctx_test1234",
        provider=provider,
        model=model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatResponseMessage(role="assistant", content="Hello from Cortex Gateway."),
                finish_reason="stop",
            )
        ],
        usage=UsageInfo(prompt_tokens=10, completion_tokens=8, total_tokens=18),
        metadata=CompletionMetadata(request_id=request_id, latency_ms=123.4),
    )


class MockProvider:
    """Generic mock provider for testing."""

    def __init__(self, name: str, enabled: bool = True) -> None:
        self._name = name
        self._enabled = enabled
        self._default_model = f"{name}-default-model"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @property
    def default_model(self) -> str:
        return self._default_model

    @property
    def capabilities(self) -> list[str]:
        return ["chat_completions"]

    async def chat(self, request, request_id: str) -> ChatCompletionResponse:
        return _make_chat_response(self._name, request.model or self._default_model, request_id)

    async def health_check(self) -> bool:
        return self._enabled

    async def list_models(self):
        from app.schemas.providers import ModelInfo
        return [ModelInfo(id=f"{self._name}-model", name=f"{self._name} Model")]


def _build_mock_registry(
    groq_enabled: bool = True,
    gemini_enabled: bool = True,
    openai_enabled: bool = False,
) -> ProviderRegistry:
    """Build a ProviderRegistry populated with mock providers."""
    registry = ProviderRegistry()
    registry.register(MockProvider("groq", enabled=groq_enabled))
    registry.register(MockProvider("gemini", enabled=gemini_enabled))
    registry.register(MockProvider("openai", enabled=openai_enabled))
    return registry


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_app():
    """Create a test FastAPI application instance."""
    app = create_app()

    # Override Phase 1 infrastructure dependencies with mocks
    async def _mock_db() -> AsyncGenerator:
        yield MockDBSession()

    async def _mock_redis() -> MockRedis:
        return MockRedis()

    app.dependency_overrides[get_db] = _mock_db
    app.dependency_overrides[get_redis] = _mock_redis

    # Inject mock provider registry (all enabled except OpenAI)
    app.state.provider_registry = _build_mock_registry()

    return app


@pytest_asyncio.fixture(scope="session")
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client targeting the test application."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.fixture
def anyio_backend() -> str:
    """Specify the backend for anyio tests."""
    return "asyncio"
