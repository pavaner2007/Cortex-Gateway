"""
Cortex Gateway – Provider Discovery Schemas (Phase 2)

Pydantic models for the provider and model discovery APIs.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Provider Schemas
# ─────────────────────────────────────────────────────────────────────────────


class ProviderInfo(BaseModel):
    """Summary information about a registered provider."""

    name: str = Field(description="Provider identifier (e.g. 'groq', 'gemini', 'openai')")
    enabled: bool = Field(description="Whether this provider is configured and available")
    capabilities: list[str] = Field(
        default_factory=lambda: ["chat_completions"],
        description="Supported capabilities",
    )


class ProvidersListResponse(BaseModel):
    """Response for GET /api/v1/providers."""

    providers: list[ProviderInfo]

    model_config = {
        "json_schema_extra": {
            "example": {
                "providers": [
                    {"name": "groq", "enabled": True, "capabilities": ["chat_completions"]},
                    {"name": "gemini", "enabled": True, "capabilities": ["chat_completions"]},
                    {"name": "openai", "enabled": False, "capabilities": ["chat_completions"]},
                ]
            }
        }
    }


class ProviderDetailResponse(BaseModel):
    """Detailed response for GET /api/v1/providers/{provider}."""

    name: str = Field(description="Provider identifier")
    enabled: bool = Field(description="Whether the provider is currently active")
    status: str = Field(description="Operational status ('active' | 'disabled' | 'unknown')")
    capabilities: list[str] = Field(description="Supported capabilities")
    default_model: str | None = Field(default=None, description="Default model for this provider")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "groq",
                "enabled": True,
                "status": "active",
                "capabilities": ["chat_completions"],
                "default_model": "llama-3.3-70b-versatile",
            }
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# Model Schemas
# ─────────────────────────────────────────────────────────────────────────────


class ModelInfo(BaseModel):
    """Information about a single model offered by a provider."""

    id: str = Field(description="Model identifier used in API requests")
    name: str = Field(description="Human-readable model name")
    description: str | None = Field(default=None, description="Model description")
    context_window: int | None = Field(default=None, description="Maximum context window in tokens")


class ModelsListResponse(BaseModel):
    """Response for GET /api/v1/providers/{provider}/models."""

    provider: str = Field(description="Provider identifier")
    models: list[ModelInfo] = Field(description="Available models for this provider")

    model_config = {
        "json_schema_extra": {
            "example": {
                "provider": "groq",
                "models": [
                    {
                        "id": "llama-3.3-70b-versatile",
                        "name": "LLaMA 3.3 70B Versatile",
                        "description": "Meta's LLaMA 3.3 70B model optimized for versatile tasks",
                        "context_window": 131072,
                    }
                ],
            }
        }
    }
