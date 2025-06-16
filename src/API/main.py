# src/api/main.py
"""
FastAPI Application with Dependency Injection
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Import configuration and dependencies
from .config.container import Container
from .config.settings import get_settings
from .middleware.rate_limiter import RateLimitMiddleware
from .middleware.cors import setup_cors

# Import routes
from .routes import chat, health, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown."""
    # Startup
    logger.info("🚀 Starting QC Agent API...")
    
    try:
        # 1. Load settings
        settings = get_settings()
        logger.info(f"📋 Loaded settings for environment: {settings.environment}")
        
        # 2. Initialize dependency container
        container = Container()
        await container.initialize(settings)
        logger.info("✅ Dependency container initialized")
        
        # 3. Initialize orchestrator
        orchestrator = await container.get_orchestrator()
        logger.info("✅ Agent orchestrator initialized")
        
        # 4. Store in app state for route access
        app.state.container = container
        app.state.orchestrator = orchestrator
        app.state.settings = settings
        
        logger.info("🎯 QC Agent API ready!")
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        raise
    
    # Shutdown
    logger.info("🛑 Shutting down QC Agent API...")
    if hasattr(app.state, 'container'):
        await app.state.container.cleanup()
        logger.info("✅ Resources cleaned up")


# Create FastAPI application
app = FastAPI(
    title="QC Agent API",
    description="Quality Control Agent Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS
setup_cors(app)

# Add middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(chat.router, prefix="/api/agent", tags=["chat"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the QC Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting QC Agent API...")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
