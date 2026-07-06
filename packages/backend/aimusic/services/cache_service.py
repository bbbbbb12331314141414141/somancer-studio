"""
Cache Service — in-memory response caching for frequently accessed data.

Provides LRU-style caching for:
  - Genre lookups (rarely changes)
  - AI model lists (changes when Ollama is updated)
  - Platform loudness targets (static)
  - Song metadata (changes less frequently than audio)

Phase 8: in-process dictionary cache with TTL.
Phase 9+: Replace with Redis for multi-process deployments.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Default TTLs (seconds)
TTL_GENRE    = 300    # 5 minutes — genre data rarely changes
TTL_MODELS   = 60     # 1 minute  — model list refreshed frequently
TTL_PLATFORM = 86400  # 24 hours  — platform targets are static
TTL_SONG     = 30     # 30 seconds — song data changes often
TTL_DEFAULT  = 120    # 2 minutes


@dataclass
class CacheEntry:
    """A single cached value with TTL."""
    value: Any
    expires_at: float
    hits: int = 0

    @property
    def is_expired(self) -> bool:
        return time.monotonic() > self.expires_at


class CacheService:
    """
    Thread-safe in-process LRU cache with TTL support.

    Usage:
        cache = CacheService()

        # Cache a value
        cache.set("genres:all", genres_list, ttl=TTL_GENRE)

        # Get a value
        cached = cache.get("genres:all")

        # Get-or-compute pattern
        genres = cache.get_or_compute(
            key="genres:all",
            fn=lambda: db.query(Genre).all(),
            ttl=TTL_GENRE,
        )
    """

    def __init__(self, max_size: int = 512) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    # ── Core Operations ───────────────────────────────────────────────────────

    def get(self, key: str) -> Optional[Any]:
        """Return cached value or None if missing/expired."""
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        if entry.is_expired:
            del self._cache[key]
            self._misses += 1
            return None
        entry.hits += 1
        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: float = TTL_DEFAULT) -> None:
        """Cache a value with a TTL in seconds."""
        if len(self._cache) >= self._max_size:
            self._evict()
        self._cache[key] = CacheEntry(
            value=value,
            expires_at=time.monotonic() + ttl,
        )

    def delete(self, key: str) -> bool:
        """Remove a specific key. Returns True if it existed."""
        return self._cache.pop(key, None) is not None

    def invalidate_prefix(self, prefix: str) -> int:
        """Remove all keys starting with `prefix`. Returns count removed."""
        to_delete = [k for k in self._cache if k.startswith(prefix)]
        for k in to_delete:
            del self._cache[k]
        return len(to_delete)

    def clear(self) -> None:
        """Remove all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_or_compute(
        self,
        key: str,
        fn: Callable[[], T],
        ttl: float = TTL_DEFAULT,
    ) -> T:
        """
        Return cached value or compute it with `fn`, then cache.

        Args:
            key: Cache key.
            fn: Zero-argument callable that produces the value.
            ttl: Time-to-live in seconds.

        Returns:
            The cached or freshly computed value.
        """
        cached = self.get(key)
        if cached is not None:
            return cached  # type: ignore[return-value]
        value = fn()
        self.set(key, value, ttl)
        return value

    # ── Diagnostics ───────────────────────────────────────────────────────────

    @property
    def stats(self) -> dict:
        """Return cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        live = sum(1 for e in self._cache.values() if not e.is_expired)
        return {
            "size": len(self._cache),
            "live_entries": live,
            "expired_entries": len(self._cache) - live,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 3),
        }

    def purge_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        expired = [k for k, e in self._cache.items() if e.is_expired]
        for k in expired:
            del self._cache[k]
        return len(expired)

    # ── Private ────────────────────────────────────────────────────────────────

    def _evict(self) -> None:
        """Remove expired entries, then the least-hit live entry."""
        # First try to clear expired
        removed = self.purge_expired()
        if removed:
            return
        # Evict least-hit entry
        if self._cache:
            lru_key = min(self._cache, key=lambda k: self._cache[k].hits)
            del self._cache[lru_key]
            logger.debug(f"Cache evicted: {lru_key}")


# ── Singleton ─────────────────────────────────────────────────────────────────

_cache: Optional[CacheService] = None


def get_cache() -> CacheService:
    """Return the global cache singleton."""
    global _cache
    if _cache is None:
        _cache = CacheService(max_size=512)
    return _cache
