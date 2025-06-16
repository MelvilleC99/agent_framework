# src/agents/chatgpt/message_builder.py
"""
Message Building and Formatting for ChatGPT Agent

Based on the Industrial Engineering Agent's message_builder.py but enhanced
with better error handling and token optimization.
"""

import json
import logging
from typing import List, Dict, Optional
from openai.types.chat import ChatCompletionMessageParam

logger = logging.getLogger("message_builder")


class MessageBuilder:
    """
    Builds OpenAI-compatible messages from conversation history and user queries.
    
    This component handles:
    - Message formatting for OpenAI API
    - Date injection and acknowledgment
    - Conversation history management
    - Token optimization
    """
    
    def __init__(self, prompt_manager):
        """Initialize the message builder."""
        self.prompt_manager = prompt_manager
        logger.info("MessageBuilder initialized")
    
    def build_messages(self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> List[ChatCompletionMessageParam]:
        """
        Build OpenAI messages from query and conversation history.
        
        Args:
            query: The user's current query
            conversation_history: Optional conversation history
            
        Returns:
            List of ChatCompletionMessageParam for OpenAI API
        """
        try:
            messages: List[ChatCompletionMessageParam] = []
            
            # Start with system prompt
            system_prompt = self.prompt_manager.get_system_prompt()
            messages.append({"role": "system", "content": system_prompt})
            
            # ALWAYS inject the current date as a function message
            current_date = self.prompt_manager.get_current_date()
            date_message = {
                "role": "function",
                "name": "get_current_date",
                "content": json.dumps(current_date)
            }
            messages.append(date_message)  # type: ignore
            logger.debug(f"Injected date message: {date_message['content']}")
            
            # Add assistant acknowledgment of the date
            messages.append({
                "role": "assistant",
                "content": f"I understand that today is {current_date['formatted_date']} ({current_date['day_of_week']}). I'll use this date for all calculations."
            })
            
            # Add conversation history
            if conversation_history:
                recent_history = conversation_history[-6:]  # Last 3 user-assistant pairs
                for msg in recent_history:
                    role = msg.get("role")
                    content = msg.get("content")
                    
                    if role in ["user", "assistant", "system", "function"] and content is not None:
                        # Handle function messages with name
                        if role == "function" and msg.get("name"):
                            messages.append({
                                "role": role,
                                "name": msg["name"],
                                "content": str(content)
                            })  # type: ignore
                        else:
                            messages.append({"role": role, "content": str(content)})  # type: ignore
            
            # Add the current query
            messages.append({"role": "user", "content": query})  # type: ignore
            
            logger.debug(f"Built {len(messages)} messages for OpenAI API")
            return messages
            
        except Exception as e:
            logger.error(f"Error building messages: {e}")
            # Return minimal message set on error
            return [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": query}
            ]
    
    def optimize_message_length(self, messages: List[ChatCompletionMessageParam], max_tokens: int = 3000) -> List[ChatCompletionMessageParam]:
        """
        Optimize message length to stay within token limits.
        
        Args:
            messages: List of messages to optimize
            max_tokens: Maximum token limit (rough estimate)
            
        Returns:
            Optimized message list
        """
        try:
            # Rough token estimation (4 characters per token)
            total_chars = sum(len(str(msg.get("content", ""))) for msg in messages)
            estimated_tokens = total_chars // 4
            
            if estimated_tokens <= max_tokens:
                return messages
            
            logger.info(f"Optimizing messages: {estimated_tokens} tokens -> target: {max_tokens}")
            
            # Keep system prompt, date injection, and current query
            # Trim conversation history if needed
            optimized_messages = []
            system_messages = []
            history_messages = []
            current_query = None
            
            for msg in messages:
                role = msg.get("role")
                if role == "system" or (role == "function" and msg.get("name") == "get_current_date"):
                    system_messages.append(msg)
                elif role == "assistant" and "I understand that today is" in str(msg.get("content", "")):
                    system_messages.append(msg)
                elif role == "user" and msg == messages[-1]:  # Last message is current query
                    current_query = msg
                else:
                    history_messages.append(msg)
            
            # Add system messages
            optimized_messages.extend(system_messages)
            
            # Add as much history as fits
            if history_messages:
                # Take the most recent history messages
                history_chars = sum(len(str(msg.get("content", ""))) for msg in system_messages)
                history_chars += len(str(current_query.get("content", ""))) if current_query else 0
                
                remaining_tokens = max_tokens - (history_chars // 4)
                
                for msg in reversed(history_messages):
                    msg_tokens = len(str(msg.get("content", ""))) // 4
                    if msg_tokens <= remaining_tokens:
                        optimized_messages.insert(-1 if current_query else len(optimized_messages), msg)
                        remaining_tokens -= msg_tokens
                    else:
                        break
            
            # Add current query
            if current_query:
                optimized_messages.append(current_query)
            
            final_chars = sum(len(str(msg.get("content", ""))) for msg in optimized_messages)
            logger.info(f"Optimized to {len(optimized_messages)} messages, ~{final_chars // 4} tokens")
            
            return optimized_messages
            
        except Exception as e:
            logger.error(f"Error optimizing messages: {e}")
            return messages
    
    def validate_messages(self, messages: List[ChatCompletionMessageParam]) -> bool:
        """
        Validate that messages are properly formatted for OpenAI API.
        
        Args:
            messages: Messages to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            for msg in messages:
                # Check required fields
                if not isinstance(msg, dict) or "role" not in msg:
                    logger.error("Message missing required 'role' field")
                    return False
                
                role = msg["role"]
                if role not in ["system", "user", "assistant", "function"]:
                    logger.error(f"Invalid role: {role}")
                    return False
                
                # Check content requirements
                if role in ["system", "user", "assistant"]:
                    if "content" not in msg or not msg["content"]:
                        logger.error(f"Message with role '{role}' missing content")
                        return False
                
                # Check function message requirements
                if role == "function":
                    if "name" not in msg or not msg["name"]:
                        logger.error("Function message missing required 'name' field")
                        return False
                    if "content" not in msg:
                        logger.error("Function message missing required 'content' field")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating messages: {e}")
            return False
