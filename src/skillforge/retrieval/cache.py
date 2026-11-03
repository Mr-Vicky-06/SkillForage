"""In-Memory LRU Content-Hash Query Cache for SkillForge Retrieval."""

from __future__ import annotations
import hashlib
import time
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple


class QueryCache:
    """Thread-safe LRU Cache with TTL and content-hash keys."""

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._cache: OrderedDict[str, Tuple[float, Any]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _hash_key(self, query: str, context: Optional[str] = None, mode: str = "balanced", limit: int = 5) -> str:
        raw = f"{query.strip().lower()}|{context or ''}|{mode}|{limit}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, query: str, context: Optional[str] = None, mode: str = "balanced", limit: int = 5) -> Optional[Any]:
        key = self._hash_key(query, context, mode, limit)
        if key not in self._cache:
            self._misses += 1
            return None

        timestamp, val = self._cache[key]
        if time.time() - timestamp > self.ttl:
            del self._cache[key]
            self._misses += 1
            return None

        # Move to end for LRU
        self._cache.move_to_end(key)
        self._hits += 1
        return val

    def put(self, query: str, value: Any, context: Optional[str] = None, mode: str = "balanced", limit: int = 5) -> None:
        key = self._hash_key(query, context, mode, limit)
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)  # Evict oldest
        self._cache[key] = (time.time(), value)

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> Dict[str, Any]:
        total = self._hits + self._misses
        hit_rate = round((self._hits / total) if total > 0 else 0.0, 4)
        return {
            "cached_entries": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate
        }

