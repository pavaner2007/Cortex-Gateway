"""
Cortex Gateway – Google Gemini Provider Adapter (Phase 2)

Translates Cortex request/response format to/from the Google Gemini API.
Uses the Gemini generateContent REST endpoint via httpx.AsyncClient.

Key mapping differences from OpenAI format:
  - system role -> systemInstruction (top-level field, not in contents)
  - contents: [{role: "user"|"model", parts: [{text: "..."}]}]
  - "assistant" role maps to "model" in Gemini
  - usage: usageMetadata.{promptTokenCount, candidatesTokenCount, totalTokenCount}
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
    ChatMessage,
    ChatResponseMessage,
    CompletionMetadata,
    UsageInfo,
)
from app.schemas.providers import ModelInfo

logger = get_logger(__name__)

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com"

_GEMINI_KNOWN_MODELS: list[ModelInfo] = [
    ModelInfo(
        id="gemini-1.5-flash",
        name="Gemini 1.5 Flash",
        description="Fast and versatile multimodal model",
        context_window=1048576,
    ),
    ModelInfo(
        id="gemini-1.5-pro",
        name="Gemini 1.5 Pro",
        description="Mid-size multimodal model for complex reasoning",
        context_window=2097152,
    ),
    ModelInfo(
        id="gemini-2.0-flash",
        name="Gemini 2.0 Flash",
        description="Next-generation speed and performance",
        context_window=1048576,
    ),
]


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider adapter.

    Calls the Gemini generateContent REST endpoint using httpx.
    Handles the translation between Cortex's OpenAI-style messages and
    Gemini's content format, including system instruction handling.
    """

    def __init__(self, settings: object) -> None:
        self._api_key: str = getattr(settings, "gemini_api_key", "")
        self._default_model: str = getattr(settings, "gemini_default_model", "gemini-1.5-flash")
        self._timeout: int = getattr(settings, "provider_timeout_seconds", 30)
        self._client: httpx.AsyncClient | None = None

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def is_enabled(self) -> bool:
        return bool(self._api_key)

    @property
    def default_model(self) -> str:
        return self._default_model

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=_GEMINI_BASE_URL,
                timeout=httpx.Timeout(self._timeout),
            )
        return self._client

    def _build_payload(self, request: ChatCompletionRequest) -> tuple[str, dict]:
        """Build the Gemini API URL path and request payload.

        Returns:
            (model_id, payload_dict)
        """
        model_id = request.model or self._default_model

        # Separate system messages from conversation messages
        system_parts: list[str] = []
        conversation: list[ChatMessage] = []
        for msg in request.messages:
            if msg.role == "system":
                system_parts.append(msg.content)
            else:
                conversation.append(msg)

        # Map Cortex roles to Gemini roles
        # "user" -> "user", "assistant" -> "model"
        contents = []
        for msg in conversation:
            gemini_role = "model" if msg.role == "assistant" else "user"
            contents.append({"role": gemini_role, "parts": [{"text": msg.content}]})

        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
            },
        }

        if request.max_tokens is not None:
            payload["generationConfig"]["maxOutputTokens"] = request.max_tokens
        if request.top_p is not None:
            payload["generationConfig"]["topP"] = request.top_p
        if request.stop is not None:
            payload["generationConfig"]["stopSequences"] = request.stop

        # System instruction is a top-level field, not part of contents
        if system_parts:
            payload["systemInstruction"] = {
                "parts": [{"text": "\n".join(system_parts)}]
            }

        return model_id, payload

    def _normalize_response(
        self,
        raw: dict,
        model_id: str,
        request_id: str,
        latency_ms: float,
    ) -> ChatCompletionResponse:
        """Translate raw Gemini response to ChatCompletionResponse."""
        candidates = raw.get("candidates", [])
        choices: list[ChatCompletionChoice] = []

        for i, candidate in enumerate(candidates):
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            finish_reason_raw = candidate.get("finishReason", "STOP")
            # Map Gemini finish reasons to OpenAI-style
            finish_reason_map = {
                "STOP": "stop",
                "MAX_TOKENS": "length",
                "SAFETY": "content_filter",
                "RECITATION": "content_filter",
                "OTHER": "stop",
            }
            finish_reason = finish_reason_map.get(finish_reason_raw, "stop")
            choices.append(
                ChatCompletionChoice(
                    index=i,
                    message=ChatResponseMessage(role="assistant", content=text),
                    finish_reason=finish_reason,
                )
            )

        # Gemini usage metadata uses different field names
        usage_meta = raw.get("usageMetadata", {})
        usage = UsageInfo(
            prompt_tokens=usage_meta.get("promptTokenCount"),
            completion_tokens=usage_meta.get("candidatesTokenCount"),
            total_tokens=usage_meta.get("totalTokenCount"),
        )

        return ChatCompletionResponse(
            id=f"ctx_{uuid.uuid4().hex[:8]}",
            provider=self.name,
            model=model_id,
            choices=choices,
            usage=usage,
            metadata=CompletionMetadata(request_id=request_id, latency_ms=latency_ms),
        )

    def _handle_error(self, response: httpx.Response, model_id: str) -> None:
        status = response.status_code
        if status in (401, 403):
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
            raise InvalidModelError(self.name, model_id)
        raise ProviderError(self.name, f"Gemini returned HTTP {status}: {response.text[:200]}")

    async def chat(
        self,
        request: ChatCompletionRequest,
        request_id: str,
    ) -> ChatCompletionResponse:
        client = self._get_client()
        model_id, payload = self._build_payload(request)

        # Gemini endpoint: /v1beta/models/{model}:generateContent?key={api_key}
        endpoint = f"/v1beta/models/{model_id}:generateContent"

        logger.info(
            f"Gemini request | request_id={request_id} model={model_id} "
            f"messages={len(request.messages)}"
        )

        start = time.perf_counter()
        try:
            response = await client.post(
                endpoint,
                json=payload,
                params={"key": self._api_key},
            )
        except httpx.TimeoutException:
            raise ProviderTimeoutError(self.name)
        except httpx.RequestError as exc:
            raise ProviderError(self.name, f"Network error contacting Gemini: {exc}") from exc

        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        if response.status_code != 200:
            logger.warning(
                f"Gemini error | request_id={request_id} status={response.status_code} "
                f"latency_ms={latency_ms}"
            )
            self._handle_error(response, model_id)

        logger.info(
            f"Gemini success | request_id={request_id} model={model_id} "
            f"latency_ms={latency_ms}"
        )

        return self._normalize_response(response.json(), model_id, request_id, latency_ms)

    async def health_check(self) -> bool:
        if not self.is_enabled:
            return False
        try:
            client = self._get_client()
            response = await client.get(
                f"/v1beta/models/{self._default_model}",
                params={"key": self._api_key},
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[ModelInfo]:
        """Return Gemini model list. Uses known models as Gemini listing requires auth."""
        return _GEMINI_KNOWN_MODELS
