"""
Security utilities (CORS, rate limiting, etc.)
"""
from fastapi import Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

from core.config import settings
from core.redis_client import redis_client


def add_cors_middleware(app):
    """
    Add CORS middleware to FastAPI app
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis
    
    Limit: 100 requests per minute per IP
    """
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Exemptions
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
            return await call_next(request)
        
        # Rate limit key
        minute = datetime.utcnow().strftime("%Y-%m-%d:%H:%M")
        key = f"ratelimit:ip:{client_ip}:{minute}"
        
        # Increment counter
        count = redis_client.incr(key)
        
        # Set expiry on first request
        if count == 1:
            redis_client.expire(key, 60)
        
        # Check limit
        if count > settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        response = await call_next(request)
        return response