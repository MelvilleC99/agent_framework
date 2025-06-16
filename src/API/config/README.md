# Configuration & Dependency Injection

This folder contains configuration management and dependency injection for the QC Agent API.

## 📁 Files

- **`container.py`** - Dependency injection container
- **`settings.py`** - Environment configuration 
- **`database.py`** - Database initialization

## 🔧 How It Works

### 1. Settings Loading
Environment variables are loaded and validated using Pydantic:

```python
from .settings import get_settings
settings = get_settings()
```

### 2. Dependency Injection
The container initializes and manages all dependencies:

```python
from .container import Container
container = Container()
await container.initialize(settings)
```

### 3. Access Dependencies
Dependencies are accessed through the container:

```python
database = container.get_database()
orchestrator = await container.get_orchestrator()
```

## 🌍 Environment Variables

Required:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase API key  
- `OPENAI_API_KEY` - Your OpenAI API key

Optional:
- `ENVIRONMENT` - "development" | "staging" | "production"
- `REDIS_URL` - Redis connection for rate limiting
- `RATE_LIMIT_PER_MINUTE` - Rate limit (default: 60)

## 🔗 Usage in Routes

```python
@router.post("/chat")
async def chat_endpoint(request: Request, payload: dict):
    # Access injected dependencies
    orchestrator = request.app.state.orchestrator
    database = request.app.state.container.get_database()
    settings = request.app.state.settings
    
    # Use dependencies
    result = await orchestrator.process_query(payload["query"])
    return result
```
