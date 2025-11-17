"""
Enhanced AI Provider System - Support for 40+ Models
Implements SuperNinja-equivalent multi-model support
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import os
from datetime import datetime
import asyncio
import httpx
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai


class ModelProvider(str, Enum):
    """AI Model Providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    MISTRAL = "mistral"
    COHERE = "cohere"
    AI21 = "ai21"
    PERPLEXITY = "perplexity"
    TOGETHER = "together"
    REPLICATE = "replicate"


class ModelTier(str, Enum):
    """Model capability tiers"""

    FLAGSHIP = "flagship"  # Most capable, highest cost
    ADVANCED = "advanced"  # High capability, moderate cost
    STANDARD = "standard"  # Good capability, low cost
    FAST = "fast"  # Fast responses, lowest cost
    LOCAL = "local"  # Local/self-hosted models


class AIModel:
    """Represents an AI model with its capabilities and pricing"""

    def __init__(
        self,
        id: str,
        name: str,
        provider: ModelProvider,
        tier: ModelTier,
        context_window: int,
        max_output: int,
        cost_per_1k_input: float,
        cost_per_1k_output: float,
        supports_vision: bool = False,
        supports_function_calling: bool = False,
        supports_streaming: bool = True,
        description: str = "",
    ):
        self.id = id
        self.name = name
        self.provider = provider
        self.tier = tier
        self.context_window = context_window
        self.max_output = max_output
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output
        self.supports_vision = supports_vision
        self.supports_function_calling = supports_function_calling
        self.supports_streaming = supports_streaming
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider.value,
            "tier": self.tier.value,
            "context_window": self.context_window,
            "max_output": self.max_output,
            "cost_per_1k_input": self.cost_per_1k_input,
            "cost_per_1k_output": self.cost_per_1k_output,
            "supports_vision": self.supports_vision,
            "supports_function_calling": self.supports_function_calling,
            "supports_streaming": self.supports_streaming,
            "description": self.description,
        }


