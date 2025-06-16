# src/usage_tracking/token_tracker.py
"""
Token Usage Tracking for LLM Sessions

Based on the Industrial Engineering Agent's token_tracker.py but enhanced
with better error handling and configurable pricing.

Tracks token usage and costs for different LLM models in real-time.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

logger = logging.getLogger("token_tracker")


class TokenTracker:
    """
    Tracks token usage and costs for different LLM models.
    
    This class helps monitor token consumption and estimated costs
    for different models to optimize usage and budget.
    """
    
    def __init__(self, pricing: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialize the token tracker.
        
        Args:
            pricing: Optional custom pricing dictionary
        """
        # Default pricing per 1000 tokens (updated pricing)
        self.pricing = pricing or {
            # OpenAI models
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015},
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4": {"input": 0.03, "output": 0.06},
            
            # DeepSeek models
            "deepseek-chat": {"input": 0.0003, "output": 0.0006},
            "deepseek-coder": {"input": 0.00015, "output": 0.0006},
            
            # Claude models (for future use)
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-opus": {"input": 0.015, "output": 0.075}
        }
        
        self.session_usage = {
            "openai": {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0},
            "deepseek": {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0},
            "claude": {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}
        }
        self.requests = []
        
        logger.info("Token tracker initialized")
    
    def track_openai_usage(self, response: Any) -> Dict[str, Any]:
        """
        Track token usage from an OpenAI API response.
        
        Args:
            response: OpenAI API response object
            
        Returns:
            Dictionary with token usage statistics
        """
        usage = {}
        model = "unknown"
        
        try:
            if hasattr(response, "model"):
                model = response.model
                
            if hasattr(response, "usage"):
                usage = {
                    "total_tokens": response.usage.total_tokens,
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "model": model,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Calculate cost
                model_pricing = self.pricing.get(model, {"input": 0.0, "output": 0.0})
                cost = (
                    (usage["input_tokens"] / 1000) * model_pricing["input"] +
                    (usage["output_tokens"] / 1000) * model_pricing["output"]
                )
                usage["cost"] = cost
                
                # Update session totals
                self.session_usage["openai"]["total_tokens"] += usage["total_tokens"]
                self.session_usage["openai"]["input_tokens"] += usage["input_tokens"]
                self.session_usage["openai"]["output_tokens"] += usage["output_tokens"]
                self.session_usage["openai"]["cost"] += cost
                
                # Log the usage
                self._log_usage("openai", model, usage)
                
                logger.info(f"OpenAI usage: {usage['total_tokens']} tokens, ${cost:.4f}")
            else:
                logger.warning("Unable to extract token usage from OpenAI response")
        except Exception as e:
            logger.error(f"Error tracking OpenAI token usage: {e}")
        
        return usage
    
    def track_deepseek_usage(self, 
                             prompt_tokens: int, 
                             completion_tokens: int, 
                             model: str = "deepseek-chat") -> Dict[str, Any]:
        """
        Track token usage for DeepSeek API calls.
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: DeepSeek model name
            
        Returns:
            Dictionary with token usage statistics
        """
        try:
            total_tokens = prompt_tokens + completion_tokens
            
            usage = {
                "total_tokens": total_tokens,
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            
            # Calculate cost
            model_pricing = self.pricing.get(model, {"input": 0.0, "output": 0.0})
            cost = (
                (prompt_tokens / 1000) * model_pricing["input"] +
                (completion_tokens / 1000) * model_pricing["output"]
            )
            usage["cost"] = cost
            
            # Update session totals
            self.session_usage["deepseek"]["total_tokens"] += total_tokens
            self.session_usage["deepseek"]["input_tokens"] += prompt_tokens
            self.session_usage["deepseek"]["output_tokens"] += completion_tokens
            self.session_usage["deepseek"]["cost"] += cost
            
            # Log the usage
            self._log_usage("deepseek", model, usage)
            
            logger.info(f"DeepSeek usage: {total_tokens} tokens, ${cost:.4f}")
            
            return usage
        except Exception as e:
            logger.error(f"Error tracking DeepSeek token usage: {e}")
            return {}
    
    def track_claude_usage(self,
                          input_tokens: int,
                          output_tokens: int,
                          model: str = "claude-3-haiku") -> Dict[str, Any]:
        """
        Track token usage for Claude API calls.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Claude model name
            
        Returns:
            Dictionary with token usage statistics
        """
        try:
            total_tokens = input_tokens + output_tokens
            
            usage = {
                "total_tokens": total_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            
            # Calculate cost
            model_pricing = self.pricing.get(model, {"input": 0.0, "output": 0.0})
            cost = (
                (input_tokens / 1000) * model_pricing["input"] +
                (output_tokens / 1000) * model_pricing["output"]
            )
            usage["cost"] = cost
            
            # Update session totals
            self.session_usage["claude"]["total_tokens"] += total_tokens
            self.session_usage["claude"]["input_tokens"] += input_tokens
            self.session_usage["claude"]["output_tokens"] += output_tokens
            self.session_usage["claude"]["cost"] += cost
            
            # Log the usage
            self._log_usage("claude", model, usage)
            
            logger.info(f"Claude usage: {total_tokens} tokens, ${cost:.4f}")
            
            return usage
        except Exception as e:
            logger.error(f"Error tracking Claude token usage: {e}")
            return {}
    
    def _log_usage(self, provider: str, model: str, usage: Dict[str, Any]) -> None:
        """
        Log token usage internally.
        
        Args:
            provider: LLM provider name
            model: Model name
            usage: Usage statistics
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "provider": provider,
                "model": model,
                "usage": usage
            }
            
            self.requests.append(log_entry)
            
            # Keep only recent requests (last 100)
            if len(self.requests) > 100:
                self.requests = self.requests[-100:]
                
        except Exception as e:
            logger.error(f"Error logging token usage: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of token usage for the current session.
        
        Returns:
            Dictionary with session usage statistics
        """
        try:
            total_cost = (
                self.session_usage["openai"]["cost"] +
                self.session_usage["deepseek"]["cost"] +
                self.session_usage["claude"]["cost"]
            )
            
            total_tokens = (
                self.session_usage["openai"]["total_tokens"] +
                self.session_usage["deepseek"]["total_tokens"] +
                self.session_usage["claude"]["total_tokens"]
            )
            
            return {
                "providers": self.session_usage,
                "totals": {
                    "total_cost": round(total_cost, 6),
                    "total_tokens": total_tokens,
                    "total_input_tokens": (
                        self.session_usage["openai"]["input_tokens"] +
                        self.session_usage["deepseek"]["input_tokens"] +
                        self.session_usage["claude"]["input_tokens"]
                    ),
                    "total_output_tokens": (
                        self.session_usage["openai"]["output_tokens"] +
                        self.session_usage["deepseek"]["output_tokens"] +
                        self.session_usage["claude"]["output_tokens"]
                    )
                },
                "request_count": len(self.requests),
                "session_start": self.requests[0]["timestamp"] if self.requests else datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            return {"error": str(e)}
    
    def reset_session(self) -> None:
        """Reset the session usage statistics."""
        try:
            self.session_usage = {
                "openai": {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0},
                "deepseek": {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0},
                "claude": {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}
            }
            self.requests = []
            logger.info("Token tracker session reset")
        except Exception as e:
            logger.error(f"Error resetting session: {e}")
    
    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get detailed cost breakdown by provider and model."""
        try:
            breakdown = {}
            
            for request in self.requests:
                provider = request.get("provider", "unknown")
                model = request.get("model", "unknown")
                usage = request.get("usage", {})
                cost = usage.get("cost", 0)
                
                if provider not in breakdown:
                    breakdown[provider] = {}
                
                if model not in breakdown[provider]:
                    breakdown[provider][model] = {
                        "requests": 0,
                        "total_cost": 0.0,
                        "total_tokens": 0,
                        "input_tokens": 0,
                        "output_tokens": 0
                    }
                
                breakdown[provider][model]["requests"] += 1
                breakdown[provider][model]["total_cost"] += cost
                breakdown[provider][model]["total_tokens"] += usage.get("total_tokens", 0)
                breakdown[provider][model]["input_tokens"] += usage.get("input_tokens", 0)
                breakdown[provider][model]["output_tokens"] += usage.get("output_tokens", 0)
            
            # Round costs
            for provider in breakdown:
                for model in breakdown[provider]:
                    breakdown[provider][model]["total_cost"] = round(
                        breakdown[provider][model]["total_cost"], 6
                    )
                    breakdown[provider][model]["avg_cost_per_request"] = round(
                        breakdown[provider][model]["total_cost"] / breakdown[provider][model]["requests"], 6
                    ) if breakdown[provider][model]["requests"] > 0 else 0
            
            return breakdown
        except Exception as e:
            logger.error(f"Error getting cost breakdown: {e}")
            return {"error": str(e)}
    
    def update_pricing(self, model: str, input_cost: float, output_cost: float) -> bool:
        """
        Update pricing for a specific model.
        
        Args:
            model: Model name
            input_cost: Cost per 1000 input tokens
            output_cost: Cost per 1000 output tokens
            
        Returns:
            True if successfully updated
        """
        try:
            self.pricing[model] = {
                "input": input_cost,
                "output": output_cost
            }
            logger.info(f"Updated pricing for {model}: input=${input_cost}, output=${output_cost}")
            return True
        except Exception as e:
            logger.error(f"Error updating pricing: {e}")
            return False
    
    def get_usage_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get usage trends for the specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Usage trend analysis
        """
        try:
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            recent_requests = []
            
            for request in self.requests:
                try:
                    request_time = datetime.fromisoformat(request["timestamp"]).timestamp()
                    if request_time >= cutoff_time:
                        recent_requests.append(request)
                except:
                    continue
            
            if not recent_requests:
                return {"message": f"No requests found in the last {hours} hours"}
            
            # Analyze trends
            total_cost = sum(req["usage"].get("cost", 0) for req in recent_requests)
            total_tokens = sum(req["usage"].get("total_tokens", 0) for req in recent_requests)
            
            # Group by hour
            hourly_usage = {}
            for request in recent_requests:
                try:
                    hour = datetime.fromisoformat(request["timestamp"]).strftime("%Y-%m-%d %H:00")
                    if hour not in hourly_usage:
                        hourly_usage[hour] = {"requests": 0, "cost": 0.0, "tokens": 0}
                    
                    hourly_usage[hour]["requests"] += 1
                    hourly_usage[hour]["cost"] += request["usage"].get("cost", 0)
                    hourly_usage[hour]["tokens"] += request["usage"].get("total_tokens", 0)
                except:
                    continue
            
            return {
                "period_hours": hours,
                "total_requests": len(recent_requests),
                "total_cost": round(total_cost, 6),
                "total_tokens": total_tokens,
                "avg_cost_per_request": round(total_cost / len(recent_requests), 6) if recent_requests else 0,
                "avg_tokens_per_request": round(total_tokens / len(recent_requests), 1) if recent_requests else 0,
                "hourly_breakdown": hourly_usage
            }
        except Exception as e:
            logger.error(f"Error getting usage trends: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the token tracker."""
        try:
            return {
                "status": "healthy",
                "active_providers": list(self.session_usage.keys()),
                "total_requests_logged": len(self.requests),
                "session_active": any(usage["total_tokens"] > 0 for usage in self.session_usage.values()),
                "pricing_models_configured": len(self.pricing)
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global token tracker instance
token_tracker = TokenTracker()
