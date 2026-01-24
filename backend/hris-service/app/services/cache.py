"""
In-memory cache with TTL for HRIS data
For production, replace with Redis for distributed caching
"""

import asyncio
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class TTLCache:
    """Simple TTL cache for reducing API calls"""

    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return f"{prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if datetime.utcnow() < entry["expires_at"]:
                    logger.debug(f"Cache HIT: {key[:50]}")
                    return entry["value"]
                else:
                    del self._cache[key]
            logger.debug(f"Cache MISS: {key[:50]}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        async with self._lock:
            self._cache[key] = {
                "value": value,
                "expires_at": datetime.utcnow() + timedelta(seconds=ttl or self._default_ttl)
            }

    async def delete(self, key: str) -> None:
        """Delete key from cache"""
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()

    def cached(self, ttl: Optional[int] = None, prefix: str = ""):
        """Decorator for caching async function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Skip 'self' for method caching
                cache_args = args[1:] if args and hasattr(args[0], '__class__') else args
                key = self._make_key(prefix or func.__name__, *cache_args, **kwargs)

                # Try cache first
                cached_value = await self.get(key)
                if cached_value is not None:
                    return cached_value

                # Call function and cache result
                result = await func(*args, **kwargs)
                await self.set(key, result, ttl)
                return result
            return wrapper
        return decorator


# Global cache instance
# For 100ms SLA: Use Redis with ~60s TTL
# For 1000ms SLA: In-memory with ~300s TTL is acceptable
hris_cache = TTLCache(default_ttl=300)


def cache_key_for_entity(entity_type: str, connection_id: str) -> str:
    """Generate cache key for entity data"""
    return f"entity:{entity_type}:{connection_id}"
