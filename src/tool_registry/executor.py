# src/tools/executor.py
"""
Generic Tool Executor for QC Agent Template

Based on the Industrial Engineering Agent tool_executor.py but enhanced
with better error handling and result formatting.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("tools.executor")


class ToolExecutor:
    """
    Generic tool executor that routes tool calls to appropriate handlers.
    
    Replaces manual if/elif execution chains with simple, generic interface.
    """
    
    def __init__(self, tool_registry=None):
        """
        Initialize the tool executor.
        
        Args:
            tool_registry: Tool registry instance
        """
        self.tool_registry = tool_registry
        logger.info("ToolExecutor initialized")
    
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute any tool by name with provided arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.tool_registry:
            logger.error("No tool registry available")
            return {"error": "Tool registry not available", "success": False}
        
        try:
            # Execute via registry (registry handles its own logging)
            result = self.tool_registry.execute_tool(tool_name, arguments)
            
            # Format result consistently
            formatted_result = self._format_result(result, tool_name)
            
            # Only log at executor level for errors or summary
            if not formatted_result.get("success", True):
                logger.warning(f"Tool {tool_name} execution failed")
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Executor error for tool {tool_name}: {e}")
            return {
                "error": f"Tool execution failed: {str(e)}",
                "success": False,
                "tool_name": tool_name,
                "arguments": arguments
            }    
    def _format_result(self, result: Any, tool_name: str) -> Dict[str, Any]:
        """
        Format tool result consistently.
        
        Args:
            result: Raw tool result
            tool_name: Name of the executed tool
            
        Returns:
            Formatted result dictionary
        """
        # If result is already a dict with standard format, return as-is
        if isinstance(result, dict) and ("success" in result or "error" in result):
            return result
        
        # Wrap simple results in standard format
        return {
            "success": True,
            "result": result,
            "tool_name": tool_name
        }
    
    def is_tool_available(self, tool_name: str) -> bool:
        """
        Check if a tool is available for execution.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if tool is available, False otherwise
        """
        if not self.tool_registry:
            return False
        tool_info = self.tool_registry.get_tool_info(tool_name)
        return tool_info is not None
    
    def get_available_tools(self) -> list:
        """
        Get list of all available tools.
        
        Returns:
            List of available tool names
        """
        if not self.tool_registry:
            return []
        return self.tool_registry.get_tool_names()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information or None if not found
        """
        if not self.tool_registry:
            return None
        return self.tool_registry.get_tool_info(tool_name)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the tool executor.
        
        Returns:
            Health status information
        """
        status = {
            "status": "healthy" if self.tool_registry else "unhealthy",
            "registry_available": self.tool_registry is not None
        }
        
        if self.tool_registry:
            registry_health = self.tool_registry.health_check()
            status.update(registry_health)
        
        return status