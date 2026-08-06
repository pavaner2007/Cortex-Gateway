"""
Cortex Gateway – Provider Discovery Endpoints (Phase 2)

GET /api/v1/providers
GET /api/v1/providers/{provider}
GET /api/v1/providers/{provider}/models

Safe provider metadata APIs — never expose API keys or secrets.
"""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from app.core.exceptions import InvalidProviderError
from app.providers.registry import ProviderRegistry
from app.schemas.common import ErrorResponse
from app.schemas.providers import (
    ModelsListResponse,
    ProviderDetailResponse,
    ProviderInfo,
    ProvidersListResponse,
)

router = APIRouter()


def _get_registry(request: Request) -> ProviderRegistry:
    return request.app.state.provider_registry


@router.get(
    "/providers",
    response_model=ProvidersListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Providers",
    description=(
        "Returns all registered LLM providers and their enabled status.\n\n"
        "Providers with no configured API key will appear as `enabled: false`."
    ),
)
async def list_providers(request: Request) -> ProvidersListResponse:
    """List all registered providers."""
    registry = _get_registry(request)
    return ProvidersListResponse(
        providers=[
            ProviderInfo(
                name=p.name,
                enabled=p.is_enabled,
                capabilities=p.capabilities,
            )
            for p in registry.list_all()
        ]
    )


@router.get(
    "/providers/{provider}",
    response_model=ProviderDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Provider Details",
    description="Returns detailed metadata about a specific provider.",
    responses={404: {"model": ErrorResponse, "description": "Provider not found"}},
)
async def get_provider(provider: str, request: Request) -> ProviderDetailResponse:
    """Return detail for a single provider."""
    registry = _get_registry(request)
    p = registry.get(provider)  # raises InvalidProviderError if not found
    status_str = "active" if p.is_enabled else "disabled"
    return ProviderDetailResponse(
        name=p.name,
        enabled=p.is_enabled,
        status=status_str,
        capabilities=p.capabilities,
        default_model=p.default_model if p.is_enabled else None,
    )


@router.get(
    "/providers/{provider}/models",
    response_model=ModelsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Provider Models",
    description=(
        "Returns models available for the specified provider.\n\n"
        "Where possible, this calls the provider's model discovery endpoint.\n"
        "Falls back to a curated list when dynamic discovery is unavailable."
    ),
    responses={404: {"model": ErrorResponse, "description": "Provider not found"}},
)
async def list_provider_models(provider: str, request: Request) -> ModelsListResponse:
    """List available models for a provider."""
    registry = _get_registry(request)
    p = registry.get(provider)  # raises InvalidProviderError if not found
    models = await p.list_models()
    return ModelsListResponse(provider=p.name, models=models)
