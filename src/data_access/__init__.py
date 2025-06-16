# Data Access Layer Package
"""
Database abstraction layer for unified data operations.

This package provides:
- Repository patterns for abstract data interfaces
- Adapters for specific database implementations
- Query templates for common operations
- Data models and schemas
"""

from .repositories import *
from .adapters import *
from .queries import *
from .models import *

__version__ = "1.0.0"
__all__ = ["repositories", "adapters", "queries", "models"]