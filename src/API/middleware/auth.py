# src/api/middleware/auth.py
"""
Authentication Middleware Template

Template for JWT authentication middleware.
Customize this file based on your authentication provider.
"""

import logging
from typing import Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("auth")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication middleware template.
    
    To use this middleware:
    1. Implement JWT validation logic
    2. Configure your JWT secret and algorithm
    3. Add to main.py: app.add_middleware(AuthMiddleware)
    """
    
    def __init__(self, app):
        super().__init__(app)
        # TODO: Configure your JWT settings
        self.jwt_secret = "your-jwt-secret"
        self.jwt_algorithm = "HS256"
    
    async def dispatch(self, request: Request, call_next):
        """Process request with authentication."""
        
        # Skip authentication for public endpoints
        public_paths = ["/", "/health", "/health/live", "/health/ready", "/docs", "/openapi.json"]
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Extract JWT token
        token = self._extract_token(request)
        
        if not token:
            raise HTTPException(status_code=401, detail="Missing authentication token")
        
        # Validate token
        user_data = self._validate_token(token)
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        # Add user data to request state
        request.state.user = user_data
        
        # Process request
        response = await call_next(request)
        return response
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        return None
    
    def _validate_token(self, token: str) -> Optional[dict]:
        """
        Validate JWT token and return user data.
        
        TODO: Implement your JWT validation logic here.
        Example implementations:
        - PyJWT for standard JWT
        - Auth0 SDK for Auth0
        - Firebase Admin SDK for Firebase
        """
        try:
            # Example with PyJWT (uncomment and customize):
            # import jwt
            # payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            # return {
            #     "user_id": payload.get("sub"),
            #     "email": payload.get("email"),
            #     "roles": payload.get("roles", [])
            # }
            
            # For now, return None (authentication disabled)
            logger.warning("Authentication middleware is not implemented")
            return None
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None


# TODO: Implement helper functions for your auth provider
def verify_auth0_token(token: str) -> Optional[dict]:
    """Example function for Auth0 token validation."""
    pass

def verify_firebase_token(token: str) -> Optional[dict]:
    """Example function for Firebase token validation."""
    pass

def verify_custom_jwt(token: str, secret: str) -> Optional[dict]:
    """Example function for custom JWT validation."""
    pass
