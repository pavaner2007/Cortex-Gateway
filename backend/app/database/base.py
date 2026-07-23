"""
Cortex Gateway – SQLAlchemy Declarative Base

All ORM models must inherit from this Base so that:
  - Alembic can discover them for autogenerate
  - Table naming conventions are consistent project-wide
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Consistent naming convention for constraints — avoids unnamed constraint issues
# across databases and keeps migrations predictable.
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Project-wide declarative base with enforced constraint naming."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
