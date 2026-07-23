"""
Alembic Environment – Cortex Gateway

Configured for async SQLAlchemy (asyncpg driver).
The database URL is sourced from app.core.config to stay in sync with the
application's own settings rather than duplicating it in alembic.ini.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import application config and Base so Alembic can find models
from app.core.config import get_settings
from app.database.base import Base

# ── Import all models here so Base.metadata is populated ──────────────────
# Example (add as models are created in future phases):
#   from app.models.user import User
#   from app.models.api_key import ApiKey

# ─────────────────────────────────────────────────────────────────────────────

config = context.config

# Set up Python logging from alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point Alembic at the application metadata for autogenerate
target_metadata = Base.metadata

# Inject the async-compatible database URL from our settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


# ─────────────────────────────────────────────────────────────────────────────
# Offline Mode (generate SQL script without a live connection)
# ─────────────────────────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ─────────────────────────────────────────────────────────────────────────────
# Online Mode (apply migrations against a live database)
# ─────────────────────────────────────────────────────────────────────────────

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations using an async engine (required for asyncpg driver)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
