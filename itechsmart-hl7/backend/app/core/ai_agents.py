"""
Multi-AI Agent System
Supports multiple AI providers with admin configuration
"""

import os
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
import json

# AI Provider imports
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    LOCAL = "local"


class AIModel(Enum):
    """Available AI models"""
    # OpenAI
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Google
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"
    
    # Meta
    LLAMA_2_70B = "llama-2-70b"
    LLAMA_3_70B = "llama-3-70b"
    
    # Local
    OLLAMA = "ollama"


class AIAgentConfig:
    """Configuration for AI agents"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self.default_model = None
        
    def add_provider(self, provider: AIProvider, api_key: str, config: Dict = None):
        """Add AI provider configuration"""
        self.providers[provider] = {
            'api_key': api_key,
            'config': config or {},
            'enabled': True
        }
        
        if not self.default_provider:
            self.default_provider = provider
    
    def set_default(self, provider: AIProvider, model: AIModel):
        """Set default provider and model"""
        self.default_provider = provider
        self.default_model = model
    
    def get_provider_config(self, provider: AIProvider) -> Optional[Dict]:
        """Get provider configuration"""
        return self.providers.get(provider)


class AIAgent:
    """
    Multi-AI agent supporting multiple providers
    """
    
    def __init__(self, config: AIAgentConfig):
        self.config = config
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI provider clients"""
        for provider, provider_config in self.config.providers.items():
            if not provider_config['enabled']:
                continue
                
            try:
                if provider == AIProvider.OPENAI and openai:
                    openai.api_key = provider_config['api_key']
                    self.clients[provider] = openai
                    logger.info("OpenAI client initialized")
                    
                elif provider == AIProvider.ANTHROPIC and anthropic:
                    self.clients[provider] = anthropic.Anthropic(
                        api_key=provider_config['api_key']
                    )
                    logger.info("Anthropic client initialized")
                    
                elif provider == AIProvider.GOOGLE and genai:
                    genai.configure(api_key=provider_config['api_key'])
                    self.clients[provider] = genai
                    logger.info("Google AI client initialized")
                    
            except Exception as e:
                logger.error(f"Error initializing {provider.value} client: {str(e)}")
    
    async def analyze(self, 
                     prompt: str, 
                     provider: Optional[AIProvider] = None,
                     model: Optional[AIModel] = None,
                     context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze using AI agent
        
        Args:
            prompt: Analysis prompt
            provider: AI provider to use (default: configured default)
            model: AI model to use (default: configured default)
            context: Additional context for analysis
            
        Returns:
            Analysis results
        """
        provider = provider or self.config.default_provider
        model = model or self.config.default_model
        
        if provider not in self.clients:
            raise ValueError(f"Provider {provider.value} not configured")
        
        try:
            if provider == AIProvider.OPENAI:
                return await self._analyze_openai(prompt, model, context)
            elif provider == AIProvider.ANTHROPIC:
                return await self._analyze_anthropic(prompt, model, context)
            elif provider == AIProvider.GOOGLE:
                return await self._analyze_google(prompt, model, context)
            else:
                raise ValueError(f"Provider {provider.value} not supported")
                
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'root_cause': 'AI analysis failed',
                'actions': ['Manual investigation required'],
                'prevention': ['Check AI service availability']
            }
    
    async def _analyze_openai(self, prompt: str, model: AIModel, context: Optional[Dict]) -> Dict[str, Any]:
        """Analyze using OpenAI"""
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=model.value if model else "gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HL7 integration specialist. Analyze incidents and provide root cause analysis with remediation steps."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Parse structured response
            return self._parse_analysis_response(content)
            
        except Exception as e:
            logger.error(f"OpenAI analysis error: {str(e)}")
            raise
    
    async def _analyze_anthropic(self, prompt: str, model: AIModel, context: Optional[Dict]) -> Dict[str, Any]:
        """Analyze using Anthropic Claude"""
        try:
            client = self.clients[AIProvider.ANTHROPIC]
            
            message = await asyncio.to_thread(
                client.messages.create,
                model=model.value if model else "claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"You are an expert HL7 integration specialist. {prompt}"
                    }
                ]
            )
            
            content = message.content[0].text
            
            return self._parse_analysis_response(content)
            
        except Exception as e:
            logger.error(f"Anthropic analysis error: {str(e)}")
            raise
    
    async def _analyze_google(self, prompt: str, model: AIModel, context: Optional[Dict]) -> Dict[str, Any]:
        """Analyze using Google Gemini"""
        try:
            model_name = model.value if model else "gemini-pro"
            model_instance = genai.GenerativeModel(model_name)
            
            response = await asyncio.to_thread(
                model_instance.generate_content,
                f"You are an expert HL7 integration specialist. {prompt}"
            )
            
            content = response.text
            
            return self._parse_analysis_response(content)
            
        except Exception as e:
            logger.error(f"Google AI analysis error: {str(e)}")
            raise
    
    def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        # Try to extract structured information
        result = {
            'success': True,
            'raw_response': content,
            'root_cause': '',
            'actions': [],
            'prevention': [],
            'confidence': 0.8
        }
        
        # Simple parsing logic (can be enhanced with better NLP)
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if 'root cause' in line.lower():
                current_section = 'root_cause'
                continue
            elif 'recommended action' in line.lower() or 'remediation' in line.lower():
                current_section = 'actions'
                continue
            elif 'prevention' in line.lower():
                current_section = 'prevention'
                continue
            
            # Extract content
            if current_section == 'root_cause' and not result['root_cause']:
                result['root_cause'] = line
            elif current_section == 'actions':
                if line.startswith('-') or line.startswith('•') or line[0].isdigit():
                    result['actions'].append(line.lstrip('-•0123456789. '))
            elif current_section == 'prevention':
                if line.startswith('-') or line.startswith('•') or line[0].isdigit():
                    result['prevention'].append(line.lstrip('-•0123456789. '))
        
        # Fallback if parsing failed
        if not result['root_cause']:
            result['root_cause'] = content[:200] + '...' if len(content) > 200 else content
        
        return result
    
    async def generate_clinical_note(self,
                                    note_type: str,
                                    patient_data: Dict,
                                    clinical_data: Dict,
                                    provider: Optional[AIProvider] = None,
                                    model: Optional[AIModel] = None) -> str:
        """
        Generate clinical note using AI
        
        Args:
            note_type: Type of note (SOAP, Nursing, Progress, etc.)
            patient_data: Patient information
            clinical_data: Clinical information
            provider: AI provider to use
            model: AI model to use
            
        Returns:
            Generated clinical note
        """
        provider = provider or self.config.default_provider
        model = model or self.config.default_model
        
        # Create prompt based on note type
        prompt = self._create_clinical_note_prompt(note_type, patient_data, clinical_data)
        
        try:
            if provider == AIProvider.OPENAI:
                return await self._generate_note_openai(prompt, model)
            elif provider == AIProvider.ANTHROPIC:
                return await self._generate_note_anthropic(prompt, model)
            elif provider == AIProvider.GOOGLE:
                return await self._generate_note_google(prompt, model)
            else:
                raise ValueError(f"Provider {provider.value} not supported")
                
        except Exception as e:
            logger.error(f"Error generating clinical note: {str(e)}")
            raise
    
    def _create_clinical_note_prompt(self, note_type: str, patient_data: Dict, clinical_data: Dict) -> str:
        """Create prompt for clinical note generation"""
        
        base_prompt = f"""
        Generate a professional {note_type} clinical note based on the following information:
        
        Patient Information:
        - Name: {patient_data.get('name', 'N/A')}
        - Age: {patient_data.get('age', 'N/A')}
        - Gender: {patient_data.get('gender', 'N/A')}
        - MRN: {patient_data.get('mrn', 'N/A')}
        
        Clinical Information:
        {json.dumps(clinical_data, indent=2)}
        
        Please generate a complete, professional {note_type} note following standard medical documentation practices.
        """
        
        if note_type == "SOAP":
            base_prompt += """
            Include:
            - Subjective: Patient's complaints and symptoms
            - Objective: Physical examination findings and vital signs
            - Assessment: Diagnosis and clinical impression
            - Plan: Treatment plan and follow-up
            """
        elif note_type == "Nursing":
            base_prompt += """
            Include:
            - Patient assessment
            - Interventions performed
            - Patient response
            - Plan of care
            """
        elif note_type == "Progress":
            base_prompt += """
            Include:
            - Current status
            - Changes since last note
            - Response to treatment
            - Plan modifications if needed
            """
        elif note_type == "Discharge Summary":
            base_prompt += """
            Include:
            - Admission diagnosis
            - Hospital course
            - Discharge diagnosis
            - Discharge medications
            - Follow-up instructions
            """
        
        return base_prompt
    
    async def _generate_note_openai(self, prompt: str, model: AIModel) -> str:
        """Generate note using OpenAI"""
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=model.value if model else "gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an experienced healthcare provider creating clinical documentation. Generate professional, accurate, and compliant clinical notes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI note generation error: {str(e)}")
            raise
    
    async def _generate_note_anthropic(self, prompt: str, model: AIModel) -> str:
        """Generate note using Anthropic"""
        try:
            client = self.clients[AIProvider.ANTHROPIC]
            
            message = await asyncio.to_thread(
                client.messages.create,
                model=model.value if model else "claude-3-opus-20240229",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic note generation error: {str(e)}")
            raise
    
    async def _generate_note_google(self, prompt: str, model: AIModel) -> str:
        """Generate note using Google"""
        try:
            model_name = model.value if model else "gemini-pro"
            model_instance = genai.GenerativeModel(model_name)
            
            response = await asyncio.to_thread(
                model_instance.generate_content,
                prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Google AI note generation error: {str(e)}")
            raise


class AIAgentManager:
    """
    Manager for AI agents with admin configuration
    """
    
    def __init__(self):
        self.config = AIAgentConfig()
        self.agent = None
    
    def configure_provider(self, provider: str, api_key: str, additional_config: Dict = None):
        """
        Configure AI provider (called from admin dashboard)
        
        Args:
            provider: Provider name (openai, anthropic, google, etc.)
            api_key: API key for the provider
            additional_config: Additional configuration options
        """
        try:
            provider_enum = AIProvider(provider.lower())
            self.config.add_provider(provider_enum, api_key, additional_config)
            
            # Reinitialize agent with new config
            self.agent = AIAgent(self.config)
            
            logger.info(f"Provider {provider} configured successfully")
            return {'success': True, 'message': f'{provider} configured'}
            
        except Exception as e:
            logger.error(f"Error configuring provider: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def set_default_provider(self, provider: str, model: str):
        """Set default AI provider and model"""
        try:
            provider_enum = AIProvider(provider.lower())
            model_enum = AIModel(model)
            
            self.config.set_default(provider_enum, model_enum)
            
            logger.info(f"Default provider set to {provider} with model {model}")
            return {'success': True, 'message': 'Default provider updated'}
            
        except Exception as e:
            logger.error(f"Error setting default provider: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_available_providers(self) -> List[Dict]:
        """Get list of available and configured providers"""
        providers = []
        
        for provider in AIProvider:
            config = self.config.get_provider_config(provider)
            providers.append({
                'name': provider.value,
                'display_name': provider.value.title(),
                'configured': config is not None,
                'enabled': config['enabled'] if config else False,
                'is_default': provider == self.config.default_provider
            })
        
        return providers
    
    def get_available_models(self, provider: str) -> List[Dict]:
        """Get available models for a provider"""
        models = []
        
        provider_models = {
            'openai': [AIModel.GPT4, AIModel.GPT4_TURBO, AIModel.GPT35_TURBO],
            'anthropic': [AIModel.CLAUDE_3_OPUS, AIModel.CLAUDE_3_SONNET, AIModel.CLAUDE_3_HAIKU],
            'google': [AIModel.GEMINI_PRO, AIModel.GEMINI_ULTRA],
            'meta': [AIModel.LLAMA_2_70B, AIModel.LLAMA_3_70B],
            'local': [AIModel.OLLAMA]
        }
        
        for model in provider_models.get(provider.lower(), []):
            models.append({
                'name': model.value,
                'display_name': model.value.replace('-', ' ').title(),
                'is_default': model == self.config.default_model
            })
        
        return models
    
    def get_agent(self) -> Optional[AIAgent]:
        """Get configured AI agent"""
        if not self.agent:
            self.agent = AIAgent(self.config)
        return self.agent


# Global agent manager instance
agent_manager = AIAgentManager()


# Example usage
if __name__ == "__main__":
    async def main():
        # Configure providers
        manager = AIAgentManager()
        
        # Add OpenAI
        manager.configure_provider('openai', 'sk-...')
        
        # Set as default
        manager.set_default_provider('openai', 'gpt-4')
        
        # Get agent
        agent = manager.get_agent()
        
        # Analyze incident
        result = await agent.analyze("""
        Analyze this HL7 incident:
        - Type: Message Failure
        - Failed Count: 10
        - Error: Connection timeout
        """)
        
        print(json.dumps(result, indent=2))
        
        # Generate clinical note
        note = await agent.generate_clinical_note(
            note_type="SOAP",
            patient_data={
                'name': 'John Doe',
                'age': 45,
                'gender': 'M',
                'mrn': '123456'
            },
            clinical_data={
                'chief_complaint': 'Chest pain',
                'vitals': {
                    'bp': '140/90',
                    'hr': 88,
                    'temp': 98.6
                },
                'exam_findings': 'Normal heart sounds, no murmurs'
            }
        )
        
        print(f"\nGenerated Note:\n{note}")
    
    asyncio.run(main())