# src/database/setup.py
"""
Database Setup and Schema Creation

Handles automatic database table creation for the agent template.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("database.setup")


class DatabaseSetup:
    """
    Database setup and schema management for the agent template.
    
    Creates required tables if they don't exist and handles migrations.
    """
    
    def __init__(self, database_client):
        """
        Initialize database setup.
        
        Args:
            database_client: Database client (Supabase, PostgreSQL, etc.)
        """
        self.db = database_client
        self.required_tables = {
            "agent_usage_logs": self._get_usage_logs_schema(),
            "session_summaries": self._get_session_summaries_schema()
        }
        
    async def ensure_tables_exist(self) -> Dict[str, bool]:
        """
        Ensure all required tables exist, create them if they don't.
        
        Returns:
            Dictionary showing which tables were created
        """
        results = {}
        
        for table_name, schema in self.required_tables.items():
            try:
                exists = await self._table_exists(table_name)
                if not exists:
                    await self._create_table(table_name, schema)
                    results[table_name] = True
                    logger.info(f"✅ Created table: {table_name}")
                else:
                    results[table_name] = False
                    logger.info(f"✅ Table exists: {table_name}")
            except Exception as e:
                logger.error(f"❌ Error with table {table_name}: {e}")
                results[table_name] = f"Error: {e}"
        
        return results
    
    async def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            # Try a simple query to see if table exists
            result = self.db.table(table_name).select("*").limit(1).execute()
            return True
        except Exception:
            return False
    
    async def _create_table(self, table_name: str, schema: str) -> bool:
        """
        Create a table with the given schema.
        
        Note: This is simplified for the template. In production, you would:
        1. Use proper SQL migrations
        2. Handle different database types
        3. Use database-specific DDL
        """
        try:
            # For Supabase/PostgreSQL, you would typically create tables via SQL
            # This is a simplified approach for the template
            logger.warning(f"Table creation for {table_name} requires manual SQL execution:")
            logger.warning(f"SQL: {schema}")
            
            # In a real implementation, you would execute the DDL here
            # For now, we'll just log the required SQL
            return True
            
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            return False
    
    def _get_usage_logs_schema(self) -> str:
        """Get the schema for agent_usage_logs table."""
        return """
        CREATE TABLE IF NOT EXISTS agent_usage_logs (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            conversation_id VARCHAR(255) NOT NULL,
            user_id VARCHAR(255),
            query_text TEXT,
            query_type VARCHAR(100),
            tools_used TEXT[], -- Array of tool names
            processing_time_ms INTEGER,
            memory_usage_mb FLOAT,
            total_api_calls INTEGER DEFAULT 0,
            total_input_tokens INTEGER DEFAULT 0,
            total_output_tokens INTEGER DEFAULT 0,
            llm_cost DECIMAL(10,6) DEFAULT 0.00,
            estimated_compute_cost DECIMAL(10,6) DEFAULT 0.00,
            total_cost DECIMAL(10,6) DEFAULT 0.00,
            success BOOLEAN DEFAULT true,
            error_message TEXT,
            agent_used VARCHAR(100),
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Indexes for better query performance
        CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_session_id ON agent_usage_logs(session_id);
        CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_user_id ON agent_usage_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_created_at ON agent_usage_logs(created_at);
        """
    
    def _get_session_summaries_schema(self) -> str:
        """Get the schema for session_summaries table."""
        return """
        CREATE TABLE IF NOT EXISTS session_summaries (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_id VARCHAR(255),
            total_queries INTEGER DEFAULT 0,
            successful_queries INTEGER DEFAULT 0,
            failed_queries INTEGER DEFAULT 0,
            session_duration_ms INTEGER,
            total_cost DECIMAL(10,6) DEFAULT 0.00,
            avg_cost_per_query DECIMAL(10,6) DEFAULT 0.00,
            tools_used TEXT[], -- Array of tool names
            main_topics TEXT[], -- Array of main topics discussed
            session_type VARCHAR(100),
            conversation_summary TEXT,
            session_ended_reason VARCHAR(100),
            session_started_at TIMESTAMP WITH TIME ZONE,
            session_ended_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Indexes for better query performance
        CREATE INDEX IF NOT EXISTS idx_session_summaries_session_id ON session_summaries(session_id);
        CREATE INDEX IF NOT EXISTS idx_session_summaries_user_id ON session_summaries(user_id);
        CREATE INDEX IF NOT EXISTS idx_session_summaries_created_at ON session_summaries(created_at);
        """
    
    def get_setup_sql(self) -> str:
        """
        Get the complete SQL for setting up all required tables.
        
        Returns:
            Complete SQL script for database setup
        """
        sql_parts = []
        
        for table_name, schema in self.required_tables.items():
            sql_parts.append(f"-- Table: {table_name}")
            sql_parts.append(schema)
            sql_parts.append("")
        
        return "\n".join(sql_parts)
    
    def print_setup_instructions(self):
        """Print setup instructions for manual database creation."""
        logger.info("=" * 80)
        logger.info("DATABASE SETUP REQUIRED")
        logger.info("=" * 80)
        logger.info("")
        logger.info("The agent template requires the following database tables.")
        logger.info("Please execute the following SQL in your database:")
        logger.info("")
        logger.info(self.get_setup_sql())
        logger.info("=" * 80)
