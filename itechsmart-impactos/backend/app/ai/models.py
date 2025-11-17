"""
AI Model Integrations (OpenAI, Anthropic, Google)
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
from abc import ABC, abstractmethod
import openai
import anthropic
import google.generativeai as genai
from app.core.config import settings


class AIModel(ABC):
    """Abstract base class for AI models"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """Generate text completion"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate text completion with streaming"""
        pass

    @abstractmethod
    async def generate_with_context(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """Generate text with conversation context"""
        pass


class OpenAIModel(AIModel):
    """OpenAI GPT-4 integration"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize OpenAI model

        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """Generate text completion"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        return response.choices[0].message.content

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate text completion with streaming"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_with_context(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """Generate text with conversation context"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        return response.choices[0].message.content


class AnthropicModel(AIModel):
    """Anthropic Claude integration"""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"
    ):
        """
        Initialize Anthropic model

        Args:
            api_key: Anthropic API key
            model: Model name (claude-3-opus, claude-3-sonnet, claude-3-haiku)
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """Generate text completion"""
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )

        return message.content[0].text

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate text completion with streaming"""
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def generate_with_context(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """Generate text with conversation context"""
        # Extract system message if present
        system_prompt = ""
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                anthropic_messages.append(
                    {"role": msg["role"], "content": msg["content"]}
                )

        message = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=anthropic_messages,
            **kwargs,
        )

        return message.content[0].text


class GoogleModel(AIModel):
    """Google Gemini integration"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """
        Initialize Google model

        Args:
            api_key: Google AI API key
            model: Model name (gemini-pro, gemini-pro-vision)
        """
        self.api_key = api_key or settings.GOOGLE_AI_API_KEY
        self.model_name = model
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """Generate text completion"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        generation_config = genai.types.GenerationConfig(
            temperature=temperature, max_output_tokens=max_tokens, **kwargs
        )

        response = await self.model.generate_content_async(
            full_prompt, generation_config=generation_config
        )

        return response.text

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate text completion with streaming"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        generation_config = genai.types.GenerationConfig(
            temperature=temperature, max_output_tokens=max_tokens, **kwargs
        )

        response = await self.model.generate_content_async(
            full_prompt, generation_config=generation_config, stream=True
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def generate_with_context(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """Generate text with conversation context"""
        # Convert messages to Gemini format
        chat = self.model.start_chat(history=[])

        # Add messages to chat history
        for msg in messages[:-1]:  # All except last message
            if msg["role"] == "user":
                chat.history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                chat.history.append({"role": "model", "parts": [msg["content"]]})

        # Send last message
        last_message = messages[-1]["content"]

        generation_config = genai.types.GenerationConfig(
            temperature=temperature, max_output_tokens=max_tokens, **kwargs
        )

        response = await chat.send_message_async(
            last_message, generation_config=generation_config
        )

        return response.text


class AIModelFactory:
    """Factory for creating AI model instances"""

    _models = {
        "gpt-4": OpenAIModel,
        "gpt-4-turbo": OpenAIModel,
        "gpt-3.5-turbo": OpenAIModel,
        "claude-3-opus": AnthropicModel,
        "claude-3-sonnet": AnthropicModel,
        "claude-3-haiku": AnthropicModel,
        "gemini-pro": GoogleModel,
        "gemini-pro-vision": GoogleModel,
    }

    @classmethod
    def create(cls, model_name: str, **kwargs) -> AIModel:
        """
        Create an AI model instance

        Args:
            model_name: Name of the model
            **kwargs: Additional arguments for model initialization

        Returns:
            AI model instance

        Raises:
            ValueError: If model name is not supported
        """
        if model_name not in cls._models:
            raise ValueError(f"Unsupported model: {model_name}")

        model_class = cls._models[model_name]
        return model_class(model=model_name, **kwargs)

    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available models"""
        return list(cls._models.keys())
