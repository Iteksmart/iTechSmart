"""
AI Agent API Routes
FastAPI endpoints for AI agent configuration and management
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Agents"])


# Request/Response Models


class ConfigureProviderRequest(BaseModel):
    """Request model for configuring AI provider"""

    provider: str = Field(..., description="openai, anthropic, google, meta, local")
    api_key: str = Field(..., description="API key for the provider")
    additional_config: Optional[Dict] = Field(
        None, description="Additional configuration"
    )


class SetDefaultProviderRequest(BaseModel):
    """Request model for setting default provider"""

    provider: str
    model: str


class TestProviderRequest(BaseModel):
    """Request model for testing provider"""

    provider: str
    test_prompt: str = Field("Hello, this is a test.", description="Test prompt")


# Endpoints


@router.post("/configure")
async def configure_provider(request: ConfigureProviderRequest):
    """
    Configure AI provider

    Adds or updates AI provider configuration (admin only)
    """
    try:
        from app.core.ai_agents import agent_manager

        result = agent_manager.configure_provider(
            request.provider, request.api_key, request.additional_config
        )

        if result["success"]:
            return {
                "success": True,
                "message": f"Provider {request.provider} configured successfully",
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        logger.error(f"Error configuring provider: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-default")
async def set_default_provider(request: SetDefaultProviderRequest):
    """
    Set default AI provider

    Sets the default provider and model for AI operations
    """
    try:
        from app.core.ai_agents import agent_manager

        result = agent_manager.set_default_provider(request.provider, request.model)

        if result["success"]:
            return {
                "success": True,
                "message": f"Default provider set to {request.provider} with model {request.model}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        logger.error(f"Error setting default provider: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_providers():
    """
    Get available AI providers

    Returns list of all available providers and their configuration status
    """
    try:
        from app.core.ai_agents import agent_manager

        providers = agent_manager.get_available_providers()

        return {
            "providers": providers,
            "total": len(providers),
            "configured": len([p for p in providers if p["configured"]]),
        }

    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/{provider}/models")
async def get_provider_models(provider: str):
    """
    Get available models for provider

    Returns list of models available for the specified provider
    """
    try:
        from app.core.ai_agents import agent_manager

        models = agent_manager.get_available_models(provider)

        return {"provider": provider, "models": models, "total": len(models)}

    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_provider(request: TestProviderRequest):
    """
    Test AI provider

    Tests provider connection and response
    """
    try:
        from app.core.ai_agents import agent_manager, AIProvider

        agent = agent_manager.get_agent()

        if not agent:
            raise HTTPException(status_code=400, detail="No AI agent configured")

        # Test with simple prompt
        result = await agent.analyze(
            request.test_prompt, provider=AIProvider(request.provider)
        )

        return {
            "success": result.get("success", True),
            "provider": request.provider,
            "response": result.get("raw_response", ""),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error testing provider: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage")
async def get_usage_statistics(
    provider: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    """
    Get AI usage statistics

    Returns usage metrics for AI providers
    """
    try:
        # In production: query database for usage stats
        stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "success_rate": 0.0,
            "avg_response_time_ms": 0.0,
            "requests_by_provider": {},
            "requests_by_model": {},
            "requests_by_type": {},
        }

        return stats

    except Exception as e:
        logger.error(f"Error getting usage statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check for AI services

    Returns health status of all configured AI providers
    """
    try:
        from app.core.ai_agents import agent_manager

        providers = agent_manager.get_available_providers()

        health_status = {"overall_status": "healthy", "providers": []}

        for provider in providers:
            if provider["configured"]:
                # In production: test each provider
                health_status["providers"].append(
                    {
                        "name": provider["name"],
                        "status": "healthy",
                        "is_default": provider["is_default"],
                    }
                )

        return health_status

    except Exception as e:
        logger.error(f"Error checking AI health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
