# src/usage_tracking/session_summarizer.py
"""
Session Summarization for Agent Usage Analytics

Creates session-level summaries from individual usage logs and provides
business intelligence on session patterns and user behavior.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .cost_calculator import CostCalculator

logger = logging.getLogger("session_summarizer")


class SessionSummarizer:
    """
    Session summarizer for agent usage analytics.
    
    Creates session-level summaries from query-level usage logs
    and provides business intelligence capabilities.
    """
    
    def __init__(self, database=None):
        """
        Initialize the session summarizer.
        
        Args:
            database: Database client for persistence
        """
        self.database = database
        self.cost_calculator = CostCalculator()
        logger.info("SessionSummarizer initialized")
    
    def create_session_summary(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        session_ended_reason: str = "manual"
    ) -> Dict[str, Any]:
        """
        Create and save a session summary to the database.
        
        Args:
            session_id: Session identifier
            user_id: User identifier (optional)
            conversation_history: Optional conversation history
            session_ended_reason: How the session ended
            
        Returns:
            Created session summary data
        """
        if not self.database:
            logger.warning("No database available - session summary not saved")
            return {"error": "Database not available"}
        
        try:
            # Get usage logs for this session
            usage_logs = self._get_session_usage_logs(session_id)
            
            if not usage_logs:
                logger.warning(f"No usage logs found for session {session_id}")
                return {"error": "No usage logs found for session"}
            
            # Calculate session statistics
            stats = self._calculate_session_statistics(usage_logs)
            
            # Classify the session
            classification = self._classify_session(usage_logs, conversation_history)
            
            # Build session summary record
            session_summary = {
                "session_id": session_id,
                "user_id": user_id,
                "total_queries": stats.get("total_queries", 0),
                "successful_queries": stats.get("successful_queries", 0),
                "failed_queries": stats.get("failed_queries", 0),
                "session_duration_ms": stats.get("session_duration_ms", 0),
                "total_cost": round(stats.get("total_cost", 0), 6),
                "avg_cost_per_query": round(stats.get("avg_cost_per_query", 0), 6),
                "tools_used": list(stats.get("unique_tools", [])),
                "main_topics": classification.get("main_topics", []),
                "session_type": classification.get("session_type", "unknown"),
                "conversation_summary": classification.get("key_outcomes", ""),
                "session_ended_reason": session_ended_reason,
                "session_started_at": stats.get("session_started_at"),
                "session_ended_at": stats.get("session_ended_at"),
                "created_at": datetime.now().isoformat()
            }
            
            # Write to database
            result = self.database.table("session_summaries").insert(session_summary).execute()
            
            if result.data:
                logger.info(f"✅ Session summary created for {session_id}")
                return True  # Return boolean for coordinator compatibility
            else:
                logger.error(f"Failed to create session summary: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating session summary: {e}")
            return False
    
    def _get_session_usage_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all usage logs for a specific session."""
        if not self.database:
            logger.error("No database client available for getting session usage logs.")
            return []
        try:
            result = self.database.table("agent_usage_logs").select("*").eq("session_id", session_id).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting session usage logs: {e}")
            return []
    
    def _calculate_session_statistics(self, usage_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistical summary of session usage."""
        if not usage_logs:
            return {}
        
        try:
            total_queries = len(usage_logs)
            successful_queries = sum(1 for log in usage_logs if log.get("success", True))
            failed_queries = total_queries - successful_queries
            
            # Time calculations
            start_times = [log.get("started_at") for log in usage_logs if log.get("started_at")]
            end_times = [log.get("completed_at") for log in usage_logs if log.get("completed_at")]
            # Filter out None values
            start_times = [t for t in start_times if t is not None]
            end_times = [t for t in end_times if t is not None]
            session_started_at = min(start_times) if start_times else datetime.now().isoformat()
            session_ended_at = max(end_times) if end_times else datetime.now().isoformat()
            
            # Calculate session duration
            try:
                start_dt = datetime.fromisoformat(session_started_at.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(session_ended_at.replace('Z', '+00:00'))
                session_duration_ms = int((end_dt - start_dt).total_seconds() * 1000)
            except:
                session_duration_ms = 0
            
            # Processing time calculations
            processing_times = [log.get("processing_time_ms", 0) for log in usage_logs]
            total_processing_time_ms = sum(processing_times)
            avg_query_time_ms = int(total_processing_time_ms / total_queries) if total_queries > 0 else 0
            
            # Cost calculations
            total_cost = sum(log.get("total_cost", 0) for log in usage_logs)
            total_llm_cost = sum(log.get("llm_cost", 0) for log in usage_logs)
            total_compute_cost = sum(log.get("estimated_compute_cost", 0) for log in usage_logs)
            avg_cost_per_query = total_cost / total_queries if total_queries > 0 else 0
            
            # Token calculations
            total_input_tokens = sum(log.get("total_input_tokens", 0) for log in usage_logs)
            total_output_tokens = sum(log.get("total_output_tokens", 0) for log in usage_logs)
            total_api_calls = sum(log.get("total_api_calls", 0) for log in usage_logs)
            
            # Agent usage
            chatgpt_queries = sum(1 for log in usage_logs if log.get("agent_used") in ["chatgpt", "both"])
            deepseek_queries = sum(1 for log in usage_logs if log.get("agent_used") in ["deepseek", "both"])
            
            # Tools used
            unique_tools = set()
            for log in usage_logs:
                tools_used = log.get("tools_used")
                if tools_used:
                    if isinstance(tools_used, str):
                        try:
                            tools_list = json.loads(tools_used)
                            unique_tools.update(tools_list)
                        except:
                            pass
                    elif isinstance(tools_used, list):
                        unique_tools.update(tools_used)
            
            return {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "session_duration_ms": session_duration_ms,
                "avg_query_time_ms": avg_query_time_ms,
                "total_processing_time_ms": total_processing_time_ms,
                "total_cost": round(total_cost, 6),
                "avg_cost_per_query": round(avg_cost_per_query, 6),
                "total_llm_cost": round(total_llm_cost, 6),
                "total_compute_cost": round(total_compute_cost, 6),
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_api_calls": total_api_calls,
                "chatgpt_queries": chatgpt_queries,
                "deepseek_queries": deepseek_queries,
                "unique_tools": unique_tools,
                "session_started_at": session_started_at,
                "session_ended_at": session_ended_at
            }
        except Exception as e:
            logger.error(f"Error calculating session statistics: {e}")
            return {}
    
    def _classify_session(
        self, 
        usage_logs: List[Dict[str, Any]], 
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Classify session type and extract key outcomes."""
        try:
            total_queries = len(usage_logs)
            successful_queries = sum(1 for log in usage_logs if log.get("success", True))
            
            # Analyze query types to determine main topics
            query_types = {}
            for log in usage_logs:
                query_type = log.get("query_type", "unknown")
                query_types[query_type] = query_types.get(query_type, 0) + 1
            
            main_topics = [qtype.replace('_', ' ') for qtype in query_types.keys() if qtype != "unknown"]
            
            # Determine session type
            if "data_query" in query_types:
                session_type = "data_inquiry"
            elif "performance_analysis" in query_types:
                session_type = "analytics"
            elif "maintenance_workflow" in query_types:
                session_type = "workflow_execution"
            else:
                session_type = "general_assistance"
            
            # Determine complexity level
            avg_processing_time = sum(log.get("processing_time_ms", 0) for log in usage_logs) / total_queries
            total_tools_used = sum(len(json.loads(log.get("tools_used", "[]")) if isinstance(log.get("tools_used"), str) else []) for log in usage_logs)
            
            if avg_processing_time > 5000 or total_tools_used > 10 or total_queries > 10:
                complexity_level = "high"
            elif avg_processing_time > 2000 or total_tools_used > 5 or total_queries > 5:
                complexity_level = "medium"
            else:
                complexity_level = "low"
            
            # Generate key outcomes summary
            if successful_queries == total_queries:
                key_outcomes = f"All {total_queries} queries completed successfully"
            elif successful_queries > 0:
                key_outcomes = f"{successful_queries}/{total_queries} queries successful"
            else:
                key_outcomes = "Session completed with errors"
            
            # Determine if follow-up is needed
            requires_followup = (successful_queries / total_queries) < 0.8 if total_queries > 0 else False
            
            return {
                "main_topics": main_topics,
                "session_type": session_type,
                "key_outcomes": key_outcomes,
                "complexity_level": complexity_level,
                "requires_followup": requires_followup
            }
        except Exception as e:
            logger.error(f"Error classifying session: {e}")
            return {
                "main_topics": ["unknown"],
                "session_type": "unknown",
                "key_outcomes": "Classification failed",
                "complexity_level": "unknown",
                "requires_followup": False
            }
    
    def get_session_analytics(self, user_id: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """
        Get session analytics for the specified period.
        
        Args:
            user_id: Optional user ID to filter by
            days: Number of days to analyze
            
        Returns:
            Session analytics summary
        """
        if not self.database:
            return {"error": "Database not available"}
        
        try:
            # Get sessions from the last N days
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = self.database.table("session_summaries").select("*").gte("session_started_at", cutoff_date)
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            result = query.execute()
            sessions = result.data if result.data else []
            
            if not sessions:
                return {"message": f"No sessions found in the last {days} days"}
            
            # Calculate analytics
            total_sessions = len(sessions)
            total_queries = sum(s.get("total_queries", 0) for s in sessions)
            total_cost = sum(s.get("total_cost", 0) for s in sessions)
            avg_session_duration = sum(s.get("session_duration_ms", 0) for s in sessions) / total_sessions
            
            # Session types
            session_types = {}
            for session in sessions:
                session_type = session.get("session_type", "unknown")
                session_types[session_type] = session_types.get(session_type, 0) + 1
            
            # Complexity levels
            complexity_counts = {"high": 0, "medium": 0, "low": 0}
            
            # Most used tools
            all_tools = []
            for session in sessions:
                tools = session.get("tools_used", [])
                if tools:
                    all_tools.extend(tools)
            
            tool_counts = {}
            for tool in all_tools:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
            
            most_used_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "period_days": days,
                "total_sessions": total_sessions,
                "total_queries": total_queries,
                "average_queries_per_session": round(total_queries / total_sessions, 2),
                "total_cost": round(total_cost, 6),
                "average_cost_per_session": round(total_cost / total_sessions, 6),
                "average_session_duration_minutes": round(avg_session_duration / 60000, 2),
                "session_types": session_types,
                "most_used_tools": most_used_tools,
                "user_filter": user_id
            }
        except Exception as e:
            logger.error(f"Error getting session analytics: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the session summarizer."""
        try:
            return {
                "status": "healthy",
                "database_available": self.database is not None,
                "cost_calculator": "healthy"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
