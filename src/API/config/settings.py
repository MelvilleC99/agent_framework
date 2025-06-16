# src/api/config/settings.py
"""
Environment Configuration

Uses Pydantic for environment variable validation and settings management.
"""

import os
from typing import Optional, Literal
from pydantic import BaseSettings, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    
    # Database
    supabase_url: str
    supabase_key: str
    disable_analytics: bool = False
    
    # LLM APIs
    openai_api_key: str
    deepseek_api_key: Optional[str] = None
    
    # Redis (optional)
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Agent Configuration
    agent_name: str = "QC Agent"
    max_session_duration_minutes: int = 30
    max_context_history: int = 6
    tools_directory: str = "src/tools"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    @validator("environment")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production")
        return v
    
    @validator("debug", pre=True, always=True)
    def set_debug(cls, v, values):
        # Auto-set debug based on environment
        if "environment" in values:
            return values["environment"] == "development"
        return v
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).
    
    This function is cached so settings are only loaded once.
    """
    return Settings()
