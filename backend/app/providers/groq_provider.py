"""
Cortex Gateway – Groq Provider Adapter (Phase 2)

Translates Cortex request/response format to/from the Groq API.
Groq follows the OpenAI Chat Completions API format, which simplifies mapping.

All Groq-specific structures are isolated within this module.
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


# Curated list of Groq-hosted models as of Phase 2.
# Groq provides a /models endpoint — we call it dynamically in list_models().
_GROQ_KNOWN_MODELS: list[ModelInfo] = [
    ModelInfo(
        id="llama-3.3-70b-versatile",
        name="LLaMA 3.3 70B Versatile",
        description="Meta's LLaMA 3.3 70B optimized for versatile tasks",
        context_window=131072,
    ),
    ModelInfo(
        id="llama-3.1-8b-instant",
        name="LLaMA 3.1 8B Instant",
        description="Fast, lightweight LLaMA 3.1 8B model",
        context_window=131072,
    ),
    ModelInfo(
        id="mixtral-8x7b-32768",
        name="Mixtral 8x7B",
        description="Mistral AI's Mixtral 8x7B mixture-of-experts model",
        context_window=32768,
    ),
    ModelInfo(
        id="gemma2-9b-it",
        name="Gemma2 9B IT",
        description="Google's Gemma2 9B instruction-tuned model",
        context_window=8192,
    ),
]


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider adapter.

    Uses httpx.AsyncClient with a shared connection pool.
    The client is created once per provider instance (application lifetime).
    """

    def __init__(self, settings: object) -> None:
        self._api_key: str = getattr(settings, "groq_api_key", "")
        self._base_url: str = getattr(settings, "groq_base_url", "https://api.groq.com/openai/v1")
        self._default_model: str = getattr(settings, "groq_default_model", "llama-3.3-70b-versatile")
        self._timeout: int = getattr(settings, "provider_timeout_seconds", 30)
        self._client: httpx.AsyncClient | None = None

    @property
    def name(self) -> str:
        return "groq"

    @property
    def is_enabled(self) -> bool:
        return bool(self._api_key)

    @property
    def default_model(self) -> str:
        return self._default_model

    def _get_client(self) -> httpx.AsyncClient:
        """Lazily create a shared async HTTP client."""
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
        """Convert Cortex request to Groq-compatible payload."""
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
        """Translate a raw Groq JSON response to ChatCompletionResponse."""
        choices = raw.get("choices", [])
        normalized_choices = []
        for choice in choices:
            msg = choice.get("message", {})
            normalized_choices.append(
                ChatCompletionChoice(
                    index=choice.get("index", 0),
                    message=ChatResponseMessage(
                        role="assistant",
                        content=msg.get("content", ""),
                    ),
                    finish_reason=choice.get("finish_reason"),
                )
            )

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
        """Map HTTP error codes to Cortex provider exceptions."""
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
        raise ProviderError(self.name, f"Groq returned HTTP {status}: {response.text[:200]}")

    async def chat(
        self,
        request: ChatCompletionRequest,
        request_id: str,
    ) -> ChatCompletionResponse:
        client = self._get_client()
        payload = self._build_payload(request)
        model_used = payload["model"]

        logger.info(
            f"Groq request | request_id={request_id} model={model_used} "
            f"messages={len(request.messages)}"
        )

        start = time.perf_counter()
        try:
            response = await client.post("/chat/completions", json=payload)
        except httpx.TimeoutException:
            raise ProviderTimeoutError(self.name)
        except httpx.RequestError as exc:
            raise ProviderError(self.name, f"Network error contacting Groq: {exc}") from exc

        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        if response.status_code != 200:
            logger.warning(
                f"Groq error | request_id={request_id} status={response.status_code} "
                f"latency_ms={latency_ms}"
            )
            self._handle_error(response)

        logger.info(
            f"Groq success | request_id={request_id} model={model_used} "
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
            return _GROQ_KNOWN_MODELS
        try:
            client = self._get_client()
            response = await client.get("/models", timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                return [
                    ModelInfo(
                        id=m.get("id", ""),
                        name=m.get("id", ""),
                        description=None,
                        context_window=m.get("context_window"),
                    )
                    for m in data
                    if m.get("id")
                ]
        except Exception:
            pass
        return _GROQ_KNOWN_MODELS
