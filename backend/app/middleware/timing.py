"""
Cortex Gateway – Request Timing Middleware

Injects an `X-Process-Time` header (in milliseconds) into every response.
This allows clients and monitoring tools to measure server-side processing time
without parsing logs.
"""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TimingMiddleware(BaseHTTPMiddleware):
    """Append X-Process-Time (ms) to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
        response.headers["X-Process-Time"] = str(elapsed_ms)
        return response
