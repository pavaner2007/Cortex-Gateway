"""
Cortex Gateway – Chat Completion Schemas (Phase 2)

Defines the unified request/response format for the chat completions API.
All providers receive and return these Pydantic models, ensuring a consistent
developer experience regardless of the underlying LLM provider.
"""

from __future__ import annotations

import time
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────────────────────────────────────

MessageRole = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: MessageRole = Field(description="Role of the message author")
    content: str = Field(description="The content of the message", min_length=1)

    model_config = {"json_schema_extra": {"example": {"role": "user", "content": "Explain Kubernetes."}}}


class ChatCompletionRequest(BaseModel):
    """Unified request schema for all LLM providers.

    The ``provider`` field selects which LLM backend to use.
    If omitted, the gateway will use the configured ``DEFAULT_PROVIDER``.
    """

    provider: str | None = Field(
        default=None,
        description="LLM provider name (e.g. 'groq', 'gemini', 'openai'). Defaults to DEFAULT_PROVIDER.",
    )
    model: str | None = Field(
        default=None,
        description="Model identifier. Defaults to the provider's configured default model.",
    )
    messages: list[ChatMessage] = Field(
        description="Conversation messages in chronological order",
        min_length=1,
    )
    temperature: Annotated[float, Field(ge=0.0, le=2.0)] = Field(
        default=0.7,
        description="Sampling temperature (0.0 – 2.0). Higher = more random.",
    )
    max_tokens: Annotated[int, Field(ge=1, le=65536)] | None = Field(
        default=None,
        description="Maximum number of tokens to generate.",
    )
    top_p: Annotated[float, Field(ge=0.0, le=1.0)] | None = Field(
        default=None,
        description="Nucleus sampling probability mass.",
    )
    stop: list[str] | None = Field(
        default=None,
        description="Up to 4 stop sequences. Generation stops at first match.",
        max_length=4,
    )

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v: list[ChatMessage]) -> list[ChatMessage]:
        if not v:
            raise ValueError("messages cannot be empty")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Explain Kubernetes in simple terms."},
                ],
                "temperature": 0.7,
                "max_tokens": 500,
            }
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────────────────────────────────────


class UsageInfo(BaseModel):
    """Normalized token usage information.

    Fields are optional because some providers do not return exact counts.
    Never fabricate token values — use None when unavailable.
    """

    prompt_tokens: int | None = Field(default=None, description="Tokens in the prompt/input")
    completion_tokens: int | None = Field(default=None, description="Tokens in the completion/output")
    total_tokens: int | None = Field(default=None, description="Total tokens consumed")


class CompletionMetadata(BaseModel):
    """Gateway-level metadata attached to every response."""

    request_id: str = Field(description="Unique trace ID (X-Request-ID)")
    latency_ms: float = Field(description="Time (ms) spent waiting for the provider")


class ChatResponseMessage(BaseModel):
    """The assistant's reply message."""

    role: Literal["assistant"] = Field(default="assistant")
    content: str = Field(description="Generated text")


class ChatCompletionChoice(BaseModel):
    """A single completion choice."""

    index: int = Field(description="Choice index (0-based)")
    message: ChatResponseMessage = Field(description="The generated message")
    finish_reason: str | None = Field(
        default=None,
        description="Reason generation stopped (e.g. 'stop', 'length')",
    )


class ChatCompletionResponse(BaseModel):
    """Standardized chat completion response.

    All providers MUST normalize their output into this schema.
    Provider-specific structures must never appear here.
    """

    id: str = Field(description="Unique completion identifier (ctx_...)")
    object: Literal["chat.completion"] = Field(default="chat.completion")
    created: int = Field(
        default_factory=lambda: int(time.time()),
        description="Unix timestamp of generation",
    )
    provider: str = Field(description="Provider that served the request")
    model: str = Field(description="Model that was used")
    choices: list[ChatCompletionChoice] = Field(description="Generated completion choices")
    usage: UsageInfo = Field(description="Token usage information")
    metadata: CompletionMetadata = Field(description="Gateway request metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "ctx_a8f31c",
                "object": "chat.completion",
                "created": 1710000000,
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Kubernetes is a container orchestration system..."},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 25, "completion_tokens": 95, "total_tokens": 120},
                "metadata": {"request_id": "uuid-here", "latency_ms": 423.5},
            }
        }
    }
