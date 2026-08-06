"""
Cortex Gateway – Provider Registry (Phase 2)

Central registry that holds all registered LLM providers.
The ChatService and API endpoints interact with providers exclusively
through this registry — never by importing concrete adapters directly.

Design:
  - Single Responsibility: registers and retrieves providers
  - Open/Closed: add a new provider by registering it, not by modifying this class
  - Used as application-level state stored on app.state.provider_registry
"""

from __future__ import annotations

from app.core.exceptions import InvalidProviderError
from app.providers.base import BaseLLMProvider


class ProviderRegistry:
    """Centralized registry for LLM provider adapters.

    Usage:
        registry = ProviderRegistry()
        registry.register(GroqProvider(settings))
        registry.register(GeminiProvider(settings))

        provider = registry.get("groq")
        response = await provider.chat(request, request_id)
    """

    def __init__(self) -> None:
        self._providers: dict[str, BaseLLMProvider] = {}

    def register(self, provider: BaseLLMProvider) -> None:
        """Register a provider adapter.

        Args:
            provider: Concrete provider instance implementing BaseLLMProvider.
        """
        self._providers[provider.name] = provider

    def get(self, name: str) -> BaseLLMProvider:
        """Retrieve a provider by name.

        Args:
            name: Provider identifier (e.g. 'groq', 'gemini').

        Raises:
            InvalidProviderError: If the provider is not registered.
        """
        provider = self._providers.get(name)
        if provider is None:
            raise InvalidProviderError(name)
        return provider

    def has(self, name: str) -> bool:
        """Return True if a provider with the given name is registered."""
        return name in self._providers

    def list_all(self) -> list[BaseLLMProvider]:
        """Return all registered providers (enabled and disabled)."""
        return list(self._providers.values())

    def list_enabled(self) -> list[BaseLLMProvider]:
        """Return only providers that are currently enabled."""
        return [p for p in self._providers.values() if p.is_enabled]


def build_registry(settings: object) -> ProviderRegistry:
    """Factory that constructs and populates the ProviderRegistry.

    Imports concrete provider classes here to keep the registry itself
    independent of any provider implementation.

    Args:
        settings: Application settings instance from get_settings().

    Returns:
        Fully populated ProviderRegistry.
    """
    from app.providers.gemini_provider import GeminiProvider
    from app.providers.groq_provider import GroqProvider

    registry = ProviderRegistry()
    registry.register(GroqProvider(settings))
    registry.register(GeminiProvider(settings))
    return registry
