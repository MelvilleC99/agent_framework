# src/api/config/database.py
"""
Database Manager

Handles database initialization and connection management.
"""

import logging
from typing import Optional
from supabase import create_client, Client

logger = logging.getLogger("database")


class DatabaseManager:
    """
    Database connection manager for Supabase.
    
    Provides a clean interface for database operations and
    ensures proper connection management.
    """
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._url: Optional[str] = None
        self._key: Optional[str] = None
    
    async def initialize(self, url: str, key: str) -> None:
        """
        Initialize the database connection.
        
        Args:
            url: Supabase project URL
            key: Supabase API key
        """
        try:
            self._url = url
            self._key = key
            self._client = create_client(url, key)
            
            # Test connection
            response = self._client.table("agent_usage_logs").select("id").limit(1).execute()
            logger.info("✅ Database connection verified")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client."""
        if not self._client:
            raise RuntimeError("Database not initialized")
        return self._client
    
    async def cleanup(self) -> None:
        """Cleanup database resources."""
        # Supabase client doesn't need explicit cleanup
        self._client = None
        logger.info("✅ Database cleanup complete")
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._client is not None
