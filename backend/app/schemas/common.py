"""
Cortex Gateway – Shared Pydantic v2 Schemas

Contains response models shared across multiple endpoints:
  - HealthResponse   : /health
  - VersionResponse  : /version
  - RootResponse     : /
  - ErrorResponse    : All error payloads
"""

from __future__ import annotations

import platform
import sys
from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

ServiceStatus = Literal["connected", "disconnected", "degraded"]
OverallStatus = Literal["healthy", "degraded", "unhealthy"]


class HealthResponse(BaseModel):
    """Response schema for GET /health."""

    status: OverallStatus = Field(description="Overall system health")
    database: ServiceStatus = Field(description="PostgreSQL connection status")
    redis: ServiceStatus = Field(description="Redis connection status")
    version: str = Field(description="Application version")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the health check",
    )

    model_config = {"json_schema_extra": {
        "example": {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z",
        }
    }}


# ─────────────────────────────────────────────────────────────────────────────
# Version
# ─────────────────────────────────────────────────────────────────────────────

class VersionResponse(BaseModel):
    """Response schema for GET /version."""

    name: str = Field(description="Application name")
    version: str = Field(description="Semantic version")
    environment: str = Field(description="Deployment environment")
    python_version: str = Field(description="Python runtime version")
    platform: str = Field(description="Host OS platform")
    phase: str = Field(default="Phase 1 – Foundation", description="Development phase")

    model_config = {"json_schema_extra": {
        "example": {
            "name": "Cortex Gateway",
            "version": "1.0.0",
            "environment": "development",
            "python_version": "3.12.0",
            "platform": "linux",
            "phase": "Phase 1 – Foundation",
        }
    }}


# ─────────────────────────────────────────────────────────────────────────────
# Root
# ─────────────────────────────────────────────────────────────────────────────

class RootResponse(BaseModel):
    """Response schema for GET /."""

    name: str = Field(description="Application name")
    version: str = Field(description="Semantic version")
    description: str = Field(description="Short description of the service")
    docs: str = Field(description="URL to Swagger UI documentation")
    redoc: str = Field(description="URL to ReDoc documentation")
    health: str = Field(description="URL to the health endpoint")
    phase: str = Field(default="Phase 1 – Foundation")


# ─────────────────────────────────────────────────────────────────────────────
# Error
# ─────────────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Consistent error response shape returned by all exception handlers."""

    error: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error description")
    request_id: Annotated[str | None, Field(description="Trace ID from X-Request-ID header")] = None
    path: Annotated[str | None, Field(description="Request path that triggered the error")] = None
    detail: object | None = Field(default=None, description="Additional error details (e.g. validation errors)")

    model_config = {"json_schema_extra": {
        "example": {
            "error": "NOT_FOUND",
            "message": "Resource 'model' with id 'gpt-5' was not found",
            "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "path": "/api/v1/models/gpt-5",
        }
    }}
