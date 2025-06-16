# src/tool_registry/tool_context.py
"""
Tool Context System - Load detailed prompts for complex tools
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("tool_context")


class ToolContextManager:
    """
    Manages detailed context/prompts for complex tools.
    
    Allows agents to request additional context about tools
    before deciding whether to use them.
    """
    
    def __init__(self, prompts_directory: str = "src/prompts/tools"):
        """
        Initialize tool context manager.
        
        Args:
            prompts_directory: Directory containing tool prompt files
        """
        self.prompts_directory = prompts_directory
        self.context_cache = {}
        logger.info(f"ToolContextManager initialized with directory: {prompts_directory}")
    
    def get_tool_context(self, tool_name: str) -> Optional[str]:
        """
        Get detailed context/prompt for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Detailed context string or None if not found
        """
        # Check cache first
        if tool_name in self.context_cache:
            return self.context_cache[tool_name]
        
        # Look for tool-specific prompt file
        context_file = os.path.join(self.prompts_directory, f"{tool_name}.txt")
        
        if os.path.exists(context_file):
            try:
                with open(context_file, 'r') as f:
                    context = f.read().strip()
                
                # Cache the context
                self.context_cache[tool_name] = context
                logger.debug(f"Loaded context for tool: {tool_name}")
                return context
                
            except Exception as e:
                logger.error(f"Error loading context for {tool_name}: {e}")
                return None
        else:
            logger.debug(f"No context file found for tool: {tool_name}")
            return None
    
    def register_context_tool(self, tool_registry):
        """
        Register the get_tool_context function as a tool.
        
        Args:
            tool_registry: Tool registry to register with
        """
        def get_tool_context_tool(tool_name: str) -> Dict[str, Any]:
            """
            Get detailed context and usage information for a specific tool.
            
            Use this when you need more information about how to use a tool
            or what it's designed for before calling it.
            
            Args:
                tool_name: Name of the tool to get context for
                
            Returns:
                Tool context and usage information
            """
            context = self.get_tool_context(tool_name)
            
            if context:
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "context": context,
                    "has_detailed_context": True
                }
            else:
                # Fallback to basic tool info from registry
                tool_info = tool_registry.get_tool_info(tool_name)
                if tool_info:
                    return {
                        "success": True,
                        "tool_name": tool_name,
                        "context": tool_info.get("description", "No description available"),
                        "has_detailed_context": False,
                        "basic_info": {
                            "category": tool_info.get("category"),
                            "parameters": tool_info.get("parameters", {})
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Tool '{tool_name}' not found in registry"
                    }
        
        # Register the context tool
        tool_registry.register_tool(
            name="get_tool_context",
            function=get_tool_context_tool,
            description="Get detailed context and usage information for a specific tool before using it",
            category="maintenance"
        )
        
        logger.info("Registered get_tool_context tool")


# Global instance
tool_context_manager = ToolContextManager()
