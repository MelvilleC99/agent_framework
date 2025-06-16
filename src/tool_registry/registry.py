# src/tools/registry.py
"""
Tool Registry for QC Agent Template

Based on the Industrial Engineering Agent tool_registry.py but enhanced
with dependency injection and better error handling for template reuse.
"""

import logging
import inspect
import json
import os
from typing import Dict, Any, List, Callable, Optional, Union, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from langchain.agents import Tool

logger = logging.getLogger("tools.registry")


class ToolRegistry:
    """
    Registry for tools used in the agent system.
    
    Manages tool definitions, documentation, and execution,
    providing a standardized interface for tools across agents.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Dict[str, Any]] = {}
        
        # Tool categories for organization and filtering
        # These buckets help organize tools by their primary purpose
        self.categories = {
            "data_retrieval": [],    # Database queries, API calls, file reading
            "analysis": [],          # Data analysis, calculations, reporting  
            "action": [],           # Data modification, system actions, updates
            "maintenance": [],      # Health checks, cleanup, diagnostics
            "notification": []      # Alerts, messages, communications
        }
        
        self._discovery = None  # Lazy loaded
        logger.info("ToolRegistry initialized with 5 categories")
    
    def _auto_categorize_tool(self, tool_name: str, description: str) -> str:
        """
        Auto-categorize a tool based on its name and description.
        
        This provides intelligent defaults when no category is specified.
        
        Args:
            tool_name: Name of the tool
            description: Tool description
            
        Returns:
            Suggested category
        """
        name_lower = tool_name.lower()
        desc_lower = description.lower()
        
        # Analysis patterns
        if any(word in name_lower for word in ["analyze", "calculate", "report", "summary", "metric"]):
            return "analysis"
        if any(word in desc_lower for word in ["analyze", "calculate", "report", "metric", "statistic"]):
            return "analysis"
            
        # Data retrieval patterns  
        if any(word in name_lower for word in ["query", "get", "fetch", "read", "search", "find"]):
            return "data_retrieval"
        if any(word in desc_lower for word in ["query", "retrieve", "fetch", "search", "database"]):
            return "data_retrieval"
            
        # Action patterns
        if any(word in name_lower for word in ["update", "create", "delete", "modify", "save", "write"]):
            return "action"
        if any(word in desc_lower for word in ["update", "create", "delete", "modify", "insert"]):
            return "action"
            
        # Maintenance patterns
        if any(word in name_lower for word in ["health", "check", "status", "diagnostic", "cleanup"]):
            return "maintenance"
        if any(word in desc_lower for word in ["health", "status", "diagnostic", "maintenance"]):
            return "maintenance"
            
        # Notification patterns
        if any(word in name_lower for word in ["notify", "alert", "send", "email", "message"]):
            return "notification"
        if any(word in desc_lower for word in ["notify", "alert", "send", "message", "email"]):
            return "notification"
        
        # Default to data_retrieval
        return "data_retrieval"    
    def register_tool(
        self, 
        name: str, 
        function: Callable, 
        description: str, 
        category: Optional[str] = None,
        parameters: Optional[Dict[str, Dict[str, Any]]] = None,
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Register a tool with the registry.
        
        Args:
            name: The tool's name
            function: The function that implements the tool
            description: A description of what the tool does
            category: The tool category (auto-detected if not provided)
            parameters: Parameter descriptions and types
            examples: Example usages of the tool
        """
        # Auto-generate parameters if not provided
        if parameters is None:
            parameters = self._generate_parameters(function)
        
        # Auto-categorize if no category provided
        if category is None:
            category = self._auto_categorize_tool(name, description)
            logger.info(f"Auto-categorized '{name}' as '{category}'")
        
        # Prevent duplicate registration
        if name in self.tools:
            logger.warning(f"Tool '{name}' already registered - skipping duplicate")
            return
        
        tool_info = {
            "name": name,
            "function": function,
            "description": description,
            "category": category,
            "parameters": parameters,
            "examples": examples or []
        }
        
        self.tools[name] = tool_info
        
        # Add to category list
        if category in self.categories:
            self.categories[category].append(name)
        else:
            # Create new category if it doesn't exist
            self.categories[category] = [name]
            logger.info(f"Created new category: {category}")
            
        logger.info(f"✅ Registered tool: {name} in category '{category}'")
    
    def _generate_parameters(self, function: Callable) -> Dict[str, Dict[str, Any]]:
        """
        Generate parameter information from function signature.
        
        Args:
            function: The function to analyze
            
        Returns:
            A dictionary of parameter information
        """
        params = {}
        
        try:
            signature = inspect.signature(function)
            
            for param_name, param in signature.parameters.items():
                # Skip 'self' parameter
                if param_name == 'self':
                    continue                    
                param_info = {
                    "type": "string",  # Default type
                    "description": f"Parameter: {param_name}",
                    "required": param.default == inspect.Parameter.empty
                }
                
                # Try to extract type annotation
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == str:
                        param_info["type"] = "string"
                    elif param.annotation == int:
                        param_info["type"] = "integer"
                    elif param.annotation == float:
                        param_info["type"] = "number"
                    elif param.annotation == bool:
                        param_info["type"] = "boolean"
                    elif hasattr(param.annotation, '__origin__'):
                        # Handle generic types like List, Dict
                        if param.annotation.__origin__ is list:
                            param_info["type"] = "array"
                        elif param.annotation.__origin__ is dict:
                            param_info["type"] = "object"
                
                params[param_name] = param_info
                
        except Exception as e:
            logger.warning(f"Could not generate parameters for {function.__name__}: {e}")
            
        return params
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a tool.
        
        Args:
            name: The tool's name
            
        Returns:
            Tool information dictionary or None if not found
        """
        return self.tools.get(name)
    
    def execute_tool(self, name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a tool with the given parameters.
        
        Args:
            name: The tool's name
            parameters: Tool parameters
            
        Returns:
            The tool's result
            
        Raises:
            ValueError: If the tool is not found
        """
        tool_info = self.tools.get(name)
        if not tool_info:
            logger.error(f"Tool not found: {name}")
            raise ValueError(f"Tool not found: {name}")
        
        function = tool_info["function"]        
        try:
            # Log tool execution
            logger.info(f"Executing tool: {name} with parameters: {json.dumps(parameters, default=str)}")
            
            # Execute the tool
            result = function(**parameters)
            
            # Log success
            logger.info(f"Tool {name} executed successfully")
            
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
            raise
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """
        Get all tool names in a category.
        
        Args:
            category: The category name
            
        Returns:
            List of tool names
        """
        return self.categories.get(category, [])
    
    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered tools.
        
        Returns:
            Dictionary of all tools
        """
        # Return a copy without the function objects
        result = {}
        for name, info in self.tools.items():
            tool_copy = info.copy()
            tool_copy.pop("function", None)
            result[name] = tool_copy
            
        return result
    
    def get_tool_names(self) -> List[str]:
        """
        Get names of all registered tools.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def get_tool_function(self, name: str) -> Optional[Callable]:
        """
        Get the function for a specific tool.
        
        Args:
            name: The tool's name
            
        Returns:
            The tool function or None if not found
        """
        tool_info = self.tools.get(name)
        if tool_info:
            return tool_info["function"]
        return None    
    def get_langchain_tools(self) -> List['Tool']:
        """
        Convert tools to Langchain Tool objects.
        
        Returns:
            List of Langchain Tool objects
        """
        try:
            from langchain.agents import Tool
            
            langchain_tools = []
            for name, tool_info in self.tools.items():
                langchain_tools.append(
                    Tool(
                        name=name,
                        func=tool_info["function"],
                        description=tool_info["description"]
                    )
                )
            
            logger.info(f"Converted {len(langchain_tools)} tools to Langchain tools")
            return langchain_tools
            
        except ImportError:
            logger.error("Could not import langchain.agents.Tool")
            return []
    
    def generate_tool_descriptions(self) -> str:
        """
        Generate formatted descriptions of all tools.
        
        Returns:
            Formatted tool descriptions
        """
        descriptions = []
        
        for category, tools in self.categories.items():
            if not tools:
                continue
                
            descriptions.append(f"## {category.upper()} TOOLS")
            
            for tool_name in tools:
                tool = self.tools.get(tool_name)
                if not tool:
                    continue
                    
                descriptions.append(f"### {tool_name}")
                descriptions.append(tool["description"])
                
                if tool["parameters"]:
                    descriptions.append("Parameters:")
                    for param_name, param_info in tool["parameters"].items():
                        required = "Required" if param_info.get("required", False) else "Optional"
                        descriptions.append(f"- {param_name} ({param_info.get('type', 'string')}): {param_info.get('description', '')} [{required}]")
                
                descriptions.append("")
        
        return "\n".join(descriptions)
    
    def auto_discover_tools(self, directory: str, category: str = "maintenance") -> int:
        """
        Auto-discover and register tools from a directory.
        
        Args:
            directory: Path to scan for tools
            category: Category to assign to discovered tools
            
        Returns:
            Number of tools discovered and registered
        """
        if not self._discovery:
            from .discovery import ToolDiscovery
            self._discovery = ToolDiscovery(tool_registry=self)
            
        try:
            tools_found = self._discovery.discover_tools_in_directory(directory, category)
            logger.info(f"Auto-discovered {tools_found} tools from {directory}")
            return tools_found
        except Exception as e:
            logger.error(f"Error in auto-discovery: {e}")
            return 0
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the tool registry.
        
        Returns:
            Health status information
        """
        return {
            "status": "healthy",
            "tool_count": len(self.tools),
            "categories": {cat: len(tools) for cat, tools in self.categories.items()},
            "tools": list(self.tools.keys())
        }


# Create global tool registry instance
tool_registry = ToolRegistry()


def register_basic_tools():
    """Register basic tools for the QC agent template."""
    
    def get_current_time() -> str:
        """Get the current date and time."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def health_check() -> Dict[str, str]:
        """Basic health check tool."""
        return {"status": "healthy", "timestamp": get_current_time()}
    
    # Register basic tools only if not already registered (prevent duplicates)
    if "get_current_time" not in tool_registry.get_tool_names():
        tool_registry.register_tool(
            name="get_current_time",
            function=get_current_time,
            description="Get the current date and time in ISO format",
            category="data_retrieval"
        )
    
    if "health_check" not in tool_registry.get_tool_names():
        tool_registry.register_tool(
            name="health_check",
            function=health_check,
            description="Perform a basic health check",
            category="maintenance"
        )
    
    # Register tool context system
    from .tool_context import tool_context_manager
    tool_context_manager.register_context_tool(tool_registry)
    
    logger.info("Basic tools and context system registered")


# Register basic tools when module loads (only once)
register_basic_tools()