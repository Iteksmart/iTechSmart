"""
Multi-AI Provider Integration - OpenAI, Anthropic, Google, DeepSeek, Ollama
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Base class for AI providers"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.name = "base"
        self.available_models: List[str] = []

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate completion"""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Chat completion"""
        pass

    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.api_key is not None


class OpenAIProvider(AIProvider):
    """OpenAI provider (GPT-4, GPT-3.5, etc.)"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.name = "openai"
        self.available_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
        ]

        if api_key:
            try:
                import openai

                self.client = openai.AsyncOpenAI(api_key=api_key)
            except ImportError:
                logger.error("OpenAI package not installed")
                self.client = None
        else:
            self.client = None

    async def generate(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate completion"""
        try:
            if not self.client:
                return {"success": False, "error": "OpenAI client not initialized"}

            response = await self.client.completions.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return {
                "success": True,
                "content": response.choices[0].text,
                "model": model,
                "provider": self.name,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            return {"success": False, "error": str(e), "provider": self.name}

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Chat completion"""
        try:
            if not self.client:
                return {"success": False, "error": "OpenAI client not initialized"}

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model,
                "provider": self.name,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

        except Exception as e:
            logger.error(f"OpenAI chat failed: {str(e)}")
            return {"success": False, "error": str(e), "provider": self.name}


class AnthropicProvider(AIProvider):
    """Anthropic provider (Claude)"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.name = "anthropic"
        self.available_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
        ]

        if api_key:
            try:
                import anthropic

                self.client = anthropic.AsyncAnthropic(api_key=api_key)
            except ImportError:
                logger.error("Anthropic package not installed")
                self.client = None
        else:
            self.client = None

    async def generate(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate completion"""
        # Claude uses chat format, convert prompt to message
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, model, temperature, max_tokens, **kwargs)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Chat completion"""
        try:
            if not self.client:
                return {"success": False, "error": "Anthropic client not initialized"}

            response = await self.client.messages.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return {
                "success": True,
                "content": response.content[0].text,
                "model": model,
                "provider": self.name,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            }

        except Exception as e:
            logger.error(f"Anthropic chat failed: {str(e)}")
            return {"success": False, "error": str(e), "provider": self.name}


class GoogleProvider(AIProvider):
    """Google provider (Gemini)"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.name = "google"
        self.available_models = ["gemini-pro", "gemini-pro-vision", "gemini-ultra"]

        if api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                self.genai = genai
            except ImportError:
                logger.error("Google GenerativeAI package not installed")
                self.genai = None
        else:
            self.genai = None

    async def generate(
        self,
        prompt: str,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate completion"""
        try:
            if not self.genai:
                return {"success": False, "error": "Google client not initialized"}

            model_instance = self.genai.GenerativeModel(model)

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            response = await asyncio.to_thread(
                model_instance.generate_content,
                prompt,
                generation_config=generation_config,
            )

            return {
                "success": True,
                "content": response.text,
                "model": model,
                "provider": self.name,
            }

        except Exception as e:
            logger.error(f"Google generation failed: {str(e)}")
            return {"success": False, "error": str(e), "provider": self.name}

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Chat completion"""
        try:
            if not self.genai:
                return {"success": False, "error": "Google client not initialized"}

            model_instance = self.genai.GenerativeModel(model)
            chat = model_instance.start_chat(history=[])

            # Convert messages to Gemini format
            for msg in messages[:-1]:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])

            # Send last message and get response
            last_message = messages[-1]["content"]
            response = await asyncio.to_thread(chat.send_message, last_message)

            return {
                "success": True,
                "content": response.text,
                "model": model,
                "provider": self.name,
            }

        except Exception as e:
            logger.error(f"Google chat failed: {str(e)}")
            return {"success": False, "error": str(e), "provider": self.name}


class DeepSeekProvider(AIProvider):
    """DeepSeek provider"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.name = "deepseek"
        self.available_models = ["deepseek-chat", "deepseek-coder"]
        self.base_url = "https://api.deepseek.com/v1"

        if api_key:
            try:
                import openai

                self.client = openai.AsyncOpenAI(
                    api_key=api_key, base_url=self.base_url
                )
            except ImportError:
                logger.error("OpenAI package not installed (required for DeepSeek)")
                self.client = None
        else:
            self.client = None

    async def generate(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate completion"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, model, temperature, max_tokens, **kwargs)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Chat completion"""
        try:
            if not self.client:
                return {"success": False, "error": "DeepSeek client not initialized"}

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model,
                "provider": self.name,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

        except Exception as e:
            logger.error(f"DeepSeek chat failed: {str(e)}")
            return {"success": False, "error": str(e), "provider": self.name}


