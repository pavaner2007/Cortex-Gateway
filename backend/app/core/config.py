"""
Cortex Gateway – Application Configuration

All settings are loaded from environment variables (or a .env file).
Uses pydantic-settings for type-safe, validated configuration.
Computed properties derive DATABASE_URL and REDIS_URL from individual parts.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised application settings.

    Values are sourced (in priority order) from:
      1. Real environment variables
      2. .env file in the working directory
      3. Field defaults defined below
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Allow extra fields so Docker-injected vars don't raise errors
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_name: str = Field(default="Cortex Gateway", description="Display name of the service")
    app_version: str = Field(default="1.0.0", description="Semantic version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Deployment environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode (never True in production)")

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port")
    postgres_db: str = Field(default="cortex_gateway", description="Database name")
    postgres_user: str = Field(default="cortex", description="Database user")
    postgres_password: str = Field(default="cortex_password", description="Database password")

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    redis_password: str | None = Field(default=None, description="Optional Redis password")

    # ── Security ──────────────────────────────────────────────────────────────
    secret_key: str = Field(
        default="change-me-in-production",
        min_length=16,
        description="Secret key used for signing tokens (min 32 chars in production)",
    )

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO", description="Loguru log level")

    # ── Computed Properties ───────────────────────────────────────────────────

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        """Async-compatible SQLAlchemy URL built from individual parts."""
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def redis_url(self) -> str:
        """Redis URL built from individual parts."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @computed_field  # type: ignore[misc]
    @property
    def is_production(self) -> bool:
        """Convenience flag – True only in production environment."""
        return self.environment == "production"

    @computed_field  # type: ignore[misc]
    @property
    def cors_origins(self) -> list[str]:
        """CORS allowed origins – wide open in dev, locked in production."""
        if self.is_production:
            return []  # Populate from env in future phases
        return ["*"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton instance of Settings.

    Using @lru_cache ensures the .env file is read only once per process,
    and the same object is returned throughout the application lifetime.
    """
    return Settings()
