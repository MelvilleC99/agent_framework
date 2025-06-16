# src/tools/__init__.py
"""
Tools Layer for QC Agent Template

This package provides the complete tools system including:
- Tool Registry: Centralized tool management
- Tool Executor: Generic tool execution
- Tool Discovery: Automatic tool discovery
- Function Generator: OpenAI function definitions

Based on the excellent Industrial Engineering Agent tool architecture.
"""

import logging

logger = logging.getLogger("tools")

# Import main components
from .registry import ToolRegistry, tool_registry
from .executor import ToolExecutor
from .discovery import ToolDiscovery
from .function_generator import FunctionGenerator

# Export main interfaces
__all__ = [
    "ToolRegistry",
    "tool_registry",
    "ToolExecutor", 
    "ToolDiscovery",
    "FunctionGenerator"
]

logger.info("Tools layer initialized")
