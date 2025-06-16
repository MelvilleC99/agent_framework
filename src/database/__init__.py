# src/database/__init__.py
"""
Database Setup and Migration System

Provides database schema creation and migration utilities
for the agent template.
"""

from .setup import DatabaseSetup
from .migrations import run_migrations, check_tables_exist

__all__ = [
    "DatabaseSetup",
    "run_migrations", 
    "check_tables_exist"
]
