# src/agents/chatgpt/response_handler.py
"""
Response Processing and Formatting for ChatGPT Agent

Based on the Industrial Engineering Agent's response_handler.py but enhanced
with better error handling and formatting options.
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("response_handler")


class ResponseHandler:
    """
    Processes OpenAI responses and formats output for users.
    
    This component handles:
    - Function call result processing
    - Response formatting and validation
    - Table data conversion to markdown
    - Error handling and fallbacks
    """
    
    def __init__(self, tool_registry=None):
        """Initialize the response handler."""
        self.tool_registry = tool_registry
        logger.info("ResponseHandler initialized")
    
    def format_function_result(self, result: Any, function_name: str) -> str:
        """
        Format a function call result for display.
        
        Args:
            result: The raw function result
            function_name: Name of the function that was called
            
        Returns:
            Formatted result string
        """
        try:
            # Handle different result types
            if isinstance(result, str):
                return result
            elif isinstance(result, dict):
                # Check if it's a structured query result
                if "data" in result and isinstance(result["data"], list):
                    return self._format_structured_data(result, function_name)
                elif "error" in result:
                    return f"Error from {function_name}: {result['error']}"
                else:
                    # Format as JSON for other dicts
                    try:
                        json_str = json.dumps(result, indent=2)
                        return f"Result from {function_name}:\n```json\n{json_str}\n```"
                    except:
                        return f"Result from {function_name}: {str(result)}"
            elif isinstance(result, list):
                return self._format_list_data(result, function_name)
            else:
                return f"Result from {function_name}: {str(result)}"
                
        except Exception as e:
            logger.error(f"Error formatting function result: {e}")
            return f"Error formatting result from {function_name}: {str(e)}"
    
    def _format_structured_data(self, result: Dict[str, Any], function_name: str) -> str:
        """Format structured data result."""
        try:
            data = result["data"]
            if not data:
                return f"No data found for {function_name}."
            
            # Check if this should be a table
            if self._should_be_table(data):
                return self._convert_to_markdown_table(data, function_name)
            else:
                return self._format_as_list(data, function_name)
                
        except Exception as e:
            logger.error(f"Error formatting structured data: {e}")
            return f"Error formatting data from {function_name}: {str(e)}"
    
    def _should_be_table(self, data: list) -> bool:
        """Determine if data should be displayed as a table."""
        if not data or not isinstance(data, list):
            return False
        
        # Table criteria
        return (
            len(data) >= 2 and  # Multiple items
            isinstance(data[0], dict) and  # Dictionary structure
            len(data[0]) >= 2  # Multiple fields
        )
    
    def _convert_to_markdown_table(self, data: list, function_name: str) -> str:
        """Convert data to markdown table format."""
        try:
            if not data:
                return f"No data found for {function_name}."
            
            # Get headers from first item
            headers = list(data[0].keys())
            
            # Create header row
            header_row = "| " + " | ".join(headers) + " |"
            separator = "|" + "|".join(["---" for _ in headers]) + "|"
            
            # Create data rows
            data_rows = []
            for row in data:
                row_values = []
                for header in headers:
                    value = str(row.get(header, ""))
                    # Truncate long values
                    if len(value) > 50:
                        value = value[:47] + "..."
                    row_values.append(value)
                data_rows.append("| " + " | ".join(row_values) + " |")
            
            # Combine into markdown table
            markdown_table = "\n".join([header_row, separator] + data_rows)
            return f"Here are the results from {function_name}:\n\n{markdown_table}\n\n*Total: {len(data)} records*"
            
        except Exception as e:
            logger.error(f"Error creating markdown table: {e}")
            return f"Error formatting table data from {function_name}: {str(e)}"
    
    def _format_as_list(self, data: list, function_name: str) -> str:
        """Format data as a numbered list."""
        try:
            if not data:
                return f"No data found for {function_name}."
            
            result = []
            for i, item in enumerate(data, 1):
                if isinstance(item, dict):
                    # Format dictionary items
                    item_text = f"{i}. "
                    key_fields = list(item.keys())[:3]  # First 3 fields
                    
                    for j, field in enumerate(key_fields):
                        value = str(item.get(field, ""))
                        if len(value) > 50:
                            value = value[:47] + "..."
                        
                        if j == 0:
                            item_text += f"**{value}**"
                        else:
                            field_name = field.replace('_', ' ').title()
                            item_text += f", {field_name}: {value}"
                    
                    result.append(item_text)
                else:
                    result.append(f"{i}. {str(item)}")
            
            formatted_list = "\n".join(result)
            return f"Results from {function_name}:\n\n{formatted_list}\n\n*Total: {len(data)} items*"
            
        except Exception as e:
            logger.error(f"Error formatting list: {e}")
            return f"Error formatting list data from {function_name}: {str(e)}"
    
    def _format_list_data(self, result: list, function_name: str) -> str:
        """Format list result data."""
        try:
            if not result:
                return f"No results found for {function_name}."
            
            if len(result) == 1:
                # Single item
                return f"Result from {function_name}: {str(result[0])}"
            else:
                # Multiple items
                return self._format_as_list(result, function_name)
                
        except Exception as e:
            logger.error(f"Error formatting list data: {e}")
            return f"Error formatting results from {function_name}: {str(e)}"
    
    def validate_function_result(self, result: Any) -> bool:
        """
        Validate that a function result is properly formatted.
        
        Args:
            result: Function result to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check for basic validity
            if result is None:
                return False
            
            # If it's a dict, check for required structure
            if isinstance(result, dict):
                # Error results should have error key
                if "error" in result:
                    return isinstance(result["error"], str)
                
                # Data results should have proper structure
                if "data" in result:
                    return isinstance(result["data"], (list, dict))
            
            # Other types are generally valid
            return True
            
        except Exception as e:
            logger.error(f"Error validating function result: {e}")
            return False
    
    def truncate_content(self, content: str, max_length: int = 1000) -> str:
        """
        Truncate content to a maximum length.
        
        Args:
            content: Content to truncate
            max_length: Maximum length
            
        Returns:
            Truncated content
        """
        if len(content) <= max_length:
            return content
        
        return content[:max_length-3] + "..."
