# Decisions Layer Package
"""
Decision-making framework for autonomous agent operations.

This package provides:
- Thresholds for condition evaluation
- Decision matrices for complex analysis
- Escalation rules for stakeholder management
"""

from .thresholds import *
from .matrices import *
from .escalation_rules import *

__version__ = "1.0.0"
__all__ = ["thresholds", "matrices", "escalation_rules"]