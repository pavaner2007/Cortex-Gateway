"""
Cortex Gateway – ProviderRegistry Unit Tests (Phase 2)

Tests for the ProviderRegistry class covering:
  - Registration
  - Retrieval by name
  - Unknown provider handling
  - Listing all vs. enabled providers
  - build_registry factory with Groq and Gemini (no OpenAI)
"""

from __future__ import annotations

import pytest

from app.core.exceptions import InvalidProviderError
from app.providers.registry import ProviderRegistry

pytestmark = pytest.mark.anyio


class MockSettingsNoKeys:
    """Settings object with no API keys configured (Groq + Gemini only)."""
    groq_api_key = ""
    groq_base_url = "https://api.groq.com/openai/v1"
    groq_default_model = "llama-3.3-70b-versatile"
    gemini_api_key = ""
    gemini_default_model = "gemini-1.5-flash"
    default_provider = "groq"
    provider_timeout_seconds = 30


class SimpleProvider:
    """Minimal provider stub for registry tests."""

    def __init__(self, name: str, enabled: bool = True) -> None:
        self._name = name
        self._enabled = enabled

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @property
    def default_model(self) -> str:
        return "test-model"

    @property
    def capabilities(self) -> list[str]:
        return ["chat_completions"]


class TestProviderRegistry:
    def test_register_and_get(self) -> None:
        registry = ProviderRegistry()
        provider = SimpleProvider("groq")
        registry.register(provider)
        assert registry.get("groq") is provider

    def test_get_unknown_raises_invalid_provider_error(self) -> None:
        registry = ProviderRegistry()
        with pytest.raises(InvalidProviderError):
            registry.get("unknown")

    def test_has_returns_true_when_registered(self) -> None:
        registry = ProviderRegistry()
        registry.register(SimpleProvider("groq"))
        assert registry.has("groq") is True

    def test_has_returns_false_when_not_registered(self) -> None:
        registry = ProviderRegistry()
        assert registry.has("groq") is False

    def test_list_all_returns_all_providers(self) -> None:
        registry = ProviderRegistry()
        registry.register(SimpleProvider("groq", enabled=True))
        registry.register(SimpleProvider("gemini", enabled=False))
        assert len(registry.list_all()) == 2

    def test_list_enabled_filters_disabled(self) -> None:
        registry = ProviderRegistry()
        registry.register(SimpleProvider("groq", enabled=True))
        registry.register(SimpleProvider("gemini", enabled=False))
        enabled = registry.list_enabled()
        assert len(enabled) == 1
        assert enabled[0].name == "groq"

    def test_register_overwrites_existing(self) -> None:
        registry = ProviderRegistry()
        p1 = SimpleProvider("groq")
        p2 = SimpleProvider("groq")
        registry.register(p1)
        registry.register(p2)
        assert registry.get("groq") is p2

    def test_two_providers(self) -> None:
        registry = ProviderRegistry()
        for name in ["groq", "gemini"]:
            registry.register(SimpleProvider(name))
        assert len(registry.list_all()) == 2
        assert registry.has("groq")
        assert registry.has("gemini")
        assert not registry.has("openai")


class TestBuildRegistry:
    def test_build_registry_registers_two_providers(self) -> None:
        from app.providers.registry import build_registry
        registry = build_registry(MockSettingsNoKeys())
        names = {p.name for p in registry.list_all()}
        assert "groq" in names
        assert "gemini" in names
        assert "openai" not in names

    def test_build_registry_no_keys_all_disabled(self) -> None:
        from app.providers.registry import build_registry
        registry = build_registry(MockSettingsNoKeys())
        assert len(registry.list_enabled()) == 0

    def test_build_registry_with_groq_key_enables_groq(self) -> None:
        from app.providers.registry import build_registry

        class SettingsGroqEnabled(MockSettingsNoKeys):
            groq_api_key = "test-groq-key"

        registry = build_registry(SettingsGroqEnabled())
        assert registry.get("groq").is_enabled is True
        assert registry.get("gemini").is_enabled is False
        assert not registry.has("openai")

    def test_build_registry_with_gemini_key_enables_gemini(self) -> None:
        from app.providers.registry import build_registry

        class SettingsGeminiEnabled(MockSettingsNoKeys):
            gemini_api_key = "test-gemini-key"

        registry = build_registry(SettingsGeminiEnabled())
        assert registry.get("groq").is_enabled is False
        assert registry.get("gemini").is_enabled is True
