"""
Cortex Gateway – API Router Aggregator

All endpoint routers are registered here and included in the FastAPI app
from main.py. Phase 1 system endpoints are at root; Phase 2 endpoints
are versioned under /api/v1.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.root import router as root_router
from app.api.endpoints.version import router as version_router
from app.api.v1.router import v1_router

# The top-level router — imported by app/main.py
api_router = APIRouter()

# ── System Endpoints (Phase 1) ────────────────────────────────────────────────
api_router.include_router(root_router, tags=["System"])
api_router.include_router(health_router, tags=["System"])
api_router.include_router(version_router, tags=["System"])

# ── Versioned API (Phase 2+) ──────────────────────────────────────────────────
api_router.include_router(v1_router)
