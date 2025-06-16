# Middleware

This folder contains FastAPI middleware for cross-cutting concerns.

## 📁 Files

- **`rate_limiter.py`** - Rate limiting middleware
- **`cors.py`** - CORS configuration
- **`auth.py`** - Authentication middleware (template)
- **`validation.py`** - Request validation middleware

## 🔧 How Middleware Works

Middleware processes requests and responses in order:

```
Request → Rate Limiter → Auth → Validation → Route Handler
Response ← Rate Limiter ← Auth ← Validation ← Route Handler  
```

## 🛡️ Rate Limiting

Uses Redis for distributed rate limiting:

```python
# Configure in settings.py
RATE_LIMIT_PER_MINUTE = 60
REDIS_URL = "redis://localhost:6379"
```

## 🔐 Authentication

Template provided for JWT authentication:

```python
# Add JWT token to requests
headers = {
    "Authorization": f"Bearer {jwt_token}"
}
```

## ⚙️ Adding New Middleware

1. Create middleware file in this folder
2. Add to `main.py`:

```python
from .middleware.your_middleware import YourMiddleware
app.add_middleware(YourMiddleware)
```