class OllamaProvider(AIProvider):
    """Ollama provider (local models)"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(None)  # No API key needed for local
        self.name = "ollama"
        self.base_url = base_url
        self.available_models = []  # Will be populated dynamically

        try:
            import ollama

            self.client = ollama.AsyncClient(host=base_url)
            # Try to get available models
            asyncio.create_task(self._load_models())
        except ImportError:
            logger.error("Ollama package not installed")
            self.client = None

    async def _load_models(self):
        """Load available models from Ollama"""
        try:
            if self.client:
                models = await self.client.list()
                self.available_models = [m["name"] for m in models.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to load Ollama models: {str(e)}")

    def is_available(self) -> bool:
        """Ollama is available if client is initialized"""
        return self.client is not None

    async def generate(
        self,
        prompt: str,
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate completion"""
        try:
            if not self.client:
                return {"success": False, "error": "Ollama client not initialized"}

            response = await self.client.generate(
                model=model,
                prompt=prompt,
                options={"temperature": temperature, "num_predict": max_tokens},
            )

            return {
                "success": True,
                "content": response["response"],
                "model": model,
                "provider": self.name,
            }

        except Exception as e:
            logger.error(f"Ollama generation failed: {str(e)}")
            return {"success": False, "error": str(e), "provider": self.name}

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Chat completion"""
        try:
            if not self.client:
                return {"success": False, "error": "Ollama client not initialized"}

            response = await self.client.chat(
                model=model,
                messages=messages,
                options={"temperature": temperature, "num_predict": max_tokens},
            )

            return {
                "success": True,
                "content": response["message"]["content"],
                "model": model,
                "provider": self.name,
            }

        except Exception as e:
            logger.error(f"Ollama chat failed: {str(e)}")
            return {"success": False, "error": str(e), "provider": self.name}


class AIProviderManager:
    """Manages multiple AI providers with fallback"""

    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self.default_provider = "openai"
        self.fallback_order = ["openai", "anthropic", "google", "deepseek", "ollama"]

    def register_provider(self, provider: AIProvider):
        """Register an AI provider"""
        self.providers[provider.name] = provider
        logger.info(f"Registered AI provider: {provider.name}")

    def set_default_provider(self, provider_name: str):
        """Set default provider"""
        if provider_name in self.providers:
            self.default_provider = provider_name
            logger.info(f"Set default provider to: {provider_name}")

    def get_provider(self, provider_name: Optional[str] = None) -> Optional[AIProvider]:
        """Get a specific provider or default"""
        if provider_name:
            return self.providers.get(provider_name)
        return self.providers.get(self.default_provider)

    async def generate(
        self,
        prompt: str,
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        use_fallback: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate with automatic fallback"""
        providers_to_try = [provider_name] if provider_name else self.fallback_order

        for prov_name in providers_to_try:
            provider = self.providers.get(prov_name)

            if not provider or not provider.is_available():
                continue

            # Use default model if not specified
            if not model and provider.available_models:
                model = provider.available_models[0]

            result = await provider.generate(
                prompt, model, temperature, max_tokens, **kwargs
            )

            if result.get("success"):
                return result

            logger.warning(f"Provider {prov_name} failed, trying next...")

            if not use_fallback:
                return result

        return {"success": False, "error": "All providers failed or unavailable"}

    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        use_fallback: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """Chat with automatic fallback"""
        providers_to_try = [provider_name] if provider_name else self.fallback_order

        for prov_name in providers_to_try:
            provider = self.providers.get(prov_name)

            if not provider or not provider.is_available():
                continue

            # Use default model if not specified
            if not model and provider.available_models:
                model = provider.available_models[0]

            result = await provider.chat(
                messages, model, temperature, max_tokens, **kwargs
            )

            if result.get("success"):
                return result

            logger.warning(f"Provider {prov_name} failed, trying next...")

            if not use_fallback:
                return result

        return {"success": False, "error": "All providers failed or unavailable"}

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [
            name for name, provider in self.providers.items() if provider.is_available()
        ]

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about all providers"""
        return {
            name: {
                "available": provider.is_available(),
                "models": provider.available_models,
            }
            for name, provider in self.providers.items()
        }


# Global AI provider manager
ai_provider_manager = AIProviderManager()


def initialize_providers(
    openai_key: Optional[str] = None,
    anthropic_key: Optional[str] = None,
    google_key: Optional[str] = None,
    deepseek_key: Optional[str] = None,
    ollama_url: str = "http://localhost:11434",
):
    """Initialize all AI providers"""
    if openai_key:
        ai_provider_manager.register_provider(OpenAIProvider(openai_key))

    if anthropic_key:
        ai_provider_manager.register_provider(AnthropicProvider(anthropic_key))

    if google_key:
        ai_provider_manager.register_provider(GoogleProvider(google_key))

    if deepseek_key:
        ai_provider_manager.register_provider(DeepSeekProvider(deepseek_key))

    # Always try to register Ollama (local)
    ai_provider_manager.register_provider(OllamaProvider(ollama_url))

    logger.info(
        f"Initialized {len(ai_provider_manager.get_available_providers())} AI providers"
    )