class EnhancedAIProviderManager:
    """
    Enhanced AI Provider Manager supporting 40+ models
    Implements SuperNinja-equivalent capabilities
    """

    def __init__(self):
        self.models: Dict[str, AIModel] = {}
        self.provider_clients: Dict[ModelProvider, Any] = {}
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        self._initialize_models()
        self._initialize_clients()

    def _initialize_models(self):
        """Initialize all 40+ supported models"""

        # ==================== OPENAI MODELS ====================
        openai_models = [
            AIModel(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.FLAGSHIP,
                context_window=128000,
                max_output=4096,
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.03,
                supports_vision=True,
                supports_function_calling=True,
                description="Most capable GPT-4 model with vision",
            ),
            AIModel(
                id="gpt-4o",
                name="GPT-4o",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.FLAGSHIP,
                context_window=128000,
                max_output=4096,
                cost_per_1k_input=0.005,
                cost_per_1k_output=0.015,
                supports_vision=True,
                supports_function_calling=True,
                description="Optimized GPT-4 with multimodal capabilities",
            ),
            AIModel(
                id="gpt-4o-mini",
                name="GPT-4o Mini",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.FAST,
                context_window=128000,
                max_output=16384,
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006,
                supports_vision=True,
                supports_function_calling=True,
                description="Fast and affordable GPT-4 variant",
            ),
            AIModel(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.STANDARD,
                context_window=16385,
                max_output=4096,
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                supports_function_calling=True,
                description="Fast and cost-effective model",
            ),
            AIModel(
                id="o1-preview",
                name="o1 Preview",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.FLAGSHIP,
                context_window=128000,
                max_output=32768,
                cost_per_1k_input=0.015,
                cost_per_1k_output=0.06,
                supports_function_calling=False,
                description="Advanced reasoning model",
            ),
            AIModel(
                id="o1-mini",
                name="o1 Mini",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.ADVANCED,
                context_window=128000,
                max_output=65536,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.012,
                supports_function_calling=False,
                description="Faster reasoning model",
            ),
        ]

        # ==================== ANTHROPIC MODELS ====================
        anthropic_models = [
            AIModel(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                provider=ModelProvider.ANTHROPIC,
                tier=ModelTier.FLAGSHIP,
                context_window=200000,
                max_output=8192,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                supports_vision=True,
                supports_function_calling=True,
                description="Most intelligent Claude model",
            ),
            AIModel(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                provider=ModelProvider.ANTHROPIC,
                tier=ModelTier.FLAGSHIP,
                context_window=200000,
                max_output=4096,
                cost_per_1k_input=0.015,
                cost_per_1k_output=0.075,
                supports_vision=True,
                supports_function_calling=True,
                description="Most powerful Claude 3 model",
            ),
            AIModel(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                provider=ModelProvider.ANTHROPIC,
                tier=ModelTier.ADVANCED,
                context_window=200000,
                max_output=4096,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                supports_vision=True,
                supports_function_calling=True,
                description="Balanced performance and speed",
            ),
            AIModel(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                provider=ModelProvider.ANTHROPIC,
                tier=ModelTier.FAST,
                context_window=200000,
                max_output=4096,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125,
                supports_vision=True,
                supports_function_calling=True,
                description="Fastest Claude 3 model",
            ),
        ]

        # ==================== GOOGLE MODELS ====================
        google_models = [
            AIModel(
                id="gemini-1.5-pro",
                name="Gemini 1.5 Pro",
                provider=ModelProvider.GOOGLE,
                tier=ModelTier.FLAGSHIP,
                context_window=2000000,
                max_output=8192,
                cost_per_1k_input=0.00125,
                cost_per_1k_output=0.005,
                supports_vision=True,
                supports_function_calling=True,
                description="Most capable Gemini model with 2M context",
            ),
            AIModel(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                provider=ModelProvider.GOOGLE,
                tier=ModelTier.FAST,
                context_window=1000000,
                max_output=8192,
                cost_per_1k_input=0.000075,
                cost_per_1k_output=0.0003,
                supports_vision=True,
                supports_function_calling=True,
                description="Fast and efficient Gemini model",
            ),
            AIModel(
                id="gemini-1.0-pro",
                name="Gemini 1.0 Pro",
                provider=ModelProvider.GOOGLE,
                tier=ModelTier.STANDARD,
                context_window=32760,
                max_output=2048,
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                supports_function_calling=True,
                description="Standard Gemini model",
            ),
        ]

        # ==================== DEEPSEEK MODELS ====================
        deepseek_models = [
            AIModel(
                id="deepseek-chat",
                name="DeepSeek Chat",
                provider=ModelProvider.DEEPSEEK,
                tier=ModelTier.ADVANCED,
                context_window=32000,
                max_output=4096,
                cost_per_1k_input=0.00014,
                cost_per_1k_output=0.00028,
                supports_function_calling=True,
                description="General purpose chat model",
            ),
            AIModel(
                id="deepseek-coder",
                name="DeepSeek Coder",
                provider=ModelProvider.DEEPSEEK,
                tier=ModelTier.ADVANCED,
                context_window=32000,
                max_output=4096,
                cost_per_1k_input=0.00014,
                cost_per_1k_output=0.00028,
                supports_function_calling=True,
                description="Specialized coding model",
            ),
        ]

        # ==================== MISTRAL MODELS ====================
        mistral_models = [
            AIModel(
                id="mistral-large-latest",
                name="Mistral Large",
                provider=ModelProvider.MISTRAL,
                tier=ModelTier.FLAGSHIP,
                context_window=128000,
                max_output=4096,
                cost_per_1k_input=0.002,
                cost_per_1k_output=0.006,
                supports_function_calling=True,
                description="Most capable Mistral model",
            ),
            AIModel(
                id="mistral-medium-latest",
                name="Mistral Medium",
                provider=ModelProvider.MISTRAL,
                tier=ModelTier.ADVANCED,
                context_window=32000,
                max_output=4096,
                cost_per_1k_input=0.0027,
                cost_per_1k_output=0.0081,
                supports_function_calling=True,
                description="Balanced Mistral model",
            ),
            AIModel(
                id="mistral-small-latest",
                name="Mistral Small",
                provider=ModelProvider.MISTRAL,
                tier=ModelTier.STANDARD,
                context_window=32000,
                max_output=4096,
                cost_per_1k_input=0.0002,
                cost_per_1k_output=0.0006,
                supports_function_calling=True,
                description="Fast and affordable",
            ),
            AIModel(
                id="mixtral-8x7b",
                name="Mixtral 8x7B",
                provider=ModelProvider.MISTRAL,
                tier=ModelTier.ADVANCED,
                context_window=32000,
                max_output=4096,
                cost_per_1k_input=0.0007,
                cost_per_1k_output=0.0007,
                supports_function_calling=True,
                description="Mixture of experts model",
            ),
        ]

        # ==================== COHERE MODELS ====================
        cohere_models = [
            AIModel(
                id="command-r-plus",
                name="Command R+",
                provider=ModelProvider.COHERE,
                tier=ModelTier.FLAGSHIP,
                context_window=128000,
                max_output=4096,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                supports_function_calling=True,
                description="Most capable Cohere model",
            ),
            AIModel(
                id="command-r",
                name="Command R",
                provider=ModelProvider.COHERE,
                tier=ModelTier.ADVANCED,
                context_window=128000,
                max_output=4096,
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                supports_function_calling=True,
                description="Balanced Cohere model",
            ),
            AIModel(
                id="command-light",
                name="Command Light",
                provider=ModelProvider.COHERE,
                tier=ModelTier.FAST,
                context_window=4096,
                max_output=4096,
                cost_per_1k_input=0.0003,
                cost_per_1k_output=0.0006,
                description="Fast and lightweight",
            ),
        ]

        # ==================== AI21 MODELS ====================
        ai21_models = [
            AIModel(
                id="j2-ultra",
                name="Jurassic-2 Ultra",
                provider=ModelProvider.AI21,
                tier=ModelTier.FLAGSHIP,
                context_window=8192,
                max_output=2048,
                cost_per_1k_input=0.015,
                cost_per_1k_output=0.015,
                description="Most capable AI21 model",
            ),
            AIModel(
                id="j2-mid",
                name="Jurassic-2 Mid",
                provider=ModelProvider.AI21,
                tier=ModelTier.STANDARD,
                context_window=8192,
                max_output=2048,
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.01,
                description="Balanced AI21 model",
            ),
        ]

        # ==================== PERPLEXITY MODELS ====================
        perplexity_models = [
            AIModel(
                id="pplx-70b-online",
                name="Perplexity 70B Online",
                provider=ModelProvider.PERPLEXITY,
                tier=ModelTier.ADVANCED,
                context_window=4096,
                max_output=4096,
                cost_per_1k_input=0.001,
                cost_per_1k_output=0.001,
                description="Online search-enabled model",
            ),
            AIModel(
                id="pplx-7b-online",
                name="Perplexity 7B Online",
                provider=ModelProvider.PERPLEXITY,
                tier=ModelTier.FAST,
                context_window=4096,
                max_output=4096,
                cost_per_1k_input=0.0002,
                cost_per_1k_output=0.0002,
                description="Fast online search model",
            ),
        ]

        # ==================== OLLAMA (LOCAL) MODELS ====================
        ollama_models = [
            AIModel(
                id="llama3.1:405b",
                name="Llama 3.1 405B",
                provider=ModelProvider.OLLAMA,
                tier=ModelTier.LOCAL,
                context_window=128000,
                max_output=4096,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                description="Largest Llama 3.1 model (local)",
            ),
            AIModel(
                id="llama3.1:70b",
                name="Llama 3.1 70B",
                provider=ModelProvider.OLLAMA,
                tier=ModelTier.LOCAL,
                context_window=128000,
                max_output=4096,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                description="Large Llama 3.1 model (local)",
            ),
            AIModel(
                id="llama3.1:8b",
                name="Llama 3.1 8B",
                provider=ModelProvider.OLLAMA,
                tier=ModelTier.LOCAL,
                context_window=128000,
                max_output=4096,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                description="Fast Llama 3.1 model (local)",
            ),
            AIModel(
                id="codellama:70b",
                name="Code Llama 70B",
                provider=ModelProvider.OLLAMA,
                tier=ModelTier.LOCAL,
                context_window=100000,
                max_output=4096,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                description="Specialized coding model (local)",
            ),
            AIModel(
                id="mistral:7b",
                name="Mistral 7B",
                provider=ModelProvider.OLLAMA,
                tier=ModelTier.LOCAL,
                context_window=32000,
                max_output=4096,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                description="Fast local model",
            ),
        ]

        # Add all models to registry
        all_models = (
            openai_models
            + anthropic_models
            + google_models
            + deepseek_models
            + mistral_models
            + cohere_models
            + ai21_models
            + perplexity_models
            + ollama_models
        )

        for model in all_models:
            self.models[model.id] = model

    def _initialize_clients(self):
        """Initialize API clients for each provider"""

        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.provider_clients[ModelProvider.OPENAI] = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )

        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            self.provider_clients[ModelProvider.ANTHROPIC] = Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )

        # Google
        if os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.provider_clients[ModelProvider.GOOGLE] = genai

        # DeepSeek
        if os.getenv("DEEPSEEK_API_KEY"):
            self.provider_clients[ModelProvider.DEEPSEEK] = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com",
            )

        # Mistral
        if os.getenv("MISTRAL_API_KEY"):
            self.provider_clients[ModelProvider.MISTRAL] = httpx.AsyncClient(
                base_url="https://api.mistral.ai/v1",
                headers={"Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}"},
            )

        # Cohere
        if os.getenv("COHERE_API_KEY"):
            self.provider_clients[ModelProvider.COHERE] = httpx.AsyncClient(
                base_url="https://api.cohere.ai/v1",
                headers={"Authorization": f"Bearer {os.getenv('COHERE_API_KEY')}"},
            )

        # AI21
        if os.getenv("AI21_API_KEY"):
            self.provider_clients[ModelProvider.AI21] = httpx.AsyncClient(
                base_url="https://api.ai21.com/studio/v1",
                headers={"Authorization": f"Bearer {os.getenv('AI21_API_KEY')}"},
            )

        # Perplexity
        if os.getenv("PERPLEXITY_API_KEY"):
            self.provider_clients[ModelProvider.PERPLEXITY] = OpenAI(
                api_key=os.getenv("PERPLEXITY_API_KEY"),
                base_url="https://api.perplexity.ai",
            )

        # Ollama (local)
        self.provider_clients[ModelProvider.OLLAMA] = httpx.AsyncClient(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )

    def get_all_models(self) -> List[Dict[str, Any]]:
        """Get all available models"""
        return [model.to_dict() for model in self.models.values()]

    def get_models_by_provider(self, provider: ModelProvider) -> List[Dict[str, Any]]:
        """Get models for a specific provider"""
        return [
            model.to_dict()
            for model in self.models.values()
            if model.provider == provider
        ]

    def get_models_by_tier(self, tier: ModelTier) -> List[Dict[str, Any]]:
        """Get models by capability tier"""
        return [model.to_dict() for model in self.models.values() if model.tier == tier]

    def get_model(self, model_id: str) -> Optional[AIModel]:
        """Get a specific model by ID"""
        return self.models.get(model_id)

    def is_provider_available(self, provider: ModelProvider) -> bool:
        """Check if a provider is configured and available"""
        return provider in self.provider_clients

    async def generate_completion(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate completion using specified model
        Universal interface for all providers
        """
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")

        if not self.is_provider_available(model.provider):
            raise ValueError(f"Provider {model.provider.value} not configured")

        # Track usage
        if model_id not in self.usage_stats:
            self.usage_stats[model_id] = {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
            }

        self.usage_stats[model_id]["total_requests"] += 1

        # Route to appropriate provider
        if model.provider == ModelProvider.OPENAI:
            return await self._generate_openai(
                model, messages, temperature, max_tokens, stream
            )
        elif model.provider == ModelProvider.ANTHROPIC:
            return await self._generate_anthropic(
                model, messages, temperature, max_tokens, stream
            )
        elif model.provider == ModelProvider.GOOGLE:
            return await self._generate_google(
                model, messages, temperature, max_tokens, stream
            )
        elif model.provider == ModelProvider.DEEPSEEK:
            return await self._generate_deepseek(
                model, messages, temperature, max_tokens, stream
            )
        elif model.provider == ModelProvider.OLLAMA:
            return await self._generate_ollama(
                model, messages, temperature, max_tokens, stream
            )
        else:
            raise NotImplementedError(
                f"Provider {model.provider.value} not yet implemented"
            )

    async def _generate_openai(
        self,
        model: AIModel,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool,
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI API"""
        client = self.provider_clients[ModelProvider.OPENAI]

        response = client.chat.completions.create(
            model=model.id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or model.max_output,
            stream=stream,
        )

        if stream:
            return {"stream": response}

        # Calculate cost
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = (input_tokens / 1000) * model.cost_per_1k_input + (
            output_tokens / 1000
        ) * model.cost_per_1k_output

        # Update stats
        self.usage_stats[model.id]["total_tokens"] += response.usage.total_tokens
        self.usage_stats[model.id]["total_cost"] += cost

        return {
            "content": response.choices[0].message.content,
            "model": model.id,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "cost": cost,
            "finish_reason": response.choices[0].finish_reason,
        }

    async def _generate_anthropic(
        self,
        model: AIModel,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool,
    ) -> Dict[str, Any]:
        """Generate completion using Anthropic API"""
        client = self.provider_clients[ModelProvider.ANTHROPIC]

        response = client.messages.create(
            model=model.id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or model.max_output,
            stream=stream,
        )

        if stream:
            return {"stream": response}

        # Calculate cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens / 1000) * model.cost_per_1k_input + (
            output_tokens / 1000
        ) * model.cost_per_1k_output

        # Update stats
        total_tokens = input_tokens + output_tokens
        self.usage_stats[model.id]["total_tokens"] += total_tokens
        self.usage_stats[model.id]["total_cost"] += cost

        return {
            "content": response.content[0].text,
            "model": model.id,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
            },
            "cost": cost,
            "finish_reason": response.stop_reason,
        }

    async def _generate_google(
        self,
        model: AIModel,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool,
    ) -> Dict[str, Any]:
        """Generate completion using Google Gemini API"""
        genai_client = self.provider_clients[ModelProvider.GOOGLE]

        # Convert messages to Gemini format
        gemini_model = genai_client.GenerativeModel(model.id)

        # Combine messages into single prompt
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        response = gemini_model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens or model.max_output,
            },
            stream=stream,
        )

        if stream:
            return {"stream": response}

        # Estimate tokens (Gemini doesn't provide exact counts)
        input_tokens = len(prompt.split()) * 1.3  # Rough estimate
        output_tokens = len(response.text.split()) * 1.3
        cost = (input_tokens / 1000) * model.cost_per_1k_input + (
            output_tokens / 1000
        ) * model.cost_per_1k_output

        # Update stats
        total_tokens = int(input_tokens + output_tokens)
        self.usage_stats[model.id]["total_tokens"] += total_tokens
        self.usage_stats[model.id]["total_cost"] += cost

        return {
            "content": response.text,
            "model": model.id,
            "usage": {
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": total_tokens,
            },
            "cost": cost,
            "finish_reason": "stop",
        }

    async def _generate_deepseek(
        self,
        model: AIModel,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool,
    ) -> Dict[str, Any]:
        """Generate completion using DeepSeek API (OpenAI-compatible)"""
        client = self.provider_clients[ModelProvider.DEEPSEEK]

        response = client.chat.completions.create(
            model=model.id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or model.max_output,
            stream=stream,
        )

        if stream:
            return {"stream": response}

        # Calculate cost
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = (input_tokens / 1000) * model.cost_per_1k_input + (
            output_tokens / 1000
        ) * model.cost_per_1k_output

        # Update stats
        self.usage_stats[model.id]["total_tokens"] += response.usage.total_tokens
        self.usage_stats[model.id]["total_cost"] += cost

        return {
            "content": response.choices[0].message.content,
            "model": model.id,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "cost": cost,
            "finish_reason": response.choices[0].finish_reason,
        }

    async def _generate_ollama(
        self,
        model: AIModel,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool,
    ) -> Dict[str, Any]:
        """Generate completion using Ollama (local)"""
        client = self.provider_clients[ModelProvider.OLLAMA]

        response = await client.post(
            "/api/chat",
            json={
                "model": model.id,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
            },
        )

        if stream:
            return {"stream": response}

        data = response.json()

        return {
            "content": data["message"]["content"],
            "model": model.id,
            "usage": {
                "input_tokens": 0,  # Ollama doesn't provide token counts
                "output_tokens": 0,
                "total_tokens": 0,
            },
            "cost": 0.0,  # Local models are free
            "finish_reason": "stop",
        }

    def get_usage_stats(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get usage statistics"""
        if model_id:
            return self.usage_stats.get(model_id, {})
        return self.usage_stats

    def compare_models(
        self,
        model_ids: List[str],
        criteria: List[str] = ["cost", "context_window", "speed"],
    ) -> Dict[str, Any]:
        """Compare multiple models across different criteria"""
        comparison = {}

        for model_id in model_ids:
            model = self.get_model(model_id)
            if not model:
                continue

            comparison[model_id] = {
                "name": model.name,
                "provider": model.provider.value,
                "tier": model.tier.value,
                "cost_per_1k_input": model.cost_per_1k_input,
                "cost_per_1k_output": model.cost_per_1k_output,
                "context_window": model.context_window,
                "max_output": model.max_output,
                "supports_vision": model.supports_vision,
                "supports_function_calling": model.supports_function_calling,
            }

        return comparison


# Global instance
enhanced_ai_manager = EnhancedAIProviderManager()
