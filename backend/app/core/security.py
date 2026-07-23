"""
Cortex Gateway – Security Primitives

Phase 1: Placeholder module. Future phases will implement:
  - API key hashing and verification
  - JWT token generation and validation
  - Tenant-scoped permission checks
  - Rate limit token bucket logic
"""

from __future__ import annotations


# ─────────────────────────────────────────────────────────────────────────────
# Placeholder helpers — to be expanded in Phase 2 (Authentication)
# ─────────────────────────────────────────────────────────────────────────────

def generate_api_key() -> str:  # pragma: no cover
    """Generate a cryptographically secure random API key.

    Phase 2 implementation will persist the hash in the database.
    """
    import secrets
    return secrets.token_urlsafe(48)


def hash_secret(value: str) -> str:  # pragma: no cover
    """Return a bcrypt/argon2 hash of *value*.

    Phase 2 will replace this with a proper password-hashing library.
    """
    import hashlib
    return hashlib.sha256(value.encode()).hexdigest()
