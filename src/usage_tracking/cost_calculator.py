# src/usage_tracking/cost_calculator.py
"""
Cost Calculation Utilities for LLM Usage and Compute Resources

Based on the Industrial Engineering Agent's cost_calculator.py but enhanced
with configurable pricing and better error handling.

Calculates costs for:
- OpenAI and DeepSeek API usage
- Estimated cloud compute costs
- Resource usage (CPU, memory, processing time)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("cost_calculator")


class CostCalculator:
    """
    Calculates costs for LLM usage and compute resources.
    
    Provides cost calculations for current development (estimates) and 
    future cloud hosting (actual costs).
    """
    
    def __init__(self, custom_pricing: Optional[Dict[str, Any]] = None):
        """
        Initialize the cost calculator with pricing configuration.
        
        Args:
            custom_pricing: Optional custom pricing overrides
        """
        # Default LLM API Pricing (per 1000 tokens) - Updated pricing
        self.llm_pricing = {
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
        
        # Cloud Compute Pricing (estimates for Google Cloud)
        self.compute_pricing = {
            # Cloud Run (Serverless) - per second
            "cloud_run": {
                "cpu_per_second": 0.00002400,      # $0.024 per vCPU-hour / 3600
                "memory_per_gb_second": 0.00000250  # $0.0025 per GB-hour / 3600
            },
            
            # Compute Engine (Dedicated) - per second  
            "compute_engine": {
                "n1_standard_1": 0.000013194,      # $0.0475/hour / 3600
                "n1_standard_2": 0.000026389,      # $0.0950/hour / 3600
                "n1_standard_4": 0.000052778       # $0.1900/hour / 3600
            },
            
            # AWS alternatives
            "aws_lambda": {
                "request_cost": 0.0000002,          # $0.20 per 1M requests
                "duration_cost_per_gb_ms": 0.0000166667  # $0.0000166667 per GB-ms
            }
        }
        
        # Apply custom pricing overrides
        if custom_pricing:
            self._apply_custom_pricing(custom_pricing)
        
        logger.info("Cost calculator initialized with current pricing")
    
    def _apply_custom_pricing(self, custom_pricing: Dict[str, Any]):
        """Apply custom pricing overrides."""
        try:
            if "llm_pricing" in custom_pricing:
                self.llm_pricing.update(custom_pricing["llm_pricing"])
            
            if "compute_pricing" in custom_pricing:
                for provider, pricing in custom_pricing["compute_pricing"].items():
                    if provider in self.compute_pricing:
                        self.compute_pricing[provider].update(pricing)
                    else:
                        self.compute_pricing[provider] = pricing
            
            logger.info("Applied custom pricing configuration")
        except Exception as e:
            logger.error(f"Error applying custom pricing: {e}")
    
    def calculate_llm_cost(self, 
                          model: str, 
                          input_tokens: int, 
                          output_tokens: int) -> Dict[str, Any]:
        """
        Calculate LLM API cost based on token usage.
        
        Args:
            model: Model name (e.g., 'gpt-4o-mini', 'deepseek-chat')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Dictionary with cost breakdown
        """
        try:
            pricing = self.llm_pricing.get(model, {"input": 0.0, "output": 0.0})
            
            if pricing["input"] == 0.0 and pricing["output"] == 0.0:
                logger.warning(f"No pricing found for model: {model}")
            
            input_cost = (input_tokens / 1000) * pricing["input"]
            output_cost = (output_tokens / 1000) * pricing["output"]
            total_cost = input_cost + output_cost
            
            return {
                "input_cost": round(input_cost, 6),
                "output_cost": round(output_cost, 6),
                "total_llm_cost": round(total_cost, 6),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": model,
                "cost_per_input_1k": pricing["input"],
                "cost_per_output_1k": pricing["output"]
            }
            
        except Exception as e:
            logger.error(f"Error calculating LLM cost: {e}")
            return {
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_llm_cost": 0.0,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": model,
                "error": str(e)
            }
    
    def calculate_cloud_run_cost(self, 
                                processing_time_ms: int, 
                                memory_usage_mb: int = 512) -> Dict[str, Any]:
        """
        Calculate estimated Cloud Run (serverless) compute cost.
        
        Args:
            processing_time_ms: Processing time in milliseconds
            memory_usage_mb: Memory usage in MB (default 512MB)
            
        Returns:
            Dictionary with compute cost breakdown
        """
        try:
            processing_time_seconds = processing_time_ms / 1000
            memory_usage_gb = memory_usage_mb / 1024
            
            pricing = self.compute_pricing["cloud_run"]
            
            cpu_cost = processing_time_seconds * pricing["cpu_per_second"]
            memory_cost = processing_time_seconds * memory_usage_gb * pricing["memory_per_gb_second"]
            total_compute_cost = cpu_cost + memory_cost
            
            return {
                "cpu_cost": round(cpu_cost, 8),
                "memory_cost": round(memory_cost, 8),
                "total_compute_cost": round(total_compute_cost, 8),
                "processing_time_ms": processing_time_ms,
                "memory_usage_mb": memory_usage_mb,
                "hosting_type": "cloud_run"
            }
            
        except Exception as e:
            logger.error(f"Error calculating Cloud Run cost: {e}")
            return {
                "cpu_cost": 0.0,
                "memory_cost": 0.0,
                "total_compute_cost": 0.0,
                "processing_time_ms": processing_time_ms,
                "memory_usage_mb": memory_usage_mb,
                "hosting_type": "cloud_run",
                "error": str(e)
            }
            # Calculate cost breakdown percentages
            llm_percentage = (llm_cost["total_llm_cost"] / total_cost * 100) if total_cost > 0 else 0
            compute_percentage = (compute_cost["total_compute_cost"] / total_cost * 100) if total_cost > 0 else 0
            
            return {
                "llm_costs": llm_cost,
                "compute_costs": compute_cost,
                "total_cost": round(total_cost, 6),
                "cost_breakdown": {
                    "llm_percentage": round(llm_percentage, 1),
                    "compute_percentage": round(compute_percentage, 1)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating total query cost: {e}")
            return {
                "llm_costs": {"total_llm_cost": 0.0},
                "compute_costs": {"total_compute_cost": 0.0},
                "total_cost": 0.0,
                "cost_breakdown": {"llm_percentage": 0, "compute_percentage": 0},
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def estimate_monthly_cost(self, 
                            daily_queries: int,
                            avg_tokens_per_query: int = 1000,
                            avg_processing_time_ms: int = 2000,
                            model: str = "gpt-4o-mini") -> Dict[str, float]:
        """
        Estimate monthly costs based on usage patterns.
        
        Args:
            daily_queries: Average queries per day
            avg_tokens_per_query: Average tokens per query (input + output)
            avg_processing_time_ms: Average processing time per query
            model: Primary LLM model used
            
        Returns:
            Dictionary with monthly cost estimates
        """
        try:
            # Assume 70% input, 30% output tokens
            input_tokens = int(avg_tokens_per_query * 0.7)
            output_tokens = int(avg_tokens_per_query * 0.3)
            
            # Calculate cost per query
            query_cost = self.calculate_total_query_cost(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                processing_time_ms=avg_processing_time_ms
            )
            
            # Monthly estimates (30 days)
            monthly_queries = daily_queries * 30
            monthly_cost = query_cost["total_cost"] * monthly_queries
            
            return {
                "cost_per_query": round(query_cost["total_cost"], 6),
                "daily_cost": round(query_cost["total_cost"] * daily_queries, 2),
                "monthly_cost": round(monthly_cost, 2),
                "monthly_queries": monthly_queries,
                "llm_monthly_cost": round(query_cost["llm_costs"]["total_llm_cost"] * monthly_queries, 2),
                "compute_monthly_cost": round(query_cost["compute_costs"]["total_compute_cost"] * monthly_queries, 2),
                "model": model,
                "assumptions": {
                    "daily_queries": daily_queries,
                    "avg_tokens_per_query": avg_tokens_per_query,
                    "avg_processing_time_ms": avg_processing_time_ms,
                    "input_output_ratio": "70/30"
                }
            }
            
        except Exception as e:
            logger.error(f"Error estimating monthly cost: {e}")
            return {
                "error": str(e),
                "cost_per_query": 0.0,
                "daily_cost": 0.0,
                "monthly_cost": 0.0
            }
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Get current pricing information for all models and compute options.
        
        Returns:
            Dictionary with all pricing data
        """
        return {
            "llm_pricing": self.llm_pricing,
            "compute_pricing": self.compute_pricing,
            "last_updated": "2024-12-01",
            "currency": "USD"
        }
    
    def update_pricing(self, model: str, input_cost: float, output_cost: float) -> bool:
        """
        Update pricing for a specific model.
        
        Args:
            model: Model name to update
            input_cost: Cost per 1000 input tokens
            output_cost: Cost per 1000 output tokens
            
        Returns:
            True if successfully updated
        """
        try:
            self.llm_pricing[model] = {
                "input": input_cost,
                "output": output_cost
            }
            logger.info(f"Updated pricing for {model}: input=${input_cost}, output=${output_cost}")
            return True
        except Exception as e:
            logger.error(f"Error updating pricing for {model}: {e}")
            return False
    
    def get_cost_optimization_suggestions(self, usage_data: Dict[str, Any]) -> List[str]:
        """
        Get cost optimization suggestions based on usage patterns.
        
        Args:
            usage_data: Usage statistics and patterns
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        try:
            # Analyze model usage
            if "model_usage" in usage_data:
                expensive_models = ["gpt-4", "gpt-4-turbo-preview", "claude-3-opus"]
                for model in expensive_models:
                    if model in usage_data["model_usage"] and usage_data["model_usage"][model] > 0.5:
                        suggestions.append(f"Consider using gpt-4o-mini instead of {model} for simple queries")
            
            # Analyze response times
            if "avg_processing_time_ms" in usage_data and usage_data["avg_processing_time_ms"] > 5000:
                suggestions.append("High processing times detected - consider optimizing prompts or using faster models")
            
            # Analyze token usage
            if "avg_tokens_per_query" in usage_data and usage_data["avg_tokens_per_query"] > 2000:
                suggestions.append("High token usage detected - consider shorter prompts or response limits")
            
            # Analyze query patterns
            if "daily_queries" in usage_data and usage_data["daily_queries"] > 1000:
                suggestions.append("High query volume - consider implementing query caching")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating cost optimization suggestions: {e}")
            return ["Error generating suggestions - check usage data format"]
    
    def calculate_cost_savings(self, 
                             current_model: str, 
                             alternative_model: str,
                             monthly_queries: int,
                             avg_tokens_per_query: int = 1000) -> Dict[str, Any]:
        """
        Calculate potential cost savings by switching models.
        
        Args:
            current_model: Current model being used
            alternative_model: Alternative model to compare
            monthly_queries: Number of queries per month
            avg_tokens_per_query: Average tokens per query
            
        Returns:
            Cost comparison and savings analysis
        """
        try:
            input_tokens = int(avg_tokens_per_query * 0.7)
            output_tokens = int(avg_tokens_per_query * 0.3)
            
            # Calculate costs for current model
            current_cost = self.calculate_llm_cost(current_model, input_tokens, output_tokens)
            current_monthly_cost = current_cost["total_llm_cost"] * monthly_queries
            
            # Calculate costs for alternative model
            alternative_cost = self.calculate_llm_cost(alternative_model, input_tokens, output_tokens)
            alternative_monthly_cost = alternative_cost["total_llm_cost"] * monthly_queries
            
            # Calculate savings
            monthly_savings = current_monthly_cost - alternative_monthly_cost
            annual_savings = monthly_savings * 12
            percentage_savings = (monthly_savings / current_monthly_cost * 100) if current_monthly_cost > 0 else 0
            
            return {
                "current_model": current_model,
                "alternative_model": alternative_model,
                "current_cost_per_query": round(current_cost["total_llm_cost"], 6),
                "alternative_cost_per_query": round(alternative_cost["total_llm_cost"], 6),
                "current_monthly_cost": round(current_monthly_cost, 2),
                "alternative_monthly_cost": round(alternative_monthly_cost, 2),
                "monthly_savings": round(monthly_savings, 2),
                "annual_savings": round(annual_savings, 2),
                "percentage_savings": round(percentage_savings, 1),
                "recommendation": "switch" if monthly_savings > 0 else "keep_current"
            }
            
        except Exception as e:
            logger.error(f"Error calculating cost savings: {e}")
            return {"error": str(e)}
