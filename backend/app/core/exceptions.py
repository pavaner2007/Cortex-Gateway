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
# Provider Exception Hierarchy (Phase 2)
# ─────────────────────────────────────────────────────────────────────────────

class ProviderError(CortexException):
    """Base class for all upstream LLM provider errors."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "PROVIDER_ERROR"

    def __init__(self, provider: str, message: str = "Provider returned an error") -> None:
        self.provider = provider
        super().__init__(message)


class InvalidProviderError(CortexException):
    """Raised when the requested provider name does not exist in the registry."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "INVALID_PROVIDER"

    def __init__(self, provider: str) -> None:
        self.provider = provider
        super().__init__(f"Provider '{provider}' is not registered")


class ProviderUnavailableError(CortexException):
    """Raised when a known provider is disabled (missing API key)."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "PROVIDER_UNAVAILABLE"

    def __init__(self, provider: str) -> None:
        self.provider = provider
        super().__init__(f"Provider '{provider}' is currently unavailable or not configured")


class ProviderTimeoutError(ProviderError):
    """Raised when an upstream provider call exceeds the configured timeout."""

    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    error_code = "PROVIDER_TIMEOUT"

    def __init__(self, provider: str) -> None:
        super().__init__(provider, f"Provider '{provider}' did not respond within the timeout period")


class ProviderRateLimitError(ProviderError):
    """Raised when the upstream provider returns a rate-limit error (HTTP 429)."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "PROVIDER_RATE_LIMITED"

    def __init__(self, provider: str) -> None:
        super().__init__(provider, f"Provider '{provider}' is currently rate limited. Please retry later.")


class ProviderAuthenticationError(ProviderError):
    """Raised when the provider rejects the API key (HTTP 401/403)."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "PROVIDER_AUTH_ERROR"

    def __init__(self, provider: str) -> None:
        super().__init__(provider, f"Authentication failed for provider '{provider}'. Check your API key.")


class InvalidModelError(CortexException):
    """Raised when the requested model does not exist for the given provider."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "INVALID_MODEL"

    def __init__(self, provider: str, model: str) -> None:
        self.provider = provider
        self.model = model
        super().__init__(f"Model '{model}' is not available on provider '{provider}'")


class InvalidProviderRequestError(CortexException):
    """Raised when the provider rejects the request payload (HTTP 400)."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "INVALID_PROVIDER_REQUEST"

    def __init__(self, provider: str, detail: str) -> None:
        self.provider = provider
        super().__init__(f"Invalid request to provider '{provider}': {detail}")


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
