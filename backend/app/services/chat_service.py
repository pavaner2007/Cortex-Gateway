"""
Cortex Gateway – Chat Service (Phase 2)

Orchestration layer between the Chat API endpoint and the ProviderRegistry.
The ChatService is responsible for:
  1. Resolving the provider (explicit or default)
  2. Verifying the provider is enabled
  3. Delegating execution to the provider adapter
  4. Returning the normalized response

ChatService has no provider-specific logic. It only coordinates.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.core.exceptions import ProviderUnavailableError
from app.logging.logger import get_logger
from app.providers.registry import ProviderRegistry
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse

logger = get_logger(__name__)


class ChatService:
    """Orchestrates chat completion requests through the provider registry.

    Designed to be constructed once and reused. The ProviderRegistry is
    injected, keeping this service decoupled from specific adapters.
    """

    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    async def complete(
        self,
        request: ChatCompletionRequest,
        request_id: str,
    ) -> ChatCompletionResponse:
        """Execute a chat completion request end-to-end.

        Args:
            request:    Validated ChatCompletionRequest.
            request_id: Trace ID from the gateway middleware.

        Returns:
            Normalized ChatCompletionResponse.

        Raises:
            InvalidProviderError: If provider name is unknown.
            ProviderUnavailableError: If provider is disabled.
            ProviderError subclasses: On any upstream failure.
        """
        settings = get_settings()

        # Resolve provider name: explicit or configured default
        provider_name = request.provider or settings.default_provider

        logger.info(
            f"Chat request | request_id={request_id} provider={provider_name} "
            f"model={request.model or 'default'} messages={len(request.messages)}"
        )

        # Retrieve from registry (raises InvalidProviderError if unknown)
        provider = self._registry.get(provider_name)

        # Guard: provider registered but not configured
        if not provider.is_enabled:
            raise ProviderUnavailableError(provider_name)

        # Delegate to provider adapter
        response = await provider.chat(request, request_id)

        logger.info(
            f"Chat complete | request_id={request_id} provider={provider_name} "
            f"model={response.model} latency_ms={response.metadata.latency_ms}"
        )

        return response
