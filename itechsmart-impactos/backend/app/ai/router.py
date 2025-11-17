"""
AI Model Router - Intelligent routing and load balancing
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
from enum import Enum
import asyncio
from datetime import datetime, timedelta
from app.ai.models import AIModel, AIModelFactory
from app.core.config import settings


class RoutingStrategy(str, Enum):
    """Routing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_LATENCY = "least_latency"
    COST_OPTIMIZED = "cost_optimized"
    QUALITY_OPTIMIZED = "quality_optimized"
    FAILOVER = "failover"


class ModelMetrics:
    """Track metrics for each model"""

    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency = 0.0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.last_used = None
        self.error_rate = 0.0

    def record_request(
        self, success: bool, latency: float, tokens: int = 0, cost: float = 0.0
    ):
        """Record a request"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.total_latency += latency
        self.total_tokens += tokens
        self.total_cost += cost
        self.last_used = datetime.utcnow()
        self.error_rate = (
            self.failed_requests / self.total_requests
            if self.total_requests > 0
            else 0.0
        )

    @property
    def average_latency(self) -> float:
        """Get average latency"""
        return (
            self.total_latency / self.successful_requests
            if self.successful_requests > 0
            else float("inf")
        )

    @property
    def success_rate(self) -> float:
        """Get success rate"""
        return (
            self.successful_requests / self.total_requests
            if self.total_requests > 0
            else 0.0
        )


class AIModelRouter:
    """
    Intelligent AI model router with load balancing and failover
    """

    def __init__(self, strategy: RoutingStrategy = RoutingStrategy.QUALITY_OPTIMIZED):
        """
        Initialize AI model router

        Args:
            strategy: Routing strategy to use
        """
        self.strategy = strategy
        self.models: Dict[str, AIModel] = {}
        self.metrics: Dict[str, ModelMetrics] = {}
        self.current_index = 0

        # Model costs per 1K tokens (approximate)
        self.model_costs = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.002,
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
            "claude-3-haiku": 0.00025,
            "gemini-pro": 0.00025,
        }

        # Model quality scores (subjective, 0-100)
        self.model_quality = {
            "gpt-4": 95,
            "gpt-4-turbo": 93,
            "gpt-3.5-turbo": 80,
            "claude-3-opus": 96,
            "claude-3-sonnet": 88,
            "claude-3-haiku": 75,
            "gemini-pro": 85,
        }

    def register_model(self, model_name: str, **kwargs):
        """
        Register a model with the router

        Args:
            model_name: Name of the model
            **kwargs: Additional arguments for model initialization
        """
        model = AIModelFactory.create(model_name, **kwargs)
        self.models[model_name] = model
        self.metrics[model_name] = ModelMetrics()

    def _select_model_round_robin(self) -> str:
        """Select model using round-robin strategy"""
        model_names = list(self.models.keys())
        if not model_names:
            raise ValueError("No models registered")

        model_name = model_names[self.current_index % len(model_names)]
        self.current_index += 1
        return model_name

    def _select_model_least_latency(self) -> str:
        """Select model with least average latency"""
        if not self.models:
            raise ValueError("No models registered")

        # Find model with lowest average latency
        best_model = min(self.metrics.items(), key=lambda x: x[1].average_latency)
        return best_model[0]

    def _select_model_cost_optimized(self) -> str:
        """Select most cost-effective model"""
        if not self.models:
            raise ValueError("No models registered")

        # Find model with lowest cost and acceptable quality
        available_models = [
            (name, self.model_costs.get(name, 0.01))
            for name in self.models.keys()
            if self.model_quality.get(name, 0) >= 75  # Minimum quality threshold
        ]

        if not available_models:
            return list(self.models.keys())[0]

        best_model = min(available_models, key=lambda x: x[1])
        return best_model[0]

    def _select_model_quality_optimized(self) -> str:
        """Select highest quality model"""
        if not self.models:
            raise ValueError("No models registered")

        # Find model with highest quality score
        best_model = max(
            [(name, self.model_quality.get(name, 0)) for name in self.models.keys()],
            key=lambda x: x[1],
        )
        return best_model[0]

    def _select_model_failover(self) -> str:
        """Select model with failover logic"""
        if not self.models:
            raise ValueError("No models registered")

        # Sort models by success rate and quality
        sorted_models = sorted(
            self.models.keys(),
            key=lambda x: (self.metrics[x].success_rate, self.model_quality.get(x, 0)),
            reverse=True,
        )

        return sorted_models[0]

    def select_model(self) -> str:
        """
        Select a model based on the routing strategy

        Returns:
            Selected model name
        """
        if self.strategy == RoutingStrategy.ROUND_ROBIN:
            return self._select_model_round_robin()
        elif self.strategy == RoutingStrategy.LEAST_LATENCY:
            return self._select_model_least_latency()
        elif self.strategy == RoutingStrategy.COST_OPTIMIZED:
            return self._select_model_cost_optimized()
        elif self.strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            return self._select_model_quality_optimized()
        elif self.strategy == RoutingStrategy.FAILOVER:
            return self._select_model_failover()
        else:
            return self._select_model_quality_optimized()

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using selected model

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            model_name: Specific model to use (optional)
            **kwargs: Additional arguments

        Returns:
            Generation result with metadata
        """
        # Select model
        selected_model = model_name or self.select_model()
        model = self.models[selected_model]

        # Track timing
        start_time = datetime.utcnow()

        try:
            # Generate text
            result = await model.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            # Calculate metrics
            end_time = datetime.utcnow()
            latency = (end_time - start_time).total_seconds()
            tokens = len(result.split())  # Rough estimate
            cost = (tokens / 1000) * self.model_costs.get(selected_model, 0.01)

            # Record success
            self.metrics[selected_model].record_request(
                success=True, latency=latency, tokens=tokens, cost=cost
            )

            return {
                "text": result,
                "model": selected_model,
                "latency": latency,
                "tokens": tokens,
                "cost": cost,
                "success": True,
            }

        except Exception as e:
            # Record failure
            end_time = datetime.utcnow()
            latency = (end_time - start_time).total_seconds()
            self.metrics[selected_model].record_request(success=False, latency=latency)

            # Try failover if enabled
            if self.strategy == RoutingStrategy.FAILOVER and len(self.models) > 1:
                # Try next best model
                other_models = [m for m in self.models.keys() if m != selected_model]
                if other_models:
                    return await self.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        model_name=other_models[0],
                        **kwargs
                    )

            return {
                "text": "",
                "model": selected_model,
                "latency": latency,
                "tokens": 0,
                "cost": 0.0,
                "success": False,
                "error": str(e),
            }

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model_name: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate text with streaming using selected model

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            model_name: Specific model to use (optional)
            **kwargs: Additional arguments

        Yields:
            Generation chunks with metadata
        """
        # Select model
        selected_model = model_name or self.select_model()
        model = self.models[selected_model]

        # Track timing
        start_time = datetime.utcnow()
        total_tokens = 0

        try:
            async for chunk in model.generate_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            ):
                total_tokens += len(chunk.split())
                yield {"chunk": chunk, "model": selected_model, "success": True}

            # Record success
            end_time = datetime.utcnow()
            latency = (end_time - start_time).total_seconds()
            cost = (total_tokens / 1000) * self.model_costs.get(selected_model, 0.01)

            self.metrics[selected_model].record_request(
                success=True, latency=latency, tokens=total_tokens, cost=cost
            )

        except Exception as e:
            # Record failure
            end_time = datetime.utcnow()
            latency = (end_time - start_time).total_seconds()
            self.metrics[selected_model].record_request(success=False, latency=latency)

            yield {
                "chunk": "",
                "model": selected_model,
                "success": False,
                "error": str(e),
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get router metrics"""
        return {
            "strategy": self.strategy.value,
            "models": {
                name: {
                    "total_requests": metrics.total_requests,
                    "successful_requests": metrics.successful_requests,
                    "failed_requests": metrics.failed_requests,
                    "success_rate": metrics.success_rate,
                    "average_latency": metrics.average_latency,
                    "total_tokens": metrics.total_tokens,
                    "total_cost": metrics.total_cost,
                    "error_rate": metrics.error_rate,
                    "last_used": (
                        metrics.last_used.isoformat() if metrics.last_used else None
                    ),
                }
                for name, metrics in self.metrics.items()
            },
        }
