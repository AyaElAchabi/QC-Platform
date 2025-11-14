"""
Rate limiting utilities
"""
from datetime import datetime
from fastapi import HTTPException, status

from core.redis_client import redis_client
from core.config import settings


def check_rate_limit(user_id: str, endpoint: str = "global") -> bool:
    """
    Check if user has exceeded rate limit
    
    Args:
        user_id: User UUID as string
        endpoint: Specific endpoint or "global"
    
    Returns:
        True if within limit
    
    Raises:
        HTTPException if limit exceeded
    """
    minute = datetime.utcnow().strftime("%Y-%m-%d:%H:%M")
    key = f"ratelimit:{user_id}:{endpoint}:{minute}"
    
    count = redis_client.incr(key)
    
    if count == 1:
        redis_client.expire(key, 60)
    
    if count > settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for {endpoint}. Max {settings.RATE_LIMIT_PER_MINUTE} requests per minute."
        )
    
    return True