"""
Cortex Gateway – Async Database Session Management

Provides:
  - Async SQLAlchemy engine (asyncpg driver)
  - AsyncSessionLocal factory
  - Async context manager get_db() for FastAPI dependency injection
  - init_db() / close_db() lifecycle hooks called on app startup/shutdown
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

# Module-level engine and session factory (initialised in init_db)
_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_engine() -> AsyncEngine:
    """Return the module-level engine, raising if not yet initialised."""
    if _engine is None:
        raise RuntimeError("Database engine is not initialised. Call init_db() first.")
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _async_session_factory is None:
        raise RuntimeError("Session factory is not initialised. Call init_db() first.")
    return _async_session_factory


# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle Hooks
# ─────────────────────────────────────────────────────────────────────────────

async def init_db() -> None:
    """Create the async engine and session factory.

    Called once during application startup (FastAPI lifespan).
    """
    global _engine, _async_session_factory

    settings = get_settings()

    logger.info(f"Initialising database connection | url={settings.database_url}")

    engine_kwargs = {
        "echo": settings.debug,
        "pool_pre_ping": True,
    }
    if not settings.database_url.startswith("sqlite"):
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 1800,
        })

    _engine = create_async_engine(
        settings.database_url,
        **engine_kwargs
    )


    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,        # Keep objects accessible after commit
        autocommit=False,
        autoflush=False,
    )

    # Verify connectivity at startup
    try:
        async with _engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.info("Database connection established successfully")
    except Exception as exc:
        logger.warning(f"Database connection check warning: {exc}")


async def close_db() -> None:
    """Dispose the engine connection pool.

    Called once during application shutdown (FastAPI lifespan).
    """
    global _engine
    if _engine is not None:
        logger.info("Closing database connection pool")
        await _engine.dispose()
        _engine = None


# ─────────────────────────────────────────────────────────────────────────────
# Dependency Injection
# ─────────────────────────────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a managed async database session.

    Usage::

        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(MyModel))
            ...

    The session is automatically committed on success and rolled back on error.
    """
    session = _get_session_factory()()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await session.close()
