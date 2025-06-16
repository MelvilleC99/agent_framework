# src/agents/chatgpt/core_agent.py
"""
Core ChatGPT Agent - Enhanced Implementation

Based on the Industrial Engineering Agent's excellent modular ChatGPT implementation
but enhanced with dependency injection and better error handling.
"""

import os
import logging
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from ..base.agent_interface import BaseAgent
from .prompt_manager import PromptManager
from .message_builder import MessageBuilder
from .response_handler import ResponseHandler
from .session_detector import SessionDetector
from .context_helpers import ContextHelpers

logger = logging.getLogger("chatgpt_agent")


class ChatGPTAgent(BaseAgent):
    """
    Enhanced ChatGPT Agent with modular components.
    
    This agent coordinates specialized components to handle user queries
    while maintaining the excellent architecture from the Industrial Engineering Agent.
    """
    
    def __init__(self, 
                 tool_registry=None,
                 context_manager=None,
                 database=None,
                 model: str = "gpt-4o-mini",
                 max_tokens: int = 500):
        """
        Initialize the ChatGPT agent with all specialized components.
        
        Args:
            tool_registry: Tool registry for function execution
            context_manager: Context manager for conversation history
            database: Database client for persistence
            model: OpenAI model to use
            max_tokens: Maximum tokens for responses
        """
        super().__init__(tool_registry, context_manager, database)
        
        self.model = model
        self.max_tokens = max_tokens
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        try:
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            logger.error("OpenAI package not installed. Run 'pip install openai'")
            raise ImportError("OpenAI package not installed. Run 'pip install openai'")
        
        # Initialize specialized components
        self.prompt_manager = PromptManager()
        self.message_builder = MessageBuilder(self.prompt_manager)
        self.response_handler = ResponseHandler(tool_registry=tool_registry)
        self.session_detector = SessionDetector()
        self.context_helpers = ContextHelpers(context_manager)
        
        # Initialize usage tracker (will be set by orchestrator)
        self.usage_tracker = None
        
        logger.info(f"ChatGPT Agent initialized with model {self.model}")
    
    def initialize(self) -> bool:
        """
        Initialize the agent and its components.
        
        Returns:
            True if initialization successful
        """
        try:
            # Test OpenAI connection
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            
            self.is_initialized = True
            logger.info("ChatGPT agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ChatGPT agent: {e}")
            self.is_initialized = False
            return False
    
    def cleanup(self) -> None:
        """Clean up agent resources."""
        # OpenAI client doesn't need explicit cleanup
        self.is_initialized = False
        logger.info("ChatGPT agent cleanup complete")
    
    def refresh_date(self):
        """Refresh the cached date - useful for long-running sessions."""
        if self.prompt_manager:
            self.prompt_manager.refresh_date()
            logger.info("Date refreshed in ChatGPT agent")
    
    def process_query(self, 
                     query: str, 
                     conversation_history: Optional[List[Dict[str, str]]] = None,
                     conversation_id: Optional[str] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Process a user query - main orchestration method.
        
        Args:
            query: The user's query
            conversation_history: Optional conversation history
            conversation_id: Optional conversation ID for tracking
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with answer and metadata
        """
        if not self.is_initialized:
            if not self.initialize():
                return {
                    "error": "Agent not initialized",
                    "answer": "I'm sorry, I'm not ready to process queries right now."
                }
        
        # Refresh date for each query
        self.refresh_date()
        current_date = self.prompt_manager.get_current_date()
        logger.info(f"Processing query with current date: {current_date['formatted_date']}")
        
        try:
            # Build messages using message builder
            messages = self.message_builder.build_messages(query, conversation_history)
            
            # Get function definitions from tool registry
            functions = self._define_functions()
            
            # Log token estimate
            estimated_tokens = self._estimate_tokens(messages)
            logger.info(f"Estimated input tokens: {estimated_tokens}")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions if functions else None,
                function_call="auto" if functions else None,
                max_tokens=self.max_tokens
            )
            
            # Track token usage
            self._track_token_usage(response)
            
            # Track API call for cost tracking
            if conversation_id and self.usage_tracker:
                try:
                    self.usage_tracker.track_api_call(
                        conversation_id=conversation_id,
                        model=self.model,
                        input_tokens=getattr(response.usage, 'prompt_tokens', 0) if response.usage else 0,
                        output_tokens=getattr(response.usage, 'completion_tokens', 0) if response.usage else 0,
                        agent_type="chatgpt"
                    )
                except Exception as e:
                    logger.warning(f"Failed to track API call: {e}")
            
            message = response.choices[0].message
            
            # Handle function calls
            if message.function_call:
                return self._handle_function_call(message, messages, functions, conversation_id)
            
            # Handle direct responses
            return self._handle_direct_response(message, response)
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return {
                "error": str(e),
                "answer": f"I apologize, but I encountered an error while processing your query: {str(e)}"
            }
    
    def _define_functions(self) -> List[Dict[str, Any]]:
        """
        Define the functions that will be available to the GPT model.
        
        Returns:
            List of function definitions (auto-generated from tool registry)
        """
        if not self.tool_registry:
            logger.warning("No tool registry available for function definitions")
            return []
        
        try:
            # Generate functions from tool registry
            functions = []
            all_tools = self.tool_registry.get_all_tools()
            
            for tool_name, tool_info in all_tools.items():
                function_def = self._create_function_definition(tool_name, tool_info)
                if function_def:
                    functions.append(function_def)
            
            logger.info(f"Generated {len(functions)} function definitions")
            return functions
        except Exception as e:
            logger.error(f"Error generating functions: {e}")
            return []
    
    def _create_function_definition(self, tool_name: str, tool_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a single ChatGPT function definition from tool metadata."""
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
                        cleaned_properties[param_name] = cleaned_param
                        
                        # Check if this parameter is required
                        if param_info.get("required", False):
                            required_params.append(param_name)
                    else:
                        # Handle simple parameter definitions
                        cleaned_properties[param_name] = param_info
                
                function_def["parameters"]["properties"] = cleaned_properties
                
                if required_params:
                    function_def["parameters"]["required"] = required_params
            
            return function_def
            
        except Exception as e:
            logger.error(f"Error creating function definition for {tool_name}: {e}")
            return None
    
    def _handle_function_call(self, message, messages, functions, conversation_id):
        """Handle function call execution and response generation."""
        function_name = message.function_call.name
        try:
            function_args = json.loads(message.function_call.arguments)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid function arguments: {e}")
            return {
                "answer": f"I encountered an error with the function call arguments. Let me try to help you another way.",
                "error": "Invalid function arguments"
            }
        
        logger.info(f"Executing function: {function_name} with args: {function_args}")
        
        # Track tool usage for cost tracking
        if conversation_id and self.usage_tracker:
            try:
                self.usage_tracker.track_tool_usage(conversation_id, function_name)
            except Exception as e:
                logger.warning(f"Failed to track tool usage: {e}")
        
        # Execute the function using tool registry
        if self.tool_registry:
            try:
                result = self.tool_registry.execute_tool(function_name, function_args)
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                result = {"error": str(e)}
        else:
            result = {"error": "Tool registry not available"}
        
        # Store query metadata for follow-up context
        if self.context_helpers:
            self.context_helpers.store_query_metadata(function_name, function_args, result)
        
        # Check if the function failed
        if isinstance(result, dict) and "error" in result:
            return {
                "answer": f"I encountered an error while trying to {function_name}: {result['error']}. Let me try to help you another way.",
                "error": result["error"]
            }
        
        # Format the result using response handler
        formatted_content = self.response_handler.format_function_result(result, function_name)
        
        # Check if result is already formatted as markdown table
        if "Here are the" in formatted_content and "|" in formatted_content:
            return {
                "answer": formatted_content,
                "response": message
            }
        
        # Add function result to messages and get final response
        messages.extend([
            {
                "role": "assistant",
                "function_call": {"name": function_name, "arguments": json.dumps(function_args)},
                "content": None
            },
            {
                "role": "function",
                "name": function_name,
                "content": formatted_content[:1000]  # Limit function result size
            }
        ])
        
        # Get final response
        try:
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages[-6:],  # Only send recent messages
                functions=functions if functions else None,
                function_call="none",  # Force it to respond without calling another function
                max_tokens=self.max_tokens
            )
            
            # Track token usage
            self._track_token_usage(final_response)
            
            # Track final API call for cost tracking
            if conversation_id and self.usage_tracker:
                try:
                    self.usage_tracker.track_api_call(
                        conversation_id=conversation_id,
                        model=self.model,
                        input_tokens=getattr(final_response.usage, 'prompt_tokens', 0) if final_response.usage else 0,
                        output_tokens=getattr(final_response.usage, 'completion_tokens', 0) if final_response.usage else 0,
                        agent_type="chatgpt"
                    )
                except Exception as e:
                    logger.warning(f"Failed to track final API call: {e}")
            
            final_message = final_response.choices[0].message
            
            # Check for goodbye or follow-up indicators in the response
            response_content = final_message.content or ""
            
            result = {
                "answer": response_content,
                "response": final_message
            }
            
            # Check if the response indicates a need for DeepSeek
            if self.session_detector.requires_deepseek(response_content):
                result["requires_deepseek"] = True
            
            # Check if this is a goodbye message
            if self.session_detector.is_goodbye_message(response_content):
                result["is_goodbye"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error in final response generation: {e}")
            return {
                "answer": "I processed your request but encountered an error generating the final response.",
                "error": str(e)
            }
    
    def _handle_direct_response(self, message, response):
        """Handle direct response from ChatGPT without function calls."""
        content = message.content or "I apologize, but I couldn't generate a response."
        
        result = {
            "answer": content,
            "response": message
        }
        
        # Check for special indicators in the response
        if self.session_detector.requires_deepseek(content):
            result["requires_deepseek"] = True
        
        if self.session_detector.is_goodbye_message(content):
            result["is_goodbye"] = True
        
        return result
    
    def _estimate_tokens(self, messages: List[Dict]) -> int:
        """Estimate token count for messages."""
        try:
            message_contents = [str(m.get("content", "")) for m in messages if m.get("content")]
            message_text = " ".join(message_contents)
            return len(message_text) // 4  # Rough approximation
        except Exception:
            return 0
    
    def _track_token_usage(self, response: ChatCompletion) -> None:
        """Track token usage from OpenAI response."""
        try:
            # Import token tracker
            from ...usage_tracking.token_tracker import token_tracker
            token_tracker.track_openai_usage(response)
        except ImportError:
            logger.warning("Token tracker not available")
        except Exception as e:
            logger.warning(f"Failed to track token usage: {e}")
