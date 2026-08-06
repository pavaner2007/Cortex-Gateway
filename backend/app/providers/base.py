"""
Cortex Gateway – Base LLM Provider Interface (Phase 2)

Defines the abstract contract that every provider adapter must fulfil.
All concrete adapters (Groq, Gemini, OpenAI, ...) extend BaseLLMProvider.

Design:
  - Open/Closed: add providers by creating new adapters, not modifying core logic
  - Dependency Inversion: ChatService depends on this abstraction, not concretions
  - Interface Segregation: methods are minimal and well-scoped
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.schemas.providers import ModelInfo


class BaseLLMProvider(ABC):
    """Abstract base for all LLM provider adapters.

    Every concrete implementation must be:
    - Fully async (no blocking I/O)
    - Stateless with respect to individual requests
    - Self-contained (provider-specific logic stays inside the adapter)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this provider (e.g. 'groq', 'gemini')."""
        ...

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """True when the provider has a valid API key and can accept requests."""
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        """The model used when the request does not specify one."""
        ...

    @property
    def capabilities(self) -> list[str]:
        """Capabilities supported by this provider."""
        return ["chat_completions"]

    @abstractmethod
    async def chat(
        self,
        request: ChatCompletionRequest,
        request_id: str,
    ) -> ChatCompletionResponse:
        """Execute a chat completion request.

        Args:
            request:    Validated Cortex chat request.
            request_id: Trace ID from the gateway middleware.

        Returns:
            Normalized ChatCompletionResponse.

        Raises:
            ProviderError: On any provider-side failure.
            ProviderTimeoutError: On timeout.
            ProviderAuthenticationError: On 401/403 from provider.
            ProviderRateLimitError: On 429 from provider.
            InvalidModelError: When the model is rejected.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Perform a lightweight connectivity check against the provider.

        Returns True if the provider is reachable, False otherwise.
        Should not raise — return False on any failure.
        """
        ...

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """Return the models available for this provider.

        May call the provider's model listing endpoint, or return a
        static curated list when dynamic discovery is unavailable.
        """
        ...
