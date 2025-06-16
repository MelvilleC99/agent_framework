# src/api/routes/health.py
"""
Health Check Routes

Provides health status and system monitoring endpoints.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request
from pydantic import BaseModel

logger = logging.getLogger("health")

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    environment: str
    database_connected: bool
    redis_connected: bool
    services: Dict[str, str]


@router.get("/", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Basic health check endpoint.
    
    Returns:
        Health status of the application and its dependencies
    """
    try:
        # Access dependencies
        container = request.app.state.container
        settings = request.app.state.settings
        
        # Check database connection
        database_connected = False
        try:
            db_client = container.get_database()
            # Simple ping to check connection
            response = db_client.table("agent_usage_logs").select("id").limit(1).execute()
            database_connected = True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
        
        # Check Redis connection
        redis_connected = False
        try:
            redis_client = container.get_redis()
            if redis_client:
                await redis_client.ping()
                redis_connected = True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
        
        # Determine overall status
        status = "healthy" if database_connected else "degraded"
        
        return HealthResponse(
            status=status,
            version="1.0.0",
            environment=settings.environment,
            database_connected=database_connected,
            redis_connected=redis_connected,
            services={
                "orchestrator": "healthy",
                "tool_registry": "healthy",
                "database": "healthy" if database_connected else "unhealthy",
                "redis": "healthy" if redis_connected else "unhealthy"
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            environment="unknown",
            database_connected=False,
            redis_connected=False,
            services={"error": str(e)}
        )


@router.get("/ready")
async def readiness_check(request: Request):
    """
    Readiness check for Kubernetes/Docker.
    
    Returns 200 if ready to serve traffic, 503 if not.
    """
    try:
        container = request.app.state.container
        
        # Check if essential services are ready
        database_ready = True
        try:
            db_client = container.get_database()
            db_client.table("agent_usage_logs").select("id").limit(1).execute()
        except Exception:
            database_ready = False
        
        if database_ready:
            return {"status": "ready"}
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Service not ready")
            
    except Exception as e:
        from fastapi import HTTPException
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/Docker.
    
    Returns 200 if the application is alive.
    """
    return {"status": "alive"}
