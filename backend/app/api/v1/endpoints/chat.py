"""
Cortex Gateway – Chat Completions Endpoint (Phase 2)

POST /api/v1/chat/completions

Unified endpoint for sending chat requests to any configured LLM provider.
The provider is selected via the request body; if omitted, the gateway
uses the configured DEFAULT_PROVIDER.
"""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from app.providers.registry import ProviderRegistry
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.schemas.common import ErrorResponse
from app.services.chat_service import ChatService

router = APIRouter()


def _get_registry(request: Request) -> ProviderRegistry:
    """Extract the ProviderRegistry from application state."""
    return request.app.state.provider_registry


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat Completions",
    description=(
        "Send a chat request to any configured LLM provider using a unified format.\n\n"
        "**Supported providers:** `groq`, `gemini`, `openai`\n\n"
        "If `provider` is omitted, the gateway uses the configured `DEFAULT_PROVIDER`.\n\n"
        "If `model` is omitted, the provider's configured default model is used."
    ),
    responses={
        200: {"description": "Successful chat completion"},
        400: {"model": ErrorResponse, "description": "Invalid request payload"},
        404: {"model": ErrorResponse, "description": "Provider or model not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Provider rate limited"},
        502: {"model": ErrorResponse, "description": "Provider returned an error"},
        503: {"model": ErrorResponse, "description": "Provider unavailable"},
        504: {"model": ErrorResponse, "description": "Provider timeout"},
    },
)
async def chat_completions(
    body: ChatCompletionRequest,
    request: Request,
) -> ChatCompletionResponse:
    """Execute a chat completion through the unified provider gateway."""
    request_id: str = getattr(request.state, "request_id", "unknown")
    registry = _get_registry(request)
    service = ChatService(registry)
    return await service.complete(body, request_id)
