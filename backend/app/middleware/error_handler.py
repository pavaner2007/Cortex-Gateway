"""
Cortex Gateway – Catch-All Error Handler Middleware

Catches any exception that escapes the route handlers and exception handlers,
returning a consistent JSON error body rather than crashing with a 500 HTML page.

Note: FastAPI's own @app.exception_handler registrations handle most cases.
This middleware is the final safety net for truly unexpected errors (e.g.,
errors inside other middleware).
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.logging.logger import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Last-resort middleware that catches unhandled exceptions and returns JSON."""

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        try:
            return await call_next(request)
        except Exception as exc:  # pylint: disable=broad-except
            request_id = getattr(request.state, "request_id", "unknown")
            logger.exception(
                f"Unhandled exception [{type(exc).__name__}] "
                f"| {request.method} {request.url.path} [id={request_id}]"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "request_id": request_id,
                    "path": str(request.url.path),
                },
            )
