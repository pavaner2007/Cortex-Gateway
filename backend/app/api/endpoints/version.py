"""
Cortex Gateway – Version Endpoint

GET /version

Returns detailed version and runtime information.
Useful for deployment verification and support debugging.
"""

from __future__ import annotations

import platform
import sys

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import VersionResponse

router = APIRouter()


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Version Information",
    description="Returns application version, environment, and runtime details.",
)
async def version() -> VersionResponse:
    """Return version and runtime metadata."""
    settings = get_settings()

    return VersionResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        python_version=sys.version.split()[0],
        platform=platform.system().lower(),
    )
