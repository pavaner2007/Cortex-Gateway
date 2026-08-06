"""
Cortex Gateway – API v1 Router Aggregator (Phase 2)

All v1 endpoint routers are registered here.
This router is mounted at /api/v1 in the top-level api/router.py.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.providers import router as providers_router

v1_router = APIRouter(prefix="/api/v1")

# ── Chat Completions ──────────────────────────────────────────────────────────
v1_router.include_router(chat_router, tags=["Chat"])

# ── Provider Discovery ────────────────────────────────────────────────────────
v1_router.include_router(providers_router, tags=["Providers"])
