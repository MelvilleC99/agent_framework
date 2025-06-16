# src/agents/chatgpt/context_helpers.py
"""
Context Management Utilities for ChatGPT Agent

Based on the Industrial Engineering Agent's context_helpers.py but enhanced
with better error handling and more robust metadata extraction.
"""

import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger("context_helpers")


class ContextHelpers:
    """
    Provides context management utilities for the ChatGPT agent.
    
    This component handles:
    - Query metadata storage and retrieval
    - Entity extraction from queries (names, IDs, etc.)
    - Context analysis utilities
    - Follow-up query support
    """
    
    def __init__(self, context_manager):
        """Initialize the context helpers."""
        self.context_manager = context_manager
        logger.info("ContextHelpers initialized")
    
    def store_query_metadata(self, function_name: str, function_args: Dict[str, Any], result: Any):
        """
        Store simplified metadata about the executed query for context-aware follow-ups.
        
        Args:
            function_name: Name of the function that was executed
            function_args: Arguments passed to the function
            result: Result returned by the function
        """
        try:
            # Only store metadata for successful query operations
            if function_name and isinstance(result, dict) and result.get("success"):
                query_type = result.get("query_type", "unknown")
                query_text = function_args.get("query", "").lower() if isinstance(function_args, dict) else ""
                
                # Extract filters from the query text and function args
                filters = self._extract_filters(query_text, function_args)
                
                # Store context in the context manager
                if self.context_manager:
                    self.context_manager.add_query_metadata(
                        query_type=query_type,
                        tool_name=function_name,
                        filters=filters,
                        table_shown=query_type
                    )
                    logger.info(f"Stored context: {query_type} query with filters: {filters}")
            
            # Clear context for non-query operations to avoid confusion
            elif function_name in ["get_tool_details", "run_scheduled_maintenance", "analyze_performance"]:
                logger.info(f"Clearing context after {function_name} operation")
                if self.context_manager:
                    self.context_manager.clear_query_metadata()
        
        except Exception as e:
            logger.warning(f"Failed to store query metadata: {e}")
    
    def _extract_filters(self, query_text: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract filters from query text and function arguments."""
        filters = {}
        
        try:
            # Extract from function arguments first
            if isinstance(function_args, dict):
                for key, value in function_args.items():
                    if key in ["user_id", "mechanic_name", "machine_id", "status", "priority", "department"]:
                        filters[key] = value
            
            # Extract from query text
            if query_text:
                # Extract entity names
                entity_name = self.extract_entity_from_query(query_text)
                if entity_name:
                    filters["entity_name"] = entity_name
                
                # Extract status indicators
                status = self._extract_status(query_text)
                if status:
                    filters["status"] = status
                
                # Extract time references
                time_ref = self._extract_time_reference(query_text)
                if time_ref:
                    filters["time_filter"] = time_ref
            
            return filters
            
        except Exception as e:
            logger.error(f"Error extracting filters: {e}")
            return {}
    
    def extract_entity_from_query(self, query_text: str) -> Optional[str]:
        """
        Extract entity names (people, departments, etc.) from query text.
        
        Args:
            query_text: Query text to analyze
            
        Returns:
            Extracted entity name or None
        """
        try:
            # Enhanced patterns for entity extraction
            patterns = [
                # Person names with context
                r'(?:for|by|from|assigned\s+to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:items?|tasks?|data|work|assignments?)',
                r'(?:mechanic|person|user|employee)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                
                # Department or team names
                r'(?:department|team|group)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                
                # Machine or asset IDs
                r'(?:machine|asset|equipment)\s*(?:#|id)?\s*([A-Z0-9]+)',
                
                # General capitalized entities
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query_text, re.IGNORECASE)
                if match:
                    entity = match.group(1).strip()
                    
                    # Filter out common words that aren't entities
                    excluded_words = {
                        'the', 'and', 'for', 'with', 'show', 'list', 'view', 'get', 'find',
                        'what', 'when', 'where', 'how', 'why', 'who', 'which', 'all', 'any',
                        'some', 'today', 'tomorrow', 'yesterday', 'monday', 'tuesday', 
                        'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
                    }
                    
                    if entity.lower() not in excluded_words and len(entity) > 2:
                        logger.debug(f"Extracted entity: '{entity}' from query")
                        return entity.lower()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting entity: {e}")
            return None
    
    def _extract_status(self, query_text: str) -> Optional[str]:
        """Extract status indicators from query text."""
        try:
            status_patterns = {
                'open': r'\b(?:open|active|pending|outstanding)\b',
                'completed': r'\b(?:completed?|finished|done|closed)\b',
                'overdue': r'\b(?:overdue|late|past\s+due)\b',
                'in_progress': r'\b(?:in\s+progress|working|ongoing)\b'
            }
            
            for status, pattern in status_patterns.items():
                if re.search(pattern, query_text, re.IGNORECASE):
                    return status
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting status: {e}")
            return None
    
    def _extract_time_reference(self, query_text: str) -> Optional[str]:
        """Extract time references from query text."""
        try:
            time_patterns = {
                'today': r'\b(?:today|now)\b',
                'tomorrow': r'\b(?:tomorrow)\b',
                'this_week': r'\b(?:this\s+week|week)\b',
                'next_week': r'\b(?:next\s+week)\b',
                'this_month': r'\b(?:this\s+month|month)\b',
                'overdue': r'\b(?:overdue|past\s+due)\b'
            }
            
            for time_ref, pattern in time_patterns.items():
                if re.search(pattern, query_text, re.IGNORECASE):
                    return time_ref
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting time reference: {e}")
            return None
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current context state.
        
        Returns:
            Dictionary with context information
        """
        try:
            if not self.context_manager:
                return {"error": "Context manager not available"}
            
            metadata = self.context_manager.get_last_query_metadata()
            is_recent = self.context_manager.is_recent_query_metadata()
            
            return {
                "has_recent_context": is_recent,
                "last_query_type": metadata.get("last_query_type", ""),
                "last_tool": metadata.get("last_tool", ""),
                "last_filters": metadata.get("last_filters", {}),
                "context_age_recent": is_recent
            }
            
        except Exception as e:
            logger.error(f"Error getting context summary: {e}")
            return {"error": str(e)}
    
    def clear_context(self):
        """Clear the current context."""
        try:
            if self.context_manager:
                self.context_manager.clear_query_metadata()
                logger.info("Context cleared")
        except Exception as e:
            logger.error(f"Error clearing context: {e}")
    
    def enhance_query_with_context(self, query: str) -> str:
        """
        Enhance a query with context information if relevant.
        
        Args:
            query: Original query
            
        Returns:
            Enhanced query with context
        """
        try:
            if not self.context_manager:
                return query
            
            # Check if we have recent relevant context
            if not self.context_manager.is_recent_query_metadata():
                return query
            
            metadata = self.context_manager.get_last_query_metadata()
            last_filters = metadata.get("last_filters", {})
            
            # If query seems to be a follow-up and we have relevant filters
            if last_filters and self._is_follow_up_query(query):
                context_info = []
                
                for key, value in last_filters.items():
                    if value and key not in ["timestamp"]:
                        context_info.append(f"{key}: {value}")
                
                if context_info:
                    enhanced_query = f"{query} (Context from previous query: {', '.join(context_info)})"
                    logger.debug(f"Enhanced query with context: {enhanced_query}")
                    return enhanced_query
            
            return query
            
        except Exception as e:
            logger.error(f"Error enhancing query with context: {e}")
            return query
    
    def _is_follow_up_query(self, query: str) -> bool:
        """Simple check for follow-up query indicators."""
        follow_up_indicators = [
            "those", "these", "them", "that", "the same", "also",
            "for him", "for her", "his", "hers", "their"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in follow_up_indicators)
