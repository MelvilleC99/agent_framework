# src/agents/base/agent_interface.py
"""
Base Agent Interface

Abstract base class that defines the contract for all agent implementations.
Ensures consistency across ChatGPT, DeepSeek, and future agents.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

logger = logging.getLogger("base_agent")


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations.
    
    This interface ensures consistency across all agents and provides
    a standardized contract for the orchestration layer.
    """
    
    def __init__(self, 
                 tool_registry=None,
                 context_manager=None,
                 database=None,
                 **kwargs):
        """
        Initialize the base agent.
        
        Args:
            tool_registry: Tool registry for function execution
            context_manager: Context manager for conversation history
            database: Database client for persistence
            **kwargs: Additional agent-specific parameters
        """
        self.tool_registry = tool_registry
        self.context_manager = context_manager
        self.database = database
        self.is_initialized = False
        
        logger.info(f"{self.__class__.__name__} base initialization complete")
    
    @abstractmethod
    def process_query(self, 
                     query: str, 
                     conversation_history: Optional[List[Dict[str, str]]] = None,
                     conversation_id: Optional[str] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Process a user query and return a response.
        
        Args:
            query: The user's query
            conversation_history: Optional conversation history
            conversation_id: Optional conversation ID for tracking
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with 'answer' key and optional metadata
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the agent and its components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up agent resources."""
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the agent and its components.
        
        Returns:
            Health status dictionary
        """
        try:
            health = {
                "agent": self.__class__.__name__,
                "status": "healthy" if self.is_initialized else "not_initialized",
                "tool_registry": "available" if self.tool_registry else "not_available",
                "context_manager": "available" if self.context_manager else "not_available",
                "database": "available" if self.database else "not_available"
            }
            
            return health
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "agent": self.__class__.__name__,
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of agent capabilities.
        
        Returns:
            List of capability strings
        """
        base_capabilities = ["query_processing", "health_check"]
        
        if self.tool_registry:
            base_capabilities.append("function_calling")
        
        if self.context_manager:
            base_capabilities.append("conversation_history")
            
        return base_capabilities
    
    def set_usage_tracker(self, usage_tracker):
        """Set the usage tracker for cost tracking."""
        self.usage_tracker = usage_tracker
        logger.info(f"Usage tracker set for {self.__class__.__name__}")
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(initialized={self.is_initialized})"
    
    def __repr__(self) -> str:
        """Detailed representation of the agent."""
        return f"{self.__class__.__name__}(tool_registry={bool(self.tool_registry)}, context_manager={bool(self.context_manager)}, database={bool(self.database)})"
