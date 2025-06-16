# src/orchestration/context_manager.py
"""
Context Manager for Agent Conversations

Manages conversation history, query metadata, and context for agent handoffs.
Based on the Industrial Engineering Agent context_manager.py but enhanced 
with dependency injection and better error handling.
"""

import logging
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger("context_manager")


class ContextManager:
    """
    Enhanced context manager for the agent system.
    
    Manages conversation history and query metadata in a format that can be
    used by both OpenAI and DeepSeek agents. Provides context-aware follow-up
    capabilities and agent handoff support.
    """
    
    def __init__(self, session_manager=None, max_history: int = 6):
        """
        Initialize the context manager.
        
        Args:
            session_manager: Optional session manager for persistence
            max_history: Maximum number of messages to keep in history
        """
        self.session_manager = session_manager
        self.max_history = max_history
        self.conversation_history = []
        
        # Query metadata for context-aware follow-ups
        self.query_metadata = {
            "last_query_type": "",
            "last_tool": "",
            "last_filters": {},
            "last_table_shown": "",
            "timestamp": 0.0
        }
        
        # Load history from session manager if available
        if session_manager:
            self._load_from_session()
            
        logger.info(f"ContextManager initialized (max_history={max_history})")
    
    def _load_from_session(self):
        """Load conversation history from session manager."""
        if self.session_manager:
            try:
                full_history = self.session_manager.get_conversation_history() or []
                # Only load the most recent messages
                self.conversation_history = full_history[-self.max_history:] if full_history else []
                logger.info(f"Loaded {len(self.conversation_history)} messages from session")
            except Exception as e:
                logger.error(f"Error loading session history: {e}")
                self.conversation_history = []
    
    def add_message(self, role: str, content: str, function_name: Optional[str] = None):
        """
        Add a message to the conversation history.
        
        Args:
            role: Message role ('user', 'assistant', or 'function')
            content: Message content
            function_name: Optional function name for function messages
        """
        try:
            # Truncate content if it's too long (for token savings)
            max_content_length = 2000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "... [truncated]"
                logger.debug(f"Truncated {role} message to {max_content_length} characters")
            
            # Create message object
            if role == 'function' and function_name:
                message = {
                    "role": role,
                    "name": function_name,
                    "content": content
                }
            else:
                message = {
                    "role": role,
                    "content": content
                }
            
            self.conversation_history.append(message)
            
            # Trim history if needed
            if len(self.conversation_history) > self.max_history:
                excess = len(self.conversation_history) - self.max_history
                # Remove in pairs when possible to maintain context
                if excess >= 2:
                    self.conversation_history = self.conversation_history[excess:]
                else:
                    self.conversation_history = self.conversation_history[1:]
                
                logger.debug(f"Trimmed history to {len(self.conversation_history)} messages")
            
            # Save to session manager if available
            if self.session_manager:
                self.session_manager.save_conversation_history(self.conversation_history)
                
            logger.debug(f"Added {role} message to history. Total: {len(self.conversation_history)}")
            
        except Exception as e:
            logger.error(f"Error adding message to context: {e}")
    
    def get_recent_history(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent conversation history.
        
        Args:
            count: Number of recent messages to return (default: all)
            
        Returns:
            List of recent messages
        """
        try:
            if count is None:
                return self.conversation_history.copy()
            
            # Ensure we get complete exchanges (user-assistant pairs)
            if count % 2 != 0:
                count += 1  # Make it even to get complete exchanges
                
            return self.conversation_history[-count:].copy()
        except Exception as e:
            logger.error(f"Error getting recent history: {e}")
            return []
    
    def get_context_for_deepseek(self) -> str:
        """
        Get formatted context for DeepSeek agent.
        
        Returns:
            Context string optimized for token efficiency
        """
        try:
            context_parts = []
            
            # Only use the most recent messages for context
            recent_messages = self.get_recent_history(4)  # Last 2 exchanges
            
            for msg in recent_messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                # Further truncate content for DeepSeek context
                if len(content) > 500:
                    content = content[:500] + "..."
                
                if role == "user":
                    context_parts.append(f"USER: {content}")
                elif role == "assistant":
                    context_parts.append(f"ASSISTANT: {content}")
                elif role == "function":
                    function_name = msg.get("name", "unknown")
                    # Summarize function results instead of full content
                    result_preview = content[:200] + "..." if len(content) > 200 else content
                    context_parts.append(f"FUNCTION '{function_name}': {result_preview}")
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"Error getting DeepSeek context: {e}")
            return "No previous conversation context available."
    
    def add_query_metadata(self, query_type: str, tool_name: str, 
                          filters: Optional[Dict[str, Any]] = None, 
                          table_shown: Optional[str] = None):
        """
        Add metadata about the last query executed for context-aware follow-ups.
        
        Args:
            query_type: Type of query executed
            tool_name: Name of the tool that was used
            filters: Filters that were applied to the query
            table_shown: Name/type of table that was displayed
        """
        try:
            # Ensure all fields are correct types
            filters = filters if filters is not None else {}
            table_shown = table_shown if table_shown is not None else ""
            query_type = query_type if query_type is not None else ""
            tool_name = tool_name if tool_name is not None else ""
            
            self.query_metadata = {
                "last_query_type": query_type,
                "last_tool": tool_name,
                "last_filters": filters,
                "last_table_shown": table_shown,
                "timestamp": time.time()
            }
            
            logger.debug(f"Added query metadata: {query_type} via {tool_name}")
        except Exception as e:
            logger.error(f"Error adding query metadata: {e}")
    
    def get_last_query_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the last query for context-aware processing.
        
        Returns:
            Dictionary with last query metadata or empty dict if none
        """
        return self.query_metadata.copy()
    
    def is_recent_query_metadata(self, max_age_seconds: int = 300) -> bool:
        """
        Check if the stored query metadata is recent enough to be relevant.
        
        Args:
            max_age_seconds: Maximum age in seconds (default: 5 minutes)
            
        Returns:
            True if metadata is recent and relevant
        """
        try:
            if not self.query_metadata.get("timestamp"):
                return False
                
            age = time.time() - self.query_metadata["timestamp"]
            return age <= max_age_seconds
        except Exception as e:
            logger.error(f"Error checking metadata age: {e}")
            return False
    
    def clear_query_metadata(self):
        """Clear the query metadata (useful when starting new conversation topics)."""
        self.query_metadata = {
            "last_query_type": "",
            "last_tool": "",
            "last_filters": {},
            "last_table_shown": "",
            "timestamp": 0.0
        }
        logger.debug("Cleared query metadata")
    
    def clear_history(self):
        """Clear the conversation history and query metadata."""
        try:
            self.conversation_history = []
            self.clear_query_metadata()
            
            # Clear session if available
            if self.session_manager:
                self.session_manager.clear_conversation_history()
                
            logger.info("Conversation history and query metadata cleared")
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
    
    def get_summary_for_handoff(self) -> str:
        """
        Get a summary of the conversation for handoff between agents.

        Returns:
            Summary string optimized for token usage
        """
        try:
            if not self.conversation_history:
                return "No previous conversation."
            
            # Get the last user query and any relevant function results
            last_user_query = None
            last_function_result = None
            
            for msg in reversed(self.conversation_history):
                if msg["role"] == "user" and not last_user_query:
                    last_user_query = msg["content"]
                elif msg["role"] == "function" and not last_function_result:
                    last_function_result = f"{msg.get('name', 'function')}: {msg['content'][:200]}..."
                
                if last_user_query and last_function_result:
                    break
            
            summary_parts = []
            if last_user_query:
                summary_parts.append(f"Query: {last_user_query}")
            if last_function_result:
                summary_parts.append(f"Result: {last_function_result}")
                
            return "\n".join(summary_parts)
        except Exception as e:
            logger.error(f"Error creating handoff summary: {e}")
            return "Error creating conversation summary."
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about the current conversation."""
        try:
            user_messages = sum(1 for msg in self.conversation_history if msg["role"] == "user")
            assistant_messages = sum(1 for msg in self.conversation_history if msg["role"] == "assistant")
            function_messages = sum(1 for msg in self.conversation_history if msg["role"] == "function")
            
            return {
                "total_messages": len(self.conversation_history),
                "user_messages": user_messages,
                "assistant_messages": assistant_messages,
                "function_messages": function_messages,
                "has_recent_metadata": self.is_recent_query_metadata()
            }
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {"error": str(e)}
