"""
Redis client for caching and queues
"""
import redis
from typing import Optional, Any
import json

from core.config import settings


class RedisClient:
    """
    Wrapper around redis-py with convenience methods
    """
    
    def __init__(self):
        self.client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True
        )
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        return self.client.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set key-value with optional TTL (seconds)"""
        if ttl:
            self.client.setex(key, ttl, value)
        else:
            self.client.set(key, value)
    
    def delete(self, key: str):
        """Delete key"""
        self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key) > 0
    
    def incr(self, key: str) -> int:
        """Increment counter"""
        return self.client.incr(key)
    
    def expire(self, key: str, seconds: int):
        """Set expiration on key"""
        self.client.expire(key, seconds)
    
    def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value"""
        value = self.get(key)
        return json.loads(value) if value else None
    
    def set_json(self, key: str, value: dict, ttl: Optional[int] = None):
        """Set JSON value"""
        self.set(key, json.dumps(value), ttl)
    
    def ping(self) -> bool:
        """Check Redis connection"""
        try:
            return self.client.ping()
        except:
            return False


# Global instance
redis_client = RedisClient()