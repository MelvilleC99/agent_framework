# API Routes

This folder contains all API endpoint definitions.

## 📁 Files

- **`chat.py`** - Chat endpoints for agent interaction
- **`health.py`** - Health check and status endpoints  
- **`admin.py`** - Admin and debugging endpoints

## 🔧 How Routes Work

### Dependency Access
All routes can access injected dependencies through the FastAPI app state:

```python
@router.post("/chat")
async def chat_endpoint(request: Request, payload: dict):
    # Access dependencies
    orchestrator = request.app.state.orchestrator
    database = request.app.state.container.get_database()
    settings = request.app.state.settings
```

### Error Handling
Use structured error responses:

```python
from fastapi import HTTPException

@router.post("/endpoint")
async def my_endpoint():
    try:
        # Your logic
        pass
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")
```

### Request/Response Models
Define Pydantic models for request/response validation:

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    execution_time: float
```
