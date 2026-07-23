"""
Cortex Gateway – Request ID Utility

Generates unique, URL-safe identifiers for request tracing.
Using UUID4 gives 122 bits of randomness — sufficient for distributed tracing
without a central coordinator.
"""

from __future__ import annotations

import uuid


def generate_request_id() -> str:
    """Return a new UUID4 string suitable for use as a request trace ID.

    Example output: ``"3a1f9e2c-7b4d-4f8a-9c3e-1d2a5b6f7e8d"``
    """
    return str(uuid.uuid4())
