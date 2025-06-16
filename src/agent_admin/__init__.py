# Agent Administration Package
"""
Production-ready operational components for agent deployment and management.

This package provides:
- Testing framework for comprehensive validation
- Monitoring dashboard for system health tracking
- Logging infrastructure for audit trails and debugging
- Configuration management for environment settings
- Deployment tools for production operations
"""

from .testing import *
from .monitoring_dashboard import *
from .logging import *
from .config import *
from .deployment import *

__version__ = "1.0.0"
__all__ = ["testing", "monitoring_dashboard", "logging", "config", "deployment"]