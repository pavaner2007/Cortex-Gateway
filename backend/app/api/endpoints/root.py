"""
Cortex Gateway – Root Endpoint

GET /

Returns project metadata — useful as a quick sanity check that the
service is running and provides links to documentation.
"""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.schemas.common import RootResponse

router = APIRouter()


@router.get(
    "/",
    response_model=RootResponse,
    summary="Project Information",
    description="Returns Cortex Gateway metadata including links to API documentation.",
)
async def root(request: Request) -> RootResponse:
    """Return project information and links to documentation."""
    settings = get_settings()
    base_url = str(request.base_url).rstrip("/")

    return RootResponse(
        name=settings.app_name,
        version=settings.app_version,
        description="Enterprise AI Gateway — route, observe, and control all your LLM traffic.",
        docs=f"{base_url}/docs",
        redoc=f"{base_url}/redoc",
        health=f"{base_url}/health",
        phase="Phase 2 – Unified Multi-Provider LLM Gateway",
    )
