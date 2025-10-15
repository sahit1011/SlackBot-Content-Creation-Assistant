# app/services/cache.py
import redis
import json
import hashlib
from typing import Any, Optional, Dict
from app.config import Config

class CacheService:
    """Handle Redis caching operations"""

    def __init__(self):
        try:
            self.client = redis.from_url(Config.REDIS_URL) if Config.REDIS_URL else None
            if self.client:
                self.client.ping()
        except:
            self.client = None
            print("Warning: Redis unavailable, caching disabled")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")

        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (default 1 hour)"""
        if not self.client:
            return False

        try:
            self.client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str):
        """Delete key from cache"""
        if not self.client:
            return

        try:
            self.client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")

    def get_user_state(self, user_id: str) -> Optional[Dict]:
        """Get user session state"""
        return self.get(f"user:{user_id}:state")

    def set_user_state(self, user_id: str, state: Dict, ttl: int = 3600):
        """Set user session state"""
        self.set(f"user:{user_id}:state", state, ttl)

    def clear_user_state(self, user_id: str):
        """Clear user session state"""
        self.delete(f"user:{user_id}:state")

    def cache_search_results(self, query: str, results: list):
        """Cache search results for 1 hour"""
        cache_key = self._generate_cache_key("search", query)
        self.set(cache_key, results, ttl=3600)

    def get_cached_search(self, query: str) -> Optional[list]:
        """Get cached search results"""
        cache_key = self._generate_cache_key("search", query)
        return self.get(cache_key)

    def cache_embeddings(self, keywords: list, embeddings: Any):
        """Cache embeddings for 24 hours"""
        cache_key = self._generate_cache_key("embeddings", str(sorted(keywords)))
        # Store as binary data
        if self.client:
            try:
                import numpy as np
                self.client.setex(
                    cache_key,
                    86400,  # 24 hours
                    embeddings.astype(np.float32).tobytes()
                )
            except:
                pass

    def get_cached_embeddings(self, keywords: list) -> Optional[Any]:
        """Get cached embeddings"""
        cache_key = self._generate_cache_key("embeddings", str(sorted(keywords)))
        if self.client:
            try:
                import numpy as np
                cached = self.client.get(cache_key)
                if cached:
                    return np.frombuffer(cached, dtype=np.float32)
            except:
                pass
        return None

    def increment_rate_limit(self, user_id: str, action: str) -> int:
        """Increment rate limit counter"""
        if not self.client:
            return 0

        key = f"ratelimit:{user_id}:{action}"
        try:
            count = self.client.incr(key)
            if count == 1:
                self.client.expire(key, 3600)  # 1 hour window
            return count
        except:
            return 0

    def check_rate_limit(self, user_id: str, action: str, max_requests: int = 10) -> bool:
        """Check if user has exceeded rate limit"""
        count = self.increment_rate_limit(user_id, action)
        return count <= max_requests

    def _generate_cache_key(self, prefix: str, data: str) -> str:
        """Generate cache key from data"""
        hash_value = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{hash_value}"