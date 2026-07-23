"""
Cortex Gateway – Structured Logging via Loguru

Provides:
  - setup_logging(): called once at application startup
  - get_logger(name): returns a bound Loguru logger for any module

Log sinks:
  1. stdout  – colourised for developer readability in development
  2. File    – JSON-serialised, rotated daily, retained for 30 days

All log records include: timestamp, level, module, function, line, message,
plus any extra fields bound via logger.bind() or the | operator.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from loguru import logger


# ─────────────────────────────────────────────────────────────────────────────
# Loguru sink format helpers
# ─────────────────────────────────────────────────────────────────────────────

_CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
    "{extra}"
)


def _json_sink(message: "loguru.Message") -> None:  # type: ignore[name-defined]  # noqa: F821
    """Write each log record as a single JSON line to a file."""
    record = message.record
    log_entry = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "thread": record["thread"].name,
        **record["extra"],  # Request ID, custom fields, etc.
    }
    if record["exception"] is not None:
        exc = record["exception"]
        log_entry["exception"] = {
            "type": exc.type.__name__ if exc.type else None,
            "value": str(exc.value) if exc.value else None,
        }
    # Write to the file opened by Loguru's file handler via rotation
    message.record["extra"]["_json"] = json.dumps(log_entry, default=str)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> None:
    """Initialise Loguru sinks.  Call once from the FastAPI lifespan startup.

    Args:
        log_level: Minimum level to capture (TRACE/DEBUG/INFO/WARNING/ERROR).
        log_dir:   Directory for rotating log files (created if absent).
    """
    # Remove the default Loguru sink
    logger.remove()

    # ── Sink 1: Colourised stdout (developer-friendly) ─────────────────────
    logger.add(
        sys.stdout,
        format=_CONSOLE_FORMAT,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
        enqueue=False,
    )

    # ── Sink 2: JSON rotating file ─────────────────────────────────────────
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_path / "cortex_{time:YYYY-MM-DD}.log"),
        format="{time:YYYY-MM-DDTHH:mm:ss.SSSZ} | {level} | {name}:{function}:{line} | {message} | {extra}",
        level=log_level,
        rotation="00:00",       # New file each midnight
        retention="30 days",    # Keep 30 days of history
        compression="zip",      # Compress rotated files
        serialize=True,         # Write as JSON
        enqueue=True,           # Non-blocking I/O via background thread
        backtrace=True,
        diagnose=False,         # Disable in production (can expose internals)
    )

    logger.info("Logging initialised", level=log_level, log_dir=str(log_path))


def get_logger(name: str) -> "loguru.Logger":  # type: ignore[name-defined]  # noqa: F821
    """Return a Loguru logger bound with the given module name.

    Usage::

        from app.logging.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened", key="value")
    """
    return logger.bind(logger_name=name)
