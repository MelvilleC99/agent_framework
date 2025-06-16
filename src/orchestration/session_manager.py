# src/orchestration/session_manager.py
"""
Session Manager for Agent Conversations

Manages session lifecycle, timeouts, and persistence.
Based on the Industrial Engineering Agent session_manager.py but enhanced
with dependency injection and better error handling.
"""

import logging
import json
import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("session_manager")


class SessionManager:
    """
    Enhanced session manager for persisting conversations and tracking lifecycle.
    
    Handles saving and loading conversation history to/from persistent storage
    and manages session timeouts with configurable storage backends.
    """
    
    def __init__(self, 
                 session_id: str, 
                 storage_type: str = "file", 
                 storage_path: Optional[str] = None, 
                 timeout_minutes: int = 30,
                 database_client=None):
        """
        Initialize the session manager.
        
        Args:
            session_id: Unique session identifier
            storage_type: Storage type ('file' or 'database')
            storage_path: Path to storage directory (for file storage)
            timeout_minutes: Session timeout in minutes
            database_client: Database client for database storage
        """
        self.session_id = session_id
        self.storage_type = storage_type
        self.timeout_minutes = timeout_minutes
        self.last_activity = time.time()
        self.session_started_at = datetime.now()
        self.database_client = database_client
        
        # Set default storage path if not provided
        if storage_path is None:
            if storage_type == "file":
                storage_path = os.path.join(os.getcwd(), "sessions")
            else:
                storage_path = None  # Database doesn't need path
                
        self.storage_path = storage_path
        
        # Create storage directory if needed
        if storage_type == "file" and storage_path and not os.path.exists(storage_path):
            try:
                os.makedirs(storage_path)
                logger.info(f"Created sessions directory: {storage_path}")
            except Exception as e:
                logger.error(f"Failed to create sessions directory: {e}")
            
        logger.info(f"SessionManager initialized for {session_id} using {storage_type} storage (timeout: {timeout_minutes}min)")
    
    def get_conversation_history(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get conversation history from storage.
        
        Returns:
            Conversation history or None if not found
        """
        try:
            if self.storage_type == "file":
                return self._get_history_from_file()
            elif self.storage_type == "database":
                return self._get_history_from_database()
            else:
                logger.warning(f"Unknown storage type: {self.storage_type}")
                return None
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            return None
    
    def _get_history_from_file(self) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history from file storage."""
        if not self.storage_path:
            return None
            
        file_path = os.path.join(self.storage_path, f"{self.session_id}.json")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r') as f:
                session_data = json.load(f)
            return session_data.get("conversation_history", [])
        except Exception as e:
            logger.error(f"Error reading session file {file_path}: {e}")
            return None
    
    def _get_history_from_database(self) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history from database storage."""
        if not self.database_client:
            logger.warning("Database client not available for session storage")
            return None
        
        try:
            # Query session history table (implement based on your schema)
            result = self.database_client.table("session_history").select("*").eq("session_id", self.session_id).execute()
            
            if result.data:
                # Reconstruct conversation history from database records
                history = []
                for record in sorted(result.data, key=lambda x: x.get("created_at", "")):
                    message = {
                        "role": record.get("role"),
                        "content": record.get("content"),
                    }
                    if record.get("function_name"):
                        message["name"] = record.get("function_name")
                    history.append(message)
                return history
            return None
        except Exception as e:
            logger.error(f"Error reading session from database: {e}")
            return None
    
    def save_conversation_history(self, conversation_history: List[Dict[str, Any]]) -> bool:
        """
        Save conversation history to storage.
        
        Args:
            conversation_history: Conversation history to save
            
        Returns:
            Success flag
        """
        try:
            if self.storage_type == "file":
                return self._save_history_to_file(conversation_history)
            elif self.storage_type == "database":
                return self._save_history_to_database(conversation_history)
            else:
                logger.warning(f"Unknown storage type: {self.storage_type}")
                return False
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}")
            return False
    
    def _save_history_to_file(self, conversation_history: List[Dict[str, Any]]) -> bool:
        """Save conversation history to file storage."""
        if not self.storage_path:
            return False
            
        try:
            file_path = os.path.join(self.storage_path, f"{self.session_id}.json")
            
            session_data = {
                "session_id": self.session_id,
                "last_updated": datetime.now().isoformat(),
                "conversation_history": conversation_history
            }
            
            with open(file_path, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            logger.debug(f"Saved {len(conversation_history)} messages to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving to file: {e}")
            return False
    
    def _save_history_to_database(self, conversation_history: List[Dict[str, Any]]) -> bool:
        """Save conversation history to database storage."""
        if not self.database_client:
            logger.warning("Database client not available for session storage")
            return False
        
        try:
            # Clear existing history for this session
            self.database_client.table("session_history").delete().eq("session_id", self.session_id).execute()
            
            # Save new history
            for i, message in enumerate(conversation_history):
                record = {
                    "session_id": self.session_id,
                    "message_index": i,
                    "role": message.get("role"),
                    "content": message.get("content"),
                    "function_name": message.get("name"),
                    "created_at": datetime.now().isoformat()
                }
                self.database_client.table("session_history").insert(record).execute()
            
            logger.debug(f"Saved {len(conversation_history)} messages to database")
            return True
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return False
    
    def clear_conversation_history(self) -> bool:
        """
        Clear conversation history from storage.
        
        Returns:
            Success flag
        """
        try:
            if self.storage_type == "file":
                return self._clear_history_from_file()
            elif self.storage_type == "database":
                return self._clear_history_from_database()
            else:
                logger.warning(f"Unknown storage type: {self.storage_type}")
                return False
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")
            return False
    
    def _clear_history_from_file(self) -> bool:
        """Clear conversation history from file storage."""
        if not self.storage_path:
            return False
            
        try:
            file_path = os.path.join(self.storage_path, f"{self.session_id}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
            logger.info(f"Cleared conversation history for session {self.session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing file history: {e}")
            return False
    
    def _clear_history_from_database(self) -> bool:
        """Clear conversation history from database storage."""
        if not self.database_client:
            return False
        
        try:
            self.database_client.table("session_history").delete().eq("session_id", self.session_id).execute()
            logger.info(f"Cleared conversation history for session {self.session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing database history: {e}")
            return False
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = time.time()
    
    def is_session_expired(self) -> bool:
        """Check if the session has expired due to inactivity."""
        try:
            current_time = time.time()
            elapsed_minutes = (current_time - self.last_activity) / 60
            return elapsed_minutes > self.timeout_minutes
        except Exception as e:
            logger.error(f"Error checking session expiry: {e}")
            return False
    
    def get_session_duration(self) -> Dict[str, Any]:
        """Get session duration information."""
        try:
            current_time = datetime.now()
            duration = current_time - self.session_started_at
            
            return {
                "started_at": self.session_started_at.isoformat(),
                "current_time": current_time.isoformat(),
                "duration_seconds": int(duration.total_seconds()),
                "duration_minutes": round(duration.total_seconds() / 60, 1),
                "last_activity": datetime.fromtimestamp(self.last_activity).isoformat(),
                "minutes_since_activity": round((time.time() - self.last_activity) / 60, 1),
                "is_expired": self.is_session_expired(),
                "timeout_minutes": self.timeout_minutes
            }
        except Exception as e:
            logger.error(f"Error getting session duration: {e}")
            return {"error": str(e)}
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get comprehensive session information."""
        try:
            conversation_history = self.get_conversation_history() or []
            duration_info = self.get_session_duration()
            
            return {
                "session_id": self.session_id,
                "storage_type": self.storage_type,
                "storage_path": self.storage_path,
                "timeout_minutes": self.timeout_minutes,
                "message_count": len(conversation_history),
                "session_duration": duration_info,
                "status": "expired" if self.is_session_expired() else "active"
            }
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return {
                "session_id": self.session_id,
                "error": str(e)
            }
    
    def extend_session(self, additional_minutes: int = 30):
        """
        Extend session timeout.
        
        Args:
            additional_minutes: Additional minutes to add to timeout
        """
        try:
            self.timeout_minutes += additional_minutes
            self.update_activity()  # Reset activity timer
            logger.info(f"Extended session {self.session_id} by {additional_minutes} minutes")
        except Exception as e:
            logger.error(f"Error extending session: {e}")
    
    def force_expire(self):
        """Force the session to expire immediately."""
        self.last_activity = time.time() - (self.timeout_minutes * 60) - 1
        logger.info(f"Forced expiry for session {self.session_id}")
