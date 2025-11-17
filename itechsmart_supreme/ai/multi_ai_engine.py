"""
Multi-AI Engine - Support for Multiple AI Providers
Supports OpenAI, Google Gemini, Anthropic Claude, Azure OpenAI, and Ollama
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import json
from enum import Enum

from ..core.models import Alert, Diagnosis


class AIProvider(Enum):
    """Supported AI providers"""

    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    OFFLINE = "offline"


class MultiAIEngine:
    """
    Unified AI engine supporting multiple providers with automatic fallback
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.providers = {}
        self.primary_provider = AIProvider(config.get("primary_provider", "offline"))
        self.fallback_chain = self._build_fallback_chain()

        # Initialize providers
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all configured AI providers"""

        # OpenAI
        if self.config.get("openai_api_key"):
            try:
                import openai

                openai.api_key = self.config["openai_api_key"]
                self.providers[AIProvider.OPENAI] = {
                    "client": openai,
                    "model": self.config.get("openai_model", "gpt-4-turbo-preview"),
                    "available": True,
                }
                self.logger.info("OpenAI provider initialized")
            except Exception as e:
                self.logger.warning(f"OpenAI initialization failed: {e}")

        # Google Gemini
        if self.config.get("gemini_api_key"):
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.config["gemini_api_key"])
                self.providers[AIProvider.GEMINI] = {
                    "client": genai,
                    "model": self.config.get("gemini_model", "gemini-pro"),
                    "available": True,
                }
                self.logger.info("Google Gemini provider initialized")
            except Exception as e:
                self.logger.warning(f"Gemini initialization failed: {e}")

        # Anthropic Claude
        if self.config.get("claude_api_key"):
            try:
                import anthropic

                self.providers[AIProvider.CLAUDE] = {
                    "client": anthropic.Anthropic(
                        api_key=self.config["claude_api_key"]
                    ),
                    "model": self.config.get("claude_model", "claude-3-opus-20240229"),
                    "available": True,
                }
                self.logger.info("Anthropic Claude provider initialized")
            except Exception as e:
                self.logger.warning(f"Claude initialization failed: {e}")

        # Azure OpenAI
        if self.config.get("azure_openai_key"):
            try:
                import openai

                openai.api_type = "azure"
                openai.api_key = self.config["azure_openai_key"]
                openai.api_base = self.config.get("azure_openai_endpoint")
                openai.api_version = self.config.get(
                    "azure_openai_version", "2024-02-15-preview"
                )
                self.providers[AIProvider.AZURE_OPENAI] = {
                    "client": openai,
                    "model": self.config.get("azure_openai_deployment"),
                    "available": True,
                }
                self.logger.info("Azure OpenAI provider initialized")
            except Exception as e:
                self.logger.warning(f"Azure OpenAI initialization failed: {e}")

        # Ollama (local)
        if self.config.get("ollama_url"):
            from ..integrations.ollama_integration import OllamaIntegration

            try:
                ollama = OllamaIntegration(
                    base_url=self.config["ollama_url"],
                    model=self.config.get("ollama_model", "llama2"),
                )
                self.providers[AIProvider.OLLAMA] = {
                    "client": ollama,
                    "model": self.config.get("ollama_model", "llama2"),
                    "available": True,
                }
                self.logger.info("Ollama provider initialized")
            except Exception as e:
                self.logger.warning(f"Ollama initialization failed: {e}")

        # Offline (always available)
        from .diagnosis_engine import AIDiagnosisEngine

        self.providers[AIProvider.OFFLINE] = {
            "client": AIDiagnosisEngine(offline_mode=True),
            "model": "rule-based",
            "available": True,
        }
        self.logger.info("Offline provider initialized")

    def _build_fallback_chain(self) -> List[AIProvider]:
        """Build fallback chain based on configuration"""

        # Default fallback order
        default_chain = [
            AIProvider.OPENAI,
            AIProvider.GEMINI,
            AIProvider.CLAUDE,
            AIProvider.AZURE_OPENAI,
            AIProvider.OLLAMA,
            AIProvider.OFFLINE,
        ]

        # Custom chain from config
        custom_chain = self.config.get("fallback_chain", [])
        if custom_chain:
            chain = [AIProvider(p) for p in custom_chain]
            # Ensure offline is always last
            if AIProvider.OFFLINE not in chain:
                chain.append(AIProvider.OFFLINE)
            return chain

        return default_chain

    async def diagnose_issue(
        self,
        alert: Alert,
        context: Dict[str, Any],
        preferred_provider: Optional[AIProvider] = None,
    ) -> Diagnosis:
        """
        Diagnose issue using AI with automatic fallback
        """

        # Determine provider order
        if preferred_provider and preferred_provider in self.providers:
            providers_to_try = [preferred_provider] + [
                p for p in self.fallback_chain if p != preferred_provider
            ]
        else:
            providers_to_try = [self.primary_provider] + [
                p for p in self.fallback_chain if p != self.primary_provider
            ]

        # Try each provider in order
        for provider in providers_to_try:
            if provider not in self.providers:
                continue

            if not self.providers[provider]["available"]:
                continue

            try:
                self.logger.info(f"Attempting diagnosis with {provider.value}")
                diagnosis = await self._diagnose_with_provider(provider, alert, context)

                if diagnosis:
                    self.logger.info(f"Diagnosis successful with {provider.value}")
                    return diagnosis

            except Exception as e:
                self.logger.warning(f"Diagnosis failed with {provider.value}: {e}")
                continue

        # Should never reach here due to offline fallback
        raise Exception("All AI providers failed")

    async def _diagnose_with_provider(
        self, provider: AIProvider, alert: Alert, context: Dict[str, Any]
    ) -> Optional[Diagnosis]:
        """Diagnose with specific provider"""

        if provider == AIProvider.OPENAI:
            return await self._diagnose_openai(alert, context)

        elif provider == AIProvider.GEMINI:
            return await self._diagnose_gemini(alert, context)

        elif provider == AIProvider.CLAUDE:
            return await self._diagnose_claude(alert, context)

        elif provider == AIProvider.AZURE_OPENAI:
            return await self._diagnose_azure_openai(alert, context)

        elif provider == AIProvider.OLLAMA:
            return await self._diagnose_ollama(alert, context)

        elif provider == AIProvider.OFFLINE:
            return await self._diagnose_offline(alert, context)

        return None

    async def _diagnose_openai(
        self, alert: Alert, context: Dict[str, Any]
    ) -> Diagnosis:
        """Diagnose using OpenAI GPT"""

        provider_info = self.providers[AIProvider.OPENAI]
        client = provider_info["client"]
        model = provider_info["model"]

        prompt = self._build_diagnosis_prompt(alert, context)

        response = client.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert IT infrastructure engineer.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)

        return Diagnosis(
            alert_id=alert.id,
            root_cause=result.get("root_cause", "Unknown"),
            confidence=result.get("confidence", 70),
            recommended_actions=result.get("actions", []),
            context=context,
            ai_model=f"openai:{model}",
        )

    async def _diagnose_gemini(
        self, alert: Alert, context: Dict[str, Any]
    ) -> Diagnosis:
        """Diagnose using Google Gemini"""

        provider_info = self.providers[AIProvider.GEMINI]
        client = provider_info["client"]
        model_name = provider_info["model"]

        prompt = self._build_diagnosis_prompt(alert, context)

        model = client.GenerativeModel(model_name)
        response = model.generate_content(
            prompt, generation_config={"temperature": 0.1, "candidate_count": 1}
        )

        # Parse JSON from response
        result = self._parse_ai_response(response.text)

        return Diagnosis(
            alert_id=alert.id,
            root_cause=result.get("root_cause", "Unknown"),
            confidence=result.get("confidence", 70),
            recommended_actions=result.get("actions", []),
            context=context,
            ai_model=f"gemini:{model_name}",
        )

    async def _diagnose_claude(
        self, alert: Alert, context: Dict[str, Any]
    ) -> Diagnosis:
        """Diagnose using Anthropic Claude"""

        provider_info = self.providers[AIProvider.CLAUDE]
        client = provider_info["client"]
        model = provider_info["model"]

        prompt = self._build_diagnosis_prompt(alert, context)

        message = client.messages.create(
            model=model,
            max_tokens=2048,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}],
        )

        result = self._parse_ai_response(message.content[0].text)

        return Diagnosis(
            alert_id=alert.id,
            root_cause=result.get("root_cause", "Unknown"),
            confidence=result.get("confidence", 70),
            recommended_actions=result.get("actions", []),
            context=context,
            ai_model=f"claude:{model}",
        )

    async def _diagnose_azure_openai(
        self, alert: Alert, context: Dict[str, Any]
    ) -> Diagnosis:
        """Diagnose using Azure OpenAI"""

        provider_info = self.providers[AIProvider.AZURE_OPENAI]
        client = provider_info["client"]
        deployment = provider_info["model"]

        prompt = self._build_diagnosis_prompt(alert, context)

        response = client.ChatCompletion.create(
            engine=deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert IT infrastructure engineer.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        result = self._parse_ai_response(response.choices[0].message.content)

        return Diagnosis(
            alert_id=alert.id,
            root_cause=result.get("root_cause", "Unknown"),
            confidence=result.get("confidence", 70),
            recommended_actions=result.get("actions", []),
            context=context,
            ai_model=f"azure:{deployment}",
        )

    async def _diagnose_ollama(
        self, alert: Alert, context: Dict[str, Any]
    ) -> Diagnosis:
        """Diagnose using Ollama (local LLM)"""

        provider_info = self.providers[AIProvider.OLLAMA]
        ollama_client = provider_info["client"]

        return await ollama_client.diagnose_with_llm(alert, context)

    async def _diagnose_offline(
        self, alert: Alert, context: Dict[str, Any]
    ) -> Diagnosis:
        """Diagnose using offline rule-based engine"""

        provider_info = self.providers[AIProvider.OFFLINE]
        offline_engine = provider_info["client"]

        return await offline_engine.diagnose_issue(alert, context)

    def _build_diagnosis_prompt(self, alert: Alert, context: Dict[str, Any]) -> str:
        """Build diagnosis prompt for AI"""

        return f"""You are an expert IT infrastructure engineer. Analyze this alert and provide a diagnosis.

Alert Information:
- Message: {alert.message}
- Host: {alert.host}
- Severity: {alert.severity.value}
- Source: {alert.source.value}
- Metrics: {json.dumps(alert.metrics, indent=2)}

System Context:
{json.dumps(context, indent=2)}

Provide your response in JSON format:
{{
    "root_cause": "Brief description of the root cause",
    "confidence": 85,
    "actions": [
        {{
            "command": "exact command to execute",
            "description": "what the command does",
            "platform": "linux|windows|network",
            "risk": "none|low|medium|high|critical"
        }}
    ]
}}

Focus on safe, effective remediation that can be automated."""

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""

        try:
            # Try to extract JSON
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)

        except Exception as e:
            self.logger.error(f"Failed to parse AI response: {e}")

        return {
            "root_cause": "Unable to parse diagnosis",
            "confidence": 50,
            "actions": [],
        }

    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        return [
            provider.value
            for provider, info in self.providers.items()
            if info["available"]
        ]

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            provider.value: {"available": info["available"], "model": info["model"]}
            for provider, info in self.providers.items()
        }
