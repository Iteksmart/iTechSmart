"""
Ollama Integration - Local LLM for AI Diagnosis
Run large language models locally without external API dependencies
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import aiohttp
import json

from ..core.models import Alert, Diagnosis


class OllamaIntegration:
    """Integration with Ollama for local LLM-powered diagnosis"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.available_models = []
    
    async def initialize(self):
        """Initialize Ollama connection and check available models"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check if Ollama is running
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.available_models = [model['name'] for model in data.get('models', [])]
                        self.logger.info(f"Ollama connected. Available models: {self.available_models}")
                        
                        # Use the first available model if specified model not found
                        if self.model not in self.available_models and self.available_models:
                            self.model = self.available_models[0]
                            self.logger.info(f"Using model: {self.model}")
                        
                        return True
                    else:
                        self.logger.error(f"Ollama not available: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    async def diagnose_with_llm(self, alert: Alert, context: Dict[str, Any]) -> Diagnosis:
        """Use local LLM to diagnose infrastructure issues"""
        
        prompt = self._build_diagnosis_prompt(alert, context)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        llm_response = data.get('response', '')
                        
                        # Parse LLM response
                        diagnosis_data = self._parse_llm_response(llm_response)
                        
                        return Diagnosis(
                            alert_id=alert.id,
                            root_cause=diagnosis_data.get('root_cause', 'Unknown issue'),
                            confidence=diagnosis_data.get('confidence', 70),
                            recommended_actions=diagnosis_data.get('actions', []),
                            context=context,
                            ai_model=f"ollama:{self.model}"
                        )
                    else:
                        self.logger.error(f"Ollama API error: {response.status}")
                        return self._fallback_diagnosis(alert, context)
        
        except Exception as e:
            self.logger.error(f"Ollama diagnosis failed: {e}")
            return self._fallback_diagnosis(alert, context)
    
    def _build_diagnosis_prompt(self, alert: Alert, context: Dict[str, Any]) -> str:
        """Build prompt for LLM diagnosis"""
        
        prompt = f"""You are an expert IT infrastructure engineer. Analyze this alert and provide a diagnosis.

Alert Information:
- Message: {alert.message}
- Host: {alert.host}
- Severity: {alert.severity.value}
- Source: {alert.source.value}
- Metrics: {json.dumps(alert.metrics, indent=2)}

System Context:
{json.dumps(context, indent=2)}

Provide your response in the following JSON format:
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

Focus on safe, effective remediation that can be automated. Be specific with commands."""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return {
                    'root_cause': response[:200],
                    'confidence': 60,
                    'actions': []
                }
        
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            return {
                'root_cause': 'Unable to parse diagnosis',
                'confidence': 50,
                'actions': []
            }
    
    def _fallback_diagnosis(self, alert: Alert, context: Dict[str, Any]) -> Diagnosis:
        """Fallback diagnosis when LLM fails"""
        
        return Diagnosis(
            alert_id=alert.id,
            root_cause="LLM diagnosis unavailable - manual investigation required",
            confidence=30,
            recommended_actions=[],
            context=context,
            ai_model="fallback"
        )
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama library"""
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"name": model_name}
                
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json=payload
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Successfully pulled model: {model_name}")
                        await self.initialize()  # Refresh available models
                        return True
                    else:
                        self.logger.error(f"Failed to pull model: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error pulling model: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        await self.initialize()
        return self.available_models
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Chat completion for interactive diagnosis"""
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                }
                
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('message', {}).get('content', '')
                    else:
                        return "Chat completion failed"
        
        except Exception as e:
            self.logger.error(f"Chat completion error: {e}")
            return f"Error: {str(e)}"