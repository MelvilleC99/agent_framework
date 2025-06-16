# Learning Layer Package
"""
Continuous improvement system for agent performance optimization.

This package provides:
- Feedback collection and outcome tracking
- Adaptation mechanisms for system improvement
- Metrics for learning effectiveness measurement
"""

from .feedback import *
from .adaptation import *
from .metrics import *

__version__ = "1.0.0"
__all__ = ["feedback", "adaptation", "metrics"]