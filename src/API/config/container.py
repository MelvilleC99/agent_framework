# src/api/config/container.py
"""
Dependency Injection Container

Manages all application dependencies and their lifecycles.
"""

import logging
from typing import Optional
import redis.asyncio as redis
from .settings import Settings
from .database import DatabaseManager

logger = logging.getLogger("container")


class Container:
    """
    Dependency injection container for the QC Agent API.
    
    This container manages the lifecycle of all dependencies:
    - Database connections
    - Redis connections  
    - Agent orchestrator
    - Tool registry
    """
    
    def __init__(self):
        self._database_manager: Optional[DatabaseManager] = None
        self._redis_client: Optional[redis.Redis] = None
        self._orchestrator = None
        self._tool_registry = None
        self._usage_tracker = None
        self._session_summarizer = None
        self._initialized = False
    
    async def initialize(self, settings: Settings) -> None:
        """
        Initialize all dependencies.
        
        Args:
            settings: Application settings
        """
        if self._initialized:
            logger.warning("Container already initialized")
            return
        
        logger.info("🔧 Initializing dependency container...")
        
        try:
            # 1. Initialize database
            self._database_manager = DatabaseManager()
            await self._database_manager.initialize(
                settings.supabase_url, 
                settings.supabase_key
            )
            logger.info("✅ Database manager initialized")
            
            # 1.1. Check and setup database tables
            if not settings.disable_analytics:
                from ...database.migrations import run_migrations
                migration_result = await run_migrations(self._database_manager.get_client())
                if migration_result["status"] == "manual_setup_required":
                    logger.warning("⚠️  Database setup required - analytics will be disabled")
                    settings.disable_analytics = True
            else:
                logger.info("📊 Analytics disabled by configuration")
            
            # 2. Initialize Redis (optional)
            if settings.redis_url:
                try:
                    self._redis_client = redis.from_url(settings.redis_url)
                    await self._redis_client.ping()
                    logger.info("✅ Redis client initialized")
                except Exception as e:
                    logger.warning(f"Redis initialization failed: {e}")
                    self._redis_client = None
            
            # 3. Initialize tool registry
            from ...tool_registry.registry import tool_registry
            from ...tool_registry.executor import ToolExecutor
            from ...usage_tracking.usage_tracker import UsageTracker
            from ...usage_tracking.session_summarizer import SessionSummarizer
            
            # Use the global registry and auto-discover tools
            self._tool_registry = tool_registry
            
            # Auto-discover tools from the tools directory
            import os
            tools_path = os.path.join(os.getcwd(), settings.tools_directory)
            try:
                discovered = self._tool_registry.auto_discover_tools(tools_path, "data_retrieval")
                logger.info(f"✅ Discovered {discovered} tools from {tools_path}")
            except Exception as e:
                logger.warning(f"Tool discovery failed: {e}")
            
            # Initialize analytics components (optional)
            if not settings.disable_analytics:
                self._usage_tracker = UsageTracker(database=self._database_manager.get_client())
                self._session_summarizer = SessionSummarizer(database=self._database_manager.get_client())
                logger.info("✅ Analytics components initialized")
            else:
                # Use no-op analytics for template mode
                from ...usage_tracking.no_op_tracker import NoOpUsageTracker, NoOpSessionSummarizer
                self._usage_tracker = NoOpUsageTracker()
                self._session_summarizer = NoOpSessionSummarizer()
                logger.info("✅ No-op analytics initialized (template mode)")
            
            logger.info("✅ Tool registry and analytics initialized")
            
            self._initialized = True
            logger.info("🎯 Container initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Container initialization failed: {e}")
            await self.cleanup()
            raise
    
    async def get_orchestrator(self):
        """Get the agent orchestrator (lazy initialization)."""
        if not self._initialized:
            raise RuntimeError("Container not initialized")
        
        if self._orchestrator is None:
            from ...orchestration.coordinator import AgentOrchestrator
            self._orchestrator = AgentOrchestrator(
                database=self._database_manager.get_client(),
                redis=self._redis_client,
                tool_registry=self._tool_registry,
                usage_tracker=self._usage_tracker,
                session_summarizer=self._session_summarizer
            )
            logger.info("✅ Orchestrator initialized")
        
        return self._orchestrator
    
    def get_database(self):
        """Get the database client."""
        if not self._initialized:
            raise RuntimeError("Container not initialized")
        return self._database_manager.get_client()
    
    def get_redis(self):
        """Get the Redis client."""
        return self._redis_client
    
    def get_tool_registry(self):
        """Get the tool registry."""
        if not self._initialized:
            raise RuntimeError("Container not initialized")
        return self._tool_registry
    
    def get_usage_tracker(self):
        """Get the usage tracker."""
        if not self._initialized:
            raise RuntimeError("Container not initialized")
        return self._usage_tracker
    
    def get_session_summarizer(self):
        """Get the session summarizer."""
        if not self._initialized:
            raise RuntimeError("Container not initialized")
        return self._session_summarizer
    
    async def cleanup(self) -> None:
        """Cleanup all resources."""
        logger.info("🧹 Cleaning up container resources...")
        
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
        
        if self._database_manager:
            await self._database_manager.cleanup()
            self._database_manager = None
        
        self._orchestrator = None
        self._tool_registry = None
        self._initialized = False
        
        logger.info("✅ Container cleanup complete")
