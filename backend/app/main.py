"""
Cortex Gateway – Application Factory

This module defines create_app() which constructs and configures the FastAPI
application. The entry point for Uvicorn is the module-level `app` instance.

Startup sequence:
  1. Logging configured
  2. Database engine created and connectivity verified
  3. Redis client created and connectivity verified

Shutdown sequence:
  1. Redis connection pool closed
  2. Database engine disposed
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.database.session import close_db, init_db
from app.logging.logger import get_logger, setup_logging
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.timing import TimingMiddleware
from app.providers.registry import build_registry
from app.services.redis_client import close_redis, init_redis

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan (startup + shutdown)
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application-level resources across the full lifecycle.

    Everything before ``yield`` runs at startup; everything after runs at shutdown.
    Using the lifespan pattern (vs. deprecated on_event) ensures resources are
    always cleaned up even if startup partially fails.
    """
    settings = get_settings()

    # ── Startup ────────────────────────────────────────────────────────────────
    setup_logging(log_level=settings.log_level)
    logger.info(f"Starting Cortex Gateway v{settings.app_version} [{settings.environment}]")

    await init_db()
    await init_redis()

    # Build the provider registry and attach to app state
    app.state.provider_registry = build_registry(settings)
    enabled = [p.name for p in app.state.provider_registry.list_enabled()]
    logger.info(f"Provider registry built | enabled={enabled}")

    logger.info("Cortex Gateway is ready to accept requests")

    yield  # Application runs here

    # ── Shutdown ──────────────────────────────────────────────────────────
    logger.info("Shutting down Cortex Gateway")
    await close_redis()
    await close_db()
    logger.info("Shutdown complete")


# ─────────────────────────────────────────────────────────────────────────────
# Application Factory
# ─────────────────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Construct and configure the FastAPI application.

    Returns a fully configured FastAPI instance.  Separating this into a
    factory function (rather than module-level construction) makes the app
    easily testable and avoids side effects on import.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "**Cortex Gateway** is an enterprise AI Infrastructure Platform that "
            "routes, manages, and observes all LLM traffic from a single control plane.\n\n"
            "### Phase 2 – Unified Multi-Provider LLM Gateway\n"
            "This release adds a unified Chat Completions API supporting Groq, Gemini, and OpenAI "
            "through a single normalized request/response format. "
            "Provider routing, auth, analytics, and advanced reliability will follow in subsequent phases."
        ),
        contact={
            "name": "Cortex Gateway Team",
            "url": "https://github.com/your-org/cortex-gateway",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware (registered in LIFO order: last added = outermost) ─────
    # Execution order for a request:
    #   CORSMiddleware → TimingMiddleware → LoggingMiddleware → ErrorHandlerMiddleware → Route

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins if settings.cors_origins != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )
    app.add_middleware(TimingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)

    # ── Exception Handlers ────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ───────────────────────────────────────────────────────────
    app.include_router(api_router)

    return app


# ─────────────────────────────────────────────────────────────────────────────
# Module-level app instance (Uvicorn entry point: app.main:app)
# ─────────────────────────────────────────────────────────────────────────────
app = create_app()
