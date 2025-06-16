# API Layer

The API layer provides the HTTP interface for the agent system. It handles request routing, middleware processing, and dependency injection.

## 📁 Structure

```
api/
├── README.md              # This file
├── main.py               # FastAPI application + startup
├── config/               # Configuration and dependency injection
│   ├── README.md         # Configuration guide
│   ├── container.py      # Dependency injection container
│   ├── settings.py       # Environment configuration
│   └── database.py       # Database initialization
├── middleware/           # Request/response middleware
│   ├── README.md         # Middleware guide
│   ├── rate_limiter.py   # Rate limiting middleware
│   ├── auth.py           # Authentication middleware
│   ├── cors.py           # CORS handling
│   └── validation.py     # Request validation
└── routes/               # API endpoints
    ├── README.md         # Routes guide
    ├── chat.py           # Chat endpoints
    ├── health.py         # Health check endpoints
    └── admin.py          # Admin/debug endpoints
```

## 🚀 Quick Start

1. **Set Environment Variables**:
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   OPENAI_API_KEY=your_openai_key
   REDIS_URL=redis://localhost:6379  # Optional
   ```

2. **Run the API**:
   ```bash
   cd /Users/melville/Documents/qc_agent_backend
   python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test the API**:
   ```bash
   curl http://localhost:8000/health
   ```

## 🔧 Configuration

The API uses dependency injection for all components. Configuration happens in `config/container.py` during startup.

### Key Components Injected:
- **Database Client**: Supabase connection
- **Redis Client**: For rate limiting and caching (optional)
- **Orchestrator**: Main agent coordinator
- **Tool Registry**: Dynamic tool management

## 📝 Adding New Endpoints

1. Create new route file in `routes/`
2. Import and include in `main.py`
3. Use dependency injection for database/orchestrator access

Example:
```python
# routes/new_endpoint.py
from fastapi import APIRouter, Depends, Request

router = APIRouter()

@router.post("/new-feature")
async def new_feature(request: Request, payload: dict):
    # Access injected dependencies
    orchestrator = request.app.state.orchestrator
    database = request.app.state.container.get_database()
    
    # Your logic here
    return {"result": "success"}
```

## 🛡️ Security

- **Rate Limiting**: Applied via middleware
- **Authentication**: JWT validation (see auth/README.md)
- **CORS**: Configured for frontend domains
- **Validation**: Request/response validation

## 📊 Monitoring

- **Health Checks**: `/health` endpoint
- **Metrics**: `/metrics` endpoint  
- **Admin**: `/admin/*` endpoints for debugging

## 🔗 Related Components

- **Orchestration**: `../orchestration/` - Agent coordination
- **Agents**: `../agents/` - LLM implementations
- **Tools**: `../tools/` - Dynamic tool system
- **Analytics**: `../analytics/` - Cost tracking
