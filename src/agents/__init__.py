# src/agents/__init__.py
"""
Agents Package

Contains all agent implementations with modular, standardized components.
"""

from .base import BaseAgent
from .chatgpt import ChatGPTAgent

__all__ = [
    'BaseAgent',
    'ChatGPTAgent'
]
