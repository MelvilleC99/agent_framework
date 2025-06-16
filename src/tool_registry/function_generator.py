# src/tools/function_generator.py
"""
Function Definition Generator for QC Agent Template

Based on the Industrial Engineering Agent function_generator.py but enhanced
with better parameter handling and validation.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("tools.function_generator")


class FunctionGenerator:
    """
    Generates ChatGPT function definitions from tool registry metadata.
    
    Converts tool registry tools into OpenAI function calling format.
    """
    
    def __init__(self, tool_registry=None):
        """
        Initialize the function generator.
        
        Args:
            tool_registry: Tool registry instance
        """
        self.tool_registry = tool_registry
        logger.info("FunctionGenerator initialized")
    
    def generate_function_definitions(self) -> List[Dict[str, Any]]:
        """
        Generate ChatGPT function definitions from all registered tools.
        
        Returns:
            List of OpenAI function definitions
        """
        if not self.tool_registry:
            logger.warning("No tool registry provided")
            return []
        
        functions = []
        
        try:
            all_tools = self.tool_registry.get_all_tools()
            
            for tool_name, tool_info in all_tools.items():
                function_def = self._create_function_definition(tool_name, tool_info)
                if function_def:
                    functions.append(function_def)
                    
            logger.info(f"Generated {len(functions)} function definitions")
            return functions
            
        except Exception as e:
            logger.error(f"Error generating function definitions: {e}")
            return []
    def _create_function_definition(self, tool_name: str, tool_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a single ChatGPT function definition from tool metadata.
        
        Args:
            tool_name: Name of the tool
            tool_info: Tool information from registry
            
        Returns:
            OpenAI function definition or None if creation fails
        """
        try:
            function_def = {
                "name": tool_name,
                "description": tool_info.get("description", f"Execute {tool_name} tool"),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Add parameters from tool info
            tool_parameters = tool_info.get("parameters", {})
            if tool_parameters:
                cleaned_properties = {}
                required_params = []
                
                for param_name, param_info in tool_parameters.items():
                    if isinstance(param_info, dict):
                        # Copy param info but remove the "required" field
                        cleaned_param = {k: v for k, v in param_info.items() if k != "required"}
                        
                        # Ensure we have a valid type
                        if "type" not in cleaned_param:
                            cleaned_param["type"] = "string"
                            
                        cleaned_properties[param_name] = cleaned_param
                        
                        # Check if this parameter is required
                        if param_info.get("required", False):
                            required_params.append(param_name)
                    else:
                        # Handle simple parameter definitions
                        cleaned_properties[param_name] = {
                            "type": "string",
                            "description": str(param_info)
                        }
                
                function_def["parameters"]["properties"] = cleaned_properties
                
                if required_params:
                    function_def["parameters"]["required"] = required_params
            
            return function_def
            
        except Exception as e:
            logger.error(f"Error creating function definition for {tool_name}: {e}")
            return None
    
    def get_function_by_name(self, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific function definition by name.
        
        Args:
            function_name: Name of the function
            
        Returns:
            Function definition or None if not found
        """
        functions = self.generate_function_definitions()
        for func in functions:
            if func.get("name") == function_name:
                return func
        return None
    
    def get_function_names(self) -> List[str]:
        """
        Get list of all available function names.
        
        Returns:
            List of function names
        """
        functions = self.generate_function_definitions()
        return [func.get("name") for func in functions if func.get("name") is not None]
    
    def validate_function_definitions(self) -> Dict[str, Any]:
        """
        Validate all function definitions for correctness.
        
        Returns:
            Validation results with any issues found
        """
        functions = self.generate_function_definitions()
        issues = []
        valid_count = 0
        
        for func in functions:
            name = func.get("name", "unnamed")
            
            # Check required fields
            if not func.get("name"):
                issues.append(f"Function missing name: {func}")
                continue
                
            if not func.get("description"):
                issues.append(f"Function {name} missing description")
                
            if "parameters" not in func:
                issues.append(f"Function {name} missing parameters")
                continue
                
            # Validate parameters structure
            params = func["parameters"]
            if not isinstance(params, dict):
                issues.append(f"Function {name} has invalid parameters structure")
                continue
                
            if "type" not in params or params["type"] != "object":
                issues.append(f"Function {name} parameters missing type=object")
                
            if "properties" not in params:
                issues.append(f"Function {name} parameters missing properties")
                
            valid_count += 1
        
        return {
            "total_functions": len(functions),
            "valid_functions": valid_count,
            "issues": issues,
            "valid": len(issues) == 0
        }