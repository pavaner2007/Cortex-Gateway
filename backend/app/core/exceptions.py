"""
Cortex Gateway – Exception Hierarchy and Global Exception Handlers

Define a clear exception hierarchy rooted at CortexException.
Global handlers are registered via register_exception_handlers(app)
so that any CortexException produces a consistent JSON error shape.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger


# ─────────────────────────────────────────────────────────────────────────────
# Base Exception Hierarchy
# ─────────────────────────────────────────────────────────────────────────────

class CortexException(Exception):
    """Root exception for all domain-specific errors in Cortex Gateway.

    Attributes:
        message:     Human-readable error description.
        status_code: HTTP status code to return to the caller.
        error_code:  Machine-readable code for programmatic handling.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "CORTEX_ERROR"

    def __init__(self, message: str = "An unexpected error occurred") -> None:
        self.message = message
        super().__init__(message)


class ServiceUnavailableError(CortexException):
    """Raised when a required downstream service (DB, Redis, etc.) is unavailable."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "SERVICE_UNAVAILABLE"

    def __init__(self, service: str) -> None:
        super().__init__(f"Service '{service}' is currently unavailable")


class ConfigurationError(CortexException):
    """Raised when the application is misconfigured."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "CONFIGURATION_ERROR"


class NotFoundError(CortexException):
    """Raised when a requested resource cannot be found."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"

    def __init__(self, resource: str, identifier: str | int | None = None) -> None:
        detail = f"'{resource}'"
        if identifier is not None:
            detail += f" with id '{identifier}'"
        super().__init__(f"Resource {detail} was not found")


class ValidationError(CortexException):
    """Raised when business-level validation fails (distinct from Pydantic errors)."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"


# ─────────────────────────────────────────────────────────────────────────────
# JSON Error Shape Builder
# ─────────────────────────────────────────────────────────────────────────────

def _error_response(
    request: Request,
    status_code: int,
    error_code: str,
    message: str,
    detail: object | None = None,
) -> JSONResponse:
    """Build a consistently-shaped JSON error response."""
    request_id = getattr(request.state, "request_id", None)
    body: dict = {
        "error": error_code,
        "message": message,
        "request_id": request_id,
        "path": str(request.url.path),
    }
    if detail is not None:
        body["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


# ─────────────────────────────────────────────────────────────────────────────
# Handler Registration
# ─────────────────────────────────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI application."""

    @app.exception_handler(CortexException)
    async def cortex_exception_handler(request: Request, exc: CortexException) -> JSONResponse:
        logger.warning(f"Domain exception raised | code={exc.error_code} message={exc.message} path={request.url.path}")
        return _error_response(request, exc.status_code, exc.error_code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(f"Request validation failed | path={request.url.path} errors={exc.errors()}")
        return _error_response(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            "Request body or parameters are invalid",
            detail=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception | path={request.url.path}")
        return _error_response(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected internal error occurred",
        )
