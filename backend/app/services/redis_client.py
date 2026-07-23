"""
Cortex Gateway – Async Redis Client

Provides:
  - init_redis()  : Connect and verify on startup
  - close_redis() : Gracefully close the connection pool on shutdown
  - get_redis()   : FastAPI dependency that yields the active Redis client
"""

from __future__ import annotations

from redis.asyncio import Redis
from redis.asyncio import from_url as redis_from_url
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.config import get_settings
from app.logging.logger import get_logger

logger = get_logger(__name__)

# Module-level client; initialised in init_redis()
_redis_client: Redis | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle Hooks
# ─────────────────────────────────────────────────────────────────────────────

async def init_redis() -> None:
    """Create and verify the Redis connection. Called at application startup."""
    global _redis_client

    settings = get_settings()
    logger.info(f"Initialising Redis connection | url={settings.redis_url}")

    _redis_client = redis_from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30,
    )

    try:
        await _redis_client.ping()
        logger.info("Redis connection established successfully")
    except RedisConnectionError as exc:
        logger.error(f"Failed to connect to Redis: {exc}")
        raise


async def close_redis() -> None:
    """Close the Redis connection pool. Called at application shutdown."""
    global _redis_client
    if _redis_client is not None:
        logger.info("Closing Redis connection")
        await _redis_client.aclose()
        _redis_client = None


# ─────────────────────────────────────────────────────────────────────────────
# Dependency Injection
# ─────────────────────────────────────────────────────────────────────────────

async def get_redis() -> Redis:
    """FastAPI dependency that returns the active Redis client.

    Usage::

        @router.get("/example")
        async def example(redis: Redis = Depends(get_redis)):
            value = await redis.get("some-key")
            ...
    """
    if _redis_client is None:
        raise RuntimeError("Redis client is not initialised. Call init_redis() first.")
    return _redis_client
