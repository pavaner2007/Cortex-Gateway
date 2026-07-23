"""
Cortex Gateway – Health Endpoint

GET /health

Performs live connectivity checks against PostgreSQL and Redis,
returning the overall system health status to monitoring tools
and the frontend dashboard.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.session import get_db
from app.logging.logger import get_logger
from app.schemas.common import HealthResponse
from app.services.redis_client import get_redis

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health Check",
    description=(
        "Performs live connectivity checks against PostgreSQL and Redis. "
        "Returns **healthy** when both services are reachable, "
        "**degraded** if one is down, or **unhealthy** if both are down."
    ),
    responses={
        200: {"description": "Health status returned (check 'status' field for actual health)"},
    },
)
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> HealthResponse:
    """Return the current health of all infrastructure dependencies."""
    settings = get_settings()

    # ── Database Check ────────────────────────────────────────────────────
    db_status: str = "disconnected"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning(f"Database health check failed: {exc}")

    # ── Redis Check ───────────────────────────────────────────────────────
    redis_status: str = "disconnected"
    try:
        await redis.ping()
        redis_status = "connected"
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning(f"Redis health check failed: {exc}")

    # ── Derive Overall Status ─────────────────────────────────────────────
    connected_count = sum([db_status == "connected", redis_status == "connected"])
    if connected_count == 2:
        overall = "healthy"
    elif connected_count == 1:
        overall = "degraded"
    else:
        overall = "unhealthy"

    logger.info(f"Health check completed | status={overall} db={db_status} redis={redis_status}")

    return HealthResponse(
        status=overall,  # type: ignore[arg-type]
        database=db_status,  # type: ignore[arg-type]
        redis=redis_status,  # type: ignore[arg-type]
        version=settings.app_version,
    )  # type: ignore comments needed because Literal[...] narrowing doesn't track str vars
