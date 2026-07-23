"""
Cortex Gateway – Request Logging Middleware

Injects a unique Request-ID into every request and logs:
  - On arrival  : method, path, client IP, request ID
  - On completion: status code, duration (ms), request ID

The request_id is stored on request.state so downstream handlers can access it.
"""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging.logger import get_logger
from app.utils.request_id import generate_request_id

logger = get_logger(__name__)

# Header name used to propagate the request ID to the client
REQUEST_ID_HEADER = "X-Request-ID"


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request/response with a unique trace ID."""

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        # ── Assign Request ID ──────────────────────────────────────────────
        request_id = request.headers.get(REQUEST_ID_HEADER) or generate_request_id()
        request.state.request_id = request_id

        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )

        start_ts = time.perf_counter()

        # ── Log incoming request ───────────────────────────────────────────
        query = f"?{request.url.query}" if request.url.query else ""
        logger.info(
            f"→ {request.method} {request.url.path}{query} "
            f"[id={request_id}] [ip={client_ip}]"
        )

        # ── Process request ────────────────────────────────────────────────
        response: Response = await call_next(request)

        # ── Log outgoing response ──────────────────────────────────────────
        duration_ms = round((time.perf_counter() - start_ts) * 1000, 2)

        log_fn = logger.warning if response.status_code >= 400 else logger.info
        log_fn(
            f"← {request.method} {request.url.path} "
            f"{response.status_code} [{duration_ms}ms] [id={request_id}]"
        )

        # ── Propagate request ID to the caller ─────────────────────────────
        response.headers[REQUEST_ID_HEADER] = request_id

        return response
