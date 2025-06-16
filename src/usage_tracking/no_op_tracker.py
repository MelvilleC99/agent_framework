# src/usage_tracking/no_op_tracker.py
"""
No-Op Analytics Components

Provides no-operation analytics components for template mode
when database is not available or analytics are disabled.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("analytics.no_op")


class NoOpUsageTracker:
    """
    No-operation usage tracker for template mode.
    
    Provides the same interface as UsageTracker but doesn't persist data.
    Useful for development, testing, or when database is not available.
    """
    
    def __init__(self):
        """Initialize the no-op usage tracker."""
        self.active_queries = {}
        logger.info("NoOpUsageTracker initialized (template mode)")
    
    def start_query_tracking(
        self, 
        session_id: str, 
        conversation_id: str, 
        query_text: str, 
        user_id: Optional[str] = None
    ) -> bool:
        """Start tracking a query (no-op)."""
        self.active_queries[conversation_id] = {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "query_text": query_text,
            "user_id": user_id,
            "started_at": datetime.now(),
            "api_calls": [],
            "tools_used": []
        }
        logger.debug(f"Started tracking query: {conversation_id}")
        return True
    
    def track_api_call(
        self,
        conversation_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float = 0.0,
        agent_type: str = "chatgpt"
    ) -> bool:
        """Track an API call (no-op)."""
        if conversation_id in self.active_queries:
            self.active_queries[conversation_id]["api_calls"].append({
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "agent_type": agent_type
            })
        logger.debug(f"Tracked API call for: {conversation_id}")
        return True
    
    def track_tool_usage(
        self,
        conversation_id: str,
        tool_name: str,
        success: bool = True,
        execution_time_ms: Optional[int] = None
    ) -> bool:
        """Track tool usage (no-op)."""
        if conversation_id in self.active_queries:
            self.active_queries[conversation_id]["tools_used"].append({
                "tool_name": tool_name,
                "success": success,
                "execution_time_ms": execution_time_ms
            })
        logger.debug(f"Tracked tool usage: {tool_name}")
        return True
    
    def complete_query_tracking(
        self,
        conversation_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
        agent_used: str = "chatgpt"
    ) -> bool:
        """Complete query tracking (no-op)."""
        if conversation_id in self.active_queries:
            query_data = self.active_queries.pop(conversation_id)
            logger.debug(f"Completed tracking for: {conversation_id}")
        return True
    
    def cleanup_stale_queries(self, max_age_minutes: int = 30) -> int:
        """Clean up stale queries (no-op)."""
        return 0
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for no-op tracker."""
        return {
            "status": "healthy",
            "mode": "no_op",
            "active_queries": len(self.active_queries),
            "database_connected": False
        }


class NoOpSessionSummarizer:
    """
    No-operation session summarizer for template mode.
    
    Provides the same interface as SessionSummarizer but doesn't persist data.
    """
    
    def __init__(self):
        """Initialize the no-op session summarizer."""
        self.session_cache = {}
        logger.info("NoOpSessionSummarizer initialized (template mode)")
    
    def create_session_summary(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create session summary (no-op)."""
        summary = {
            "session_id": session_id,
            "user_id": user_id,
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "session_duration_ms": 0,
            "total_cost": 0.0,
            "avg_cost_per_query": 0.0,
            "tools_used": [],
            "main_topics": [],
            "session_type": "unknown",
            "conversation_summary": "No summary available (template mode)",
            "session_ended_reason": "template_mode",
            "created_at": datetime.now()
        }
        
        self.session_cache[session_id] = summary
        logger.debug(f"Created session summary: {session_id}")
        return summary
    
    def get_session_analytics(
        self,
        user_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get session analytics (no-op)."""
        return {
            "total_sessions": len(self.session_cache),
            "total_queries": 0,
            "average_session_length": 0,
            "most_used_tools": [],
            "cost_trends": [],
            "session_types": {"template_mode": len(self.session_cache)},
            "period_days": days,
            "mode": "no_op"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for no-op summarizer."""
        return {
            "status": "healthy",
            "mode": "no_op",
            "cached_sessions": len(self.session_cache),
            "database_connected": False
        }
