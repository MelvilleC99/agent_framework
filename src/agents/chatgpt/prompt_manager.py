# src/agents/chatgpt/prompt_manager.py
"""
Prompt and Date Management for ChatGPT Agent

Based on the Industrial Engineering Agent's prompt_manager.py but enhanced
with configurable prompt paths and better error handling.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger("prompt_manager")


class PromptManager:
    """
    Manages system prompts and date handling for the ChatGPT agent.
    
    This component handles:
    - System prompt loading from files or fallback
    - Date utilities and formatting
    - Prompt caching and refresh
    """
    
    def __init__(self, prompt_path: Optional[str] = None):
        """
        Initialize the prompt manager.
        
        Args:
            prompt_path: Optional path to system prompt file
        """
        self.prompt_path = prompt_path or os.getenv("CHATGPT_SYSTEM_PROMPT_PATH")
        self.current_date = self._get_current_date()
        self.system_prompt = self._load_system_prompt()
        logger.info("PromptManager initialized")
    
    def _get_current_date(self) -> Dict[str, str]:
        """Get the current date in multiple formats."""
        now = datetime.now()
        return {
            "current_date": now.strftime("%Y-%m-%d"),
            "current_datetime": now.isoformat(),
            "formatted_date": now.strftime("%B %d, %Y"),
            "day_of_week": now.strftime("%A"),
            "time": now.strftime("%H:%M:%S")
        }
    
    def refresh_date(self):
        """Refresh the cached date - useful for long-running sessions."""
        self.current_date = self._get_current_date()
        logger.info(f"Refreshed current date to: {self.current_date['formatted_date']}")
    
    def get_current_date(self) -> Dict[str, str]:
        """Get the current date information."""
        return self.current_date.copy()

    def _load_system_prompt(self) -> str:
        """Load the system prompt from file or use fallback."""
        try:
            # Try loading from specified path
            if self.prompt_path and os.path.exists(self.prompt_path):
                with open(self.prompt_path, 'r') as f:
                    prompt = f.read().strip()
                
                logger.info(f"Loaded system prompt from {self.prompt_path}")
                return prompt
            
            # Try loading from domain prompts directory
            domain_prompt_path = "/Users/melville/Documents/qc_agent_backend/src/domain/prompts/system.txt"
            if os.path.exists(domain_prompt_path):
                with open(domain_prompt_path, 'r') as f:
                    prompt = f.read().strip()
                
                logger.info(f"Loaded system prompt from {domain_prompt_path}")
                return prompt
            
            # Try loading from various common locations
            common_paths = [
                "domain/prompts/system.txt",
                "prompts/system.txt", 
                "../prompts/system.txt",
                "../../prompts/system.txt"
            ]
            
            for path in common_paths:
                full_path = os.path.abspath(path)
                if os.path.exists(full_path):
                    with open(full_path, 'r') as f:
                        prompt = f.read().strip()
                    
                    logger.info(f"Loaded system prompt from {full_path}")
                    return prompt
                
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")
        
        # Fallback to enhanced minimal prompt
        logger.info("Using fallback system prompt")
        return self._get_fallback_prompt()
    
    def _get_fallback_prompt(self) -> str:
        """Get fallback system prompt when no file is available."""
        return """You are a helpful AI assistant for quality control operations.

Your goal is to help users with:
1. Data analysis and reporting
2. Process optimization
3. Quality metrics and tracking
4. General questions and assistance

When answering questions:
- ALWAYS use the current date provided by the get_current_date function result
- The current date is provided at the start of each conversation
- Use this date for all calculations and comparisons
- Never guess or use a date from training data
- Consider the context of previous messages
- For follow-up questions, analyze the previous response
- Be specific and helpful in your responses
- When data shows issues, calculate relevant metrics based on the current date

For complex analysis that requires deep investigation, indicate that more detailed analysis is needed."""
    
    def get_system_prompt(self) -> str:
        """Get the system prompt."""
        return self.system_prompt
    
    def reload_prompt(self) -> bool:
        """
        Reload the system prompt from file.
        
        Returns:
            True if successfully reloaded, False otherwise
        """
        try:
            old_prompt = self.system_prompt
            self.system_prompt = self._load_system_prompt()
            
            if self.system_prompt != old_prompt:
                logger.info("System prompt reloaded successfully")
                return True
            else:
                logger.info("System prompt unchanged after reload")
                return True
                
        except Exception as e:
            logger.error(f"Error reloading system prompt: {e}")
            return False
    
    def update_prompt_path(self, new_path: str) -> bool:
        """
        Update the prompt file path and reload.
        
        Args:
            new_path: New path to system prompt file
            
        Returns:
            True if successfully updated, False otherwise
        """
        try:
            if not os.path.exists(new_path):
                logger.error(f"Prompt file not found: {new_path}")
                return False
            
            self.prompt_path = new_path
            return self.reload_prompt()
            
        except Exception as e:
            logger.error(f"Error updating prompt path: {e}")
            return False
    
    def get_prompt_info(self) -> Dict[str, str]:
        """Get information about the current prompt configuration."""
        return {
            "prompt_path": self.prompt_path or "Using fallback prompt",
            "prompt_length": str(len(self.system_prompt)),
            "last_updated": self.current_date["current_datetime"],
            "source": "file" if self.prompt_path and os.path.exists(self.prompt_path) else "fallback"
        }
