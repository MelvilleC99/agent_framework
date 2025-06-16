# src/api/routes/admin.py
"""
Admin and Debug Routes

Provides administrative endpoints for debugging and monitoring.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("admin")

router = APIRouter()


@router.get("/tools")
async def list_tools(request: Request):
    """List all available tools in the registry."""
    try:
        container = request.app.state.container
        tool_registry = container.get_tool_registry()
        
        available_tools = tool_registry.get_all_tools()
        tool_count_by_category = {}
        for category, tools in tool_registry.categories.items():
            tool_count_by_category[category] = len(tools)
        
        return {
            "tool_count": len(available_tools),
            "categories": tool_count_by_category,
            "tools": available_tools
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/{tool_name}")
async def get_tool_details(tool_name: str, request: Request):
    """Get detailed information about a specific tool."""
    try:
        container = request.app.state.container
        tool_registry = container.get_tool_registry()
        
        tool_info = tool_registry.get_tool_info(tool_name)
        if not tool_info:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        # Remove function object for serialization
        safe_info = tool_info.copy()
        safe_info.pop("function", None)
        
        return safe_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/category/{category}")
async def list_tools_by_category(category: str, request: Request):
    """List all tools in a specific category."""
    try:
        container = request.app.state.container
        tool_registry = container.get_tool_registry()
        
        tools_in_category = tool_registry.get_tools_by_category(category)
        tool_details = []
        
        for tool_name in tools_in_category:
            tool_info = tool_registry.get_tool_info(tool_name)
            if tool_info:
                safe_info = tool_info.copy()
                safe_info.pop("function", None)
                tool_details.append(safe_info)
        
        return {
            "category": category,
            "tool_count": len(tool_details),
            "tools": tool_details
        }
    except Exception as e:
        logger.error(f"Error listing tools by category: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}


@router.post("/tools/execute")
async def execute_tool(request_data: ToolExecutionRequest, request: Request):
    """Execute a tool with provided parameters (admin only)."""
    try:
        container = request.app.state.container
        tool_registry = container.get_tool_registry()
        
        from ...tool_registry.executor import ToolExecutor
        executor = ToolExecutor(tool_registry)
        
        result = executor.execute(request_data.tool_name, request_data.parameters)
        
        return {
            "tool_name": request_data.tool_name,
            "parameters": request_data.parameters,
            "result": result,
            "execution_successful": result.get("success", True)
        }
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/functions")
async def list_function_definitions(request: Request):
    """Get OpenAI function definitions for all tools."""
    try:
        container = request.app.state.container
        tool_registry = container.get_tool_registry()
        
        from ...tool_registry.function_generator import FunctionGenerator
        generator = FunctionGenerator(tool_registry)
        
        functions = generator.generate_function_definitions()
        validation = generator.validate_function_definitions()
        
        return {
            "function_count": len(functions),
            "functions": functions,
            "validation": validation
        }
    except Exception as e:
        logger.error(f"Error listing function definitions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/discovery-help")
async def get_discovery_help(request: Request):
    """Get help information about tool discovery rules."""
    try:
        container = request.app.state.container
        tool_registry = container.get_tool_registry()
        
        from ...tool_registry.discovery import ToolDiscovery
        discovery = ToolDiscovery(tool_registry)
        
        help_text = discovery.get_discovery_help()
        
        return {
            "help": help_text,
            "current_rules": {
                "naming_convention": "Functions must end with '_tool'",
                "docstring_required": True,
                "return_type_recommended": "dict",
                "skipped_patterns": ["_*", "main", "test", "setup", "init"]
            },
            "categories": {
                "data_retrieval": "Database queries, API calls, file reading",
                "analysis": "Data analysis, calculations, reporting",
                "action": "Data modification, system actions, updates", 
                "maintenance": "Health checks, cleanup, diagnostics",
                "notification": "Alerts, messages, communications"
            }
        }
    except Exception as e:
        logger.error(f"Error getting discovery help: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discover-tools")
async def discover_tools(request: Request, directory: str = None):
    """Discover and register tools from a directory."""
    try:
        if not directory:
            # Use configured tools directory
            settings = request.app.state.settings
            import os
            directory = os.path.join(os.getcwd(), settings.tools_directory)
            
        container = request.app.state.container
        tool_registry = container.get_tool_registry()
        
        discovered_count = tool_registry.auto_discover_tools(directory, "data_retrieval")
        
        return {
            "directory": directory,
            "tools_discovered": discovered_count,
            "total_tools": len(tool_registry.get_tool_names())
        }
    except Exception as e:
        logger.error(f"Error discovering tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config(request: Request):
    """Get current application configuration (safe fields only)."""
    try:
        settings = request.app.state.settings
        
        # Return safe configuration fields only
        safe_config = {
            "environment": settings.environment,
            "debug": settings.debug,
            "agent_name": settings.agent_name,
            "rate_limit_per_minute": settings.rate_limit_per_minute,
            "max_session_duration_minutes": settings.max_session_duration_minutes,
            "max_context_history": settings.max_context_history,
            "cors_origins": settings.cors_origins,
            "redis_configured": bool(settings.redis_url)
        }
        
        return safe_config
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-token-usage")
async def reset_token_usage(request: Request):
    """Reset token usage statistics."""
    try:
        orchestrator = request.app.state.orchestrator
        
        # Reset token tracking
        from ...usage_tracking.token_tracker import token_tracker
        token_tracker.reset_session()
        
        return {"status": "Token usage statistics reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting token usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics(request: Request):
    """Get basic application metrics."""
    try:
        # This would typically integrate with a metrics system like Prometheus
        # For now, return basic stats
        
        from ...api.routes.chat import active_sessions
        
        metrics = {
            "active_sessions": len(active_sessions),
            "total_requests": "Not implemented",  # Would track via middleware
            "average_response_time": "Not implemented",  # Would track via middleware
            "error_rate": "Not implemented"  # Would track via middleware
        }
        
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
