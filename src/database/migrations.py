# src/database/migrations.py
"""
Database Migration Utilities

Simple migration system for the agent template.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("database.migrations")


async def check_tables_exist(database_client) -> Dict[str, bool]:
    """
    Check which required tables exist in the database.
    
    Args:
        database_client: Database client
        
    Returns:
        Dictionary showing table existence status
    """
    required_tables = ["agent_usage_logs", "session_summaries"]
    results = {}
    
    for table_name in required_tables:
        try:
            # Try a simple query to check if table exists
            result = database_client.table(table_name).select("*").limit(1).execute()
            results[table_name] = True
            logger.info(f"✅ Table exists: {table_name}")
        except Exception as e:
            results[table_name] = False
            logger.warning(f"❌ Table missing: {table_name}")
    
    return results


async def run_migrations(database_client) -> Dict[str, Any]:
    """
    Run database migrations to ensure tables exist.
    
    Args:
        database_client: Database client
        
    Returns:
        Migration results
    """
    from .setup import DatabaseSetup
    
    setup = DatabaseSetup(database_client)
    
    # Check current state
    table_status = await check_tables_exist(database_client)
    missing_tables = [table for table, exists in table_status.items() if not exists]
    
    if missing_tables:
        logger.warning(f"Missing tables: {missing_tables}")
        setup.print_setup_instructions()
        
        return {
            "status": "manual_setup_required",
            "missing_tables": missing_tables,
            "setup_sql": setup.get_setup_sql(),
            "message": "Please run the provided SQL to create required tables"
        }
    else:
        logger.info("✅ All required tables exist")
        return {
            "status": "complete",
            "missing_tables": [],
            "message": "All required tables exist"
        }


def get_setup_instructions() -> str:
    """
    Get database setup instructions for new installations.
    
    Returns:
        Setup instructions text
    """
    return """
# Database Setup for Agent Template

## Required Tables

The agent template requires two main tables for analytics and tracking:

1. **agent_usage_logs** - Detailed query-level tracking
2. **session_summaries** - Session-level analytics

## Setup Options

### Option 1: Automatic Setup (Recommended)
The template will check for tables on startup and provide SQL if missing.

### Option 2: Manual Setup
Execute the SQL provided by the setup system in your database.

### Option 3: No Database Mode
Set `DISABLE_ANALYTICS=true` to run without database persistence.
Analytics will use in-memory tracking only.

## Environment Variables

```bash
# Database connection
SUPABASE_URL=your_database_url
SUPABASE_KEY=your_database_key

# Optional: Disable database analytics
DISABLE_ANALYTICS=false
```

## Database Types Supported

- PostgreSQL (recommended)
- Supabase (PostgreSQL-based)
- SQLite (for development)
- Any PostgreSQL-compatible database
"""
