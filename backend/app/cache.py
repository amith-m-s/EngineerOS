"""Cache abstraction with TTL support.

Provides an ``InMemoryCache`` for development and a contract for
Redis-backed implementations in production.  Also includes a token
blacklist used by the logout flow.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any


class CacheBackend(ABC):
    """Abstract cache interface."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        ...

    @abstractmethod
    async def clear(self) -> None:
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        ...


class InMemoryCache(CacheBackend):
    """Simple in-memory cache with TTL support.

    Good enough for development and single-process deployments.
    In production, swap for a Redis-backed implementation.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float | None]] = {}  # key → (value, expires_at)

    def _is_expired(self, key: str) -> bool:
        entry = self._store.get(key)
        if entry is None:
            return True
        _, expires_at = entry
        if expires_at is not None and time.time() > expires_at:
            del self._store[key]
            return True
        return False

    async def get(self, key: str) -> Any | None:
        if self._is_expired(key):
            return None
        value, _ = self._store[key]
        return value

    async def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        expires_at = (time.time() + ttl_seconds) if ttl_seconds else None
        self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    async def clear(self) -> None:
        self._store.clear()

    async def exists(self, key: str) -> bool:
        return not self._is_expired(key)


# ---------------------------------------------------------------------------
# Token blacklist (used by logout)
# ---------------------------------------------------------------------------

class TokenBlacklist:
    """Keeps track of invalidated JWT tokens.

    Uses the cache backend so it works with both in-memory and Redis.
    Tokens are stored with a TTL matching their remaining lifetime so
    the blacklist doesn't grow unboundedly.
    """

    _PREFIX = "blacklist:"

    def __init__(self, cache: CacheBackend) -> None:
        self._cache = cache

    async def blacklist(self, token_jti: str, *, ttl_seconds: int = 86400) -> None:
        """Add a token to the blacklist."""
        await self._cache.set(f"{self._PREFIX}{token_jti}", True, ttl_seconds=ttl_seconds)

    async def is_blacklisted(self, token_jti: str) -> bool:
        """Check whether a token has been blacklisted."""
        return await self._cache.exists(f"{self._PREFIX}{token_jti}")


# ---------------------------------------------------------------------------
# Singleton instances
# ---------------------------------------------------------------------------

_cache: InMemoryCache | None = None
_blacklist: TokenBlacklist | None = None


def get_cache() -> InMemoryCache:
    """Get the singleton cache instance."""
    global _cache
    if _cache is None:
        _cache = InMemoryCache()
    return _cache


def get_token_blacklist() -> TokenBlacklist:
    """Get the singleton token blacklist instance."""
    global _blacklist
    if _blacklist is None:
        _blacklist = TokenBlacklist(get_cache())
    return _blacklist
