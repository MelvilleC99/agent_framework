# src/api/middleware/rate_limiter.py
"""
Rate Limiting Middleware

Implements rate limiting using Redis for distributed environments.
"""

import time
import json
import logging
from typing import Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("rate_limiter")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.
    
    Limits requests per IP address with configurable limits.
    """
    
    def __init__(self, app, redis_client: Optional[object] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.requests_per_minute = 60  # Default limit
        self.burst_limit = 10  # Default burst limit
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/live", "/health/ready"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        allowed = await self._check_rate_limit(client_ip)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content=json.dumps({"error": "Rate limit exceeded"}),
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self._get_remaining_requests(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP (behind proxy)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    async def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limits."""
        if not self.redis_client:
            # If no Redis, allow all requests (development mode)
            return True
        
        try:
            key = f"rate_limit:{client_ip}"
            current_time = int(time.time())
            window_start = current_time - 60  # 60-second window
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            current_count = await self.redis_client.zcard(key)
            
            if current_count >= self.requests_per_minute:
                return False
            
            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})
            
            # Set expiry on key
            await self.redis_client.expire(key, 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # On error, allow request (fail open)
            return True
    
    async def _get_remaining_requests(self, client_ip: str) -> int:
        """Get remaining requests for client."""
        if not self.redis_client:
            return self.requests_per_minute
        
        try:
            key = f"rate_limit:{client_ip}"
            current_count = await self.redis_client.zcard(key)
            return max(0, self.requests_per_minute - current_count)
        except Exception:
            return self.requests_per_minute
