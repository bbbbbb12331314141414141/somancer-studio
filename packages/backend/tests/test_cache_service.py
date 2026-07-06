"""Tests for CacheService and system API."""

import time
import pytest
from aimusic.services.cache_service import CacheService, TTL_GENRE


class TestCacheService:

    def test_set_and_get(self):
        c = CacheService()
        c.set("key1", {"data": 42}, ttl=10)
        assert c.get("key1") == {"data": 42}

    def test_miss_returns_none(self):
        c = CacheService()
        assert c.get("nonexistent") is None

    def test_expired_returns_none(self):
        c = CacheService()
        c.set("exp", "value", ttl=0.01)
        time.sleep(0.02)
        assert c.get("exp") is None

    def test_delete(self):
        c = CacheService()
        c.set("del_me", 99, ttl=60)
        assert c.delete("del_me") is True
        assert c.get("del_me") is None
        assert c.delete("del_me") is False

    def test_invalidate_prefix(self):
        c = CacheService()
        c.set("genres:all", [1, 2], ttl=60)
        c.set("genres:rock", [3], ttl=60)
        c.set("songs:1", {"id": 1}, ttl=60)
        removed = c.invalidate_prefix("genres:")
        assert removed == 2
        assert c.get("genres:all") is None
        assert c.get("songs:1") == {"id": 1}

    def test_clear(self):
        c = CacheService()
        c.set("a", 1, ttl=60)
        c.set("b", 2, ttl=60)
        c.clear()
        assert c.get("a") is None
        assert c.stats["size"] == 0

    def test_get_or_compute(self):
        c = CacheService()
        calls = []

        def compute():
            calls.append(1)
            return "result"

        r1 = c.get_or_compute("k", compute, ttl=60)
        r2 = c.get_or_compute("k", compute, ttl=60)
        assert r1 == "result"
        assert r2 == "result"
        assert len(calls) == 1  # only computed once

    def test_stats_hit_rate(self):
        c = CacheService()
        c.set("x", 1, ttl=60)
        c.get("x")   # hit
        c.get("x")   # hit
        c.get("y")   # miss
        stats = c.stats
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == pytest.approx(2 / 3, abs=0.01)

    def test_purge_expired(self):
        c = CacheService()
        c.set("live", "a", ttl=60)
        c.set("dead", "b", ttl=0.01)
        time.sleep(0.02)
        removed = c.purge_expired()
        assert removed == 1
        assert c.get("live") == "a"
        assert c.get("dead") is None

    def test_max_size_eviction(self):
        c = CacheService(max_size=3)
        c.set("a", 1, ttl=60)
        c.set("b", 2, ttl=60)
        c.set("c", 3, ttl=60)
        c.set("d", 4, ttl=60)  # triggers eviction
        assert len(c._cache) == 3

    def test_ttl_genre_constant(self):
        assert TTL_GENRE == 300
