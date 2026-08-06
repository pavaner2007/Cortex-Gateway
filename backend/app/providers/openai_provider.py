"""
Cortex Gateway – OpenAI Provider Adapter (Phase 2)

Translates Cortex request/response format to/from the OpenAI Chat Completions API.
OpenAI uses the same format that Cortex is modelled on, making mapping straightforward.

Supports any OpenAI-compatible endpoint via OPENAI_BASE_URL, enabling use with
local models (Ollama, LM Studio, etc.) in future phases.
"""

from __future__ import annotations

import time
import uuid

import httpx

from app.core.exceptions import (
    InvalidModelError,
    InvalidProviderRequestError,
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from app.logging.logger import get_logger
from app.providers.base import BaseLLMProvider
from app.schemas.chat import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatResponseMessage,
    CompletionMetadata,
    UsageInfo,
)
from app.schemas.providers import ModelInfo

logger = get_logger(__name__)

_OPENAI_KNOWN_MODELS: list[ModelInfo] = [
    ModelInfo(
        id="gpt-4o",
        name="GPT-4o",
        description="Most capable GPT-4 model with multimodal support",
        context_window=128000,
    ),
    ModelInfo(
        id="gpt-4o-mini",
        name="GPT-4o Mini",
        description="Affordable, fast, and capable smaller model",
        context_window=128000,
    ),
    ModelInfo(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        description="High-intelligence GPT-4 with large context",
        context_window=128000,
    ),
    ModelInfo(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        description="Fast, inexpensive model for simple tasks",
        context_window=16385,
    ),
]


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider adapter.

    The Cortex request format is modelled on the OpenAI API,
    so mapping is nearly 1:1. Supports custom base URLs for
    OpenAI-compatible endpoints.
    """

    def __init__(self, settings: object) -> None:
        self._api_key: str = getattr(settings, "openai_api_key", "")
        self._base_url: str = getattr(settings, "openai_base_url", "https://api.openai.com/v1")
        self._default_model: str = getattr(settings, "openai_default_model", "gpt-4o-mini")
        self._timeout: int = getattr(settings, "provider_timeout_seconds", 30)
        self._client: httpx.AsyncClient | None = None

    @property
    def name(self) -> str:
        return "openai"

    @property
    def is_enabled(self) -> bool:
        return bool(self._api_key)

    @property
    def default_model(self) -> str:
        return self._default_model

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(self._timeout),
            )
        return self._client

    def _build_payload(self, request: ChatCompletionRequest) -> dict:
        payload: dict = {
            "model": request.model or self._default_model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.stop is not None:
            payload["stop"] = request.stop
        return payload

    def _normalize_response(
        self,
        raw: dict,
        request: ChatCompletionRequest,
        request_id: str,
        latency_ms: float,
    ) -> ChatCompletionResponse:
        choices = raw.get("choices", [])
        normalized_choices = [
            ChatCompletionChoice(
                index=c.get("index", 0),
                message=ChatResponseMessage(
                    role="assistant",
                    content=c.get("message", {}).get("content", ""),
                ),
                finish_reason=c.get("finish_reason"),
            )
            for c in choices
        ]

        raw_usage = raw.get("usage", {})
        usage = UsageInfo(
            prompt_tokens=raw_usage.get("prompt_tokens"),
            completion_tokens=raw_usage.get("completion_tokens"),
            total_tokens=raw_usage.get("total_tokens"),
        )

        return ChatCompletionResponse(
            id=f"ctx_{uuid.uuid4().hex[:8]}",
            provider=self.name,
            model=raw.get("model", request.model or self._default_model),
            choices=normalized_choices,
            usage=usage,
            metadata=CompletionMetadata(request_id=request_id, latency_ms=latency_ms),
        )

    def _handle_error(self, response: httpx.Response) -> None:
        status = response.status_code
        if status == 401:
            raise ProviderAuthenticationError(self.name)
        if status == 429:
            raise ProviderRateLimitError(self.name)
        if status == 400:
            try:
                detail = response.json().get("error", {}).get("message", response.text)
            except Exception:
                detail = response.text
            raise InvalidProviderRequestError(self.name, detail)
        if status == 404:
            raise InvalidModelError(self.name, "unknown")
        raise ProviderError(self.name, f"OpenAI returned HTTP {status}: {response.text[:200]}")

    async def chat(
        self,
        request: ChatCompletionRequest,
        request_id: str,
    ) -> ChatCompletionResponse:
        client = self._get_client()
        payload = self._build_payload(request)
        model_used = payload["model"]

        logger.info(
            f"OpenAI request | request_id={request_id} model={model_used} "
            f"messages={len(request.messages)}"
        )

        start = time.perf_counter()
        try:
            response = await client.post("/chat/completions", json=payload)
        except httpx.TimeoutException:
            raise ProviderTimeoutError(self.name)
        except httpx.RequestError as exc:
            raise ProviderError(self.name, f"Network error contacting OpenAI: {exc}") from exc

        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        if response.status_code != 200:
            logger.warning(
                f"OpenAI error | request_id={request_id} status={response.status_code} "
                f"latency_ms={latency_ms}"
            )
            self._handle_error(response)

        logger.info(
            f"OpenAI success | request_id={request_id} model={model_used} "
            f"latency_ms={latency_ms}"
        )

        return self._normalize_response(response.json(), request, request_id, latency_ms)

    async def health_check(self) -> bool:
        if not self.is_enabled:
            return False
        try:
            client = self._get_client()
            response = await client.get("/models", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[ModelInfo]:
        """Attempt dynamic model discovery; fall back to curated list."""
        if not self.is_enabled:
            return _OPENAI_KNOWN_MODELS
        try:
            client = self._get_client()
            response = await client.get("/models", timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                # Filter to chat models only
                chat_models = [m for m in data if "gpt" in m.get("id", "").lower()]
                if chat_models:
                    return [
                        ModelInfo(
                            id=m["id"],
                            name=m["id"],
                            description=None,
                            context_window=None,
                        )
                        for m in chat_models[:20]  # cap at 20
                    ]
        except Exception:
            pass
        return _OPENAI_KNOWN_MODELS
