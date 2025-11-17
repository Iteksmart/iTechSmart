"""
Models API - Enhanced AI Model Management
Provides endpoints for browsing, selecting, and comparing AI models
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.integrations.enhanced_ai_providers import (
    enhanced_ai_manager,
    ModelProvider,
    ModelTier,
)
from app.core.security import get_current_user
from app.models.database import User

router = APIRouter(prefix="/api/models", tags=["models"])


# ==================== REQUEST/RESPONSE MODELS ====================


class CompletionRequest(BaseModel):
    """Request for generating completion"""

    model_id: str
    messages: List[Dict[str, str]]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False


class CompletionResponse(BaseModel):
    """Response from completion generation"""

    content: str
    model: str
    usage: Dict[str, int]
    cost: float
    finish_reason: str


class ModelComparisonRequest(BaseModel):
    """Request for comparing models"""

    model_ids: List[str]
    criteria: List[str] = ["cost", "context_window", "speed"]


# ==================== ENDPOINTS ====================


@router.get("/all")
async def get_all_models(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get all available AI models

    Returns:
        List of all 40+ supported models with their capabilities
    """
    models = enhanced_ai_manager.get_all_models()

    return {
        "success": True,
        "total_models": len(models),
        "models": models,
        "providers": [p.value for p in ModelProvider],
        "tiers": [t.value for t in ModelTier],
    }


@router.get("/provider/{provider}")
async def get_models_by_provider(
    provider: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get models for a specific provider

    Args:
        provider: Provider name (openai, anthropic, google, etc.)
    """
    try:
        provider_enum = ModelProvider(provider)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    models = enhanced_ai_manager.get_models_by_provider(provider_enum)
    is_available = enhanced_ai_manager.is_provider_available(provider_enum)

    return {
        "success": True,
        "provider": provider,
        "available": is_available,
        "total_models": len(models),
        "models": models,
    }


@router.get("/tier/{tier}")
async def get_models_by_tier(
    tier: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get models by capability tier

    Args:
        tier: Tier name (flagship, advanced, standard, fast, local)
    """
    try:
        tier_enum = ModelTier(tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")

    models = enhanced_ai_manager.get_models_by_tier(tier_enum)

    return {
        "success": True,
        "tier": tier,
        "total_models": len(models),
        "models": models,
    }


@router.get("/{model_id}")
async def get_model_details(
    model_id: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific model

    Args:
        model_id: Model identifier
    """
    model = enhanced_ai_manager.get_model(model_id)

    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

    # Get usage stats for this model
    usage_stats = enhanced_ai_manager.get_usage_stats(model_id)

    return {
        "success": True,
        "model": model.to_dict(),
        "usage_stats": usage_stats,
        "provider_available": enhanced_ai_manager.is_provider_available(model.provider),
    }


@router.post("/generate")
async def generate_completion(
    request: CompletionRequest, current_user: User = Depends(get_current_user)
) -> CompletionResponse:
    """
    Generate completion using specified model

    Args:
        request: Completion request with model, messages, and parameters
    """
    try:
        result = await enhanced_ai_manager.generate_completion(
            model_id=request.model_id,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream,
        )

        if request.stream:
            # For streaming, return stream object
            # (In production, use StreamingResponse)
            raise HTTPException(
                status_code=501, detail="Streaming not yet implemented in this endpoint"
            )

        return CompletionResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/compare")
async def compare_models(
    request: ModelComparisonRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Compare multiple models across different criteria

    Args:
        request: Comparison request with model IDs and criteria
    """
    comparison = enhanced_ai_manager.compare_models(
        model_ids=request.model_ids, criteria=request.criteria
    )

    if not comparison:
        raise HTTPException(
            status_code=404, detail="No valid models found for comparison"
        )

    return {"success": True, "comparison": comparison, "criteria": request.criteria}


@router.get("/usage/stats")
async def get_usage_statistics(
    model_id: Optional[str] = None, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get usage statistics for models

    Args:
        model_id: Optional model ID to get stats for specific model
    """
    stats = enhanced_ai_manager.get_usage_stats(model_id)

    return {"success": True, "model_id": model_id, "stats": stats}


@router.get("/providers/status")
async def get_providers_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get status of all AI providers (configured/available)
    """
    status = {}

    for provider in ModelProvider:
        is_available = enhanced_ai_manager.is_provider_available(provider)
        models = enhanced_ai_manager.get_models_by_provider(provider)

        status[provider.value] = {
            "available": is_available,
            "total_models": len(models),
            "models": [m["id"] for m in models],
        }

    return {"success": True, "providers": status}


@router.get("/recommendations")
async def get_model_recommendations(
    task_type: str = "general",
    budget: str = "medium",
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get model recommendations based on task type and budget

    Args:
        task_type: Type of task (general, coding, research, creative, fast)
        budget: Budget level (low, medium, high, unlimited)
    """
    recommendations = []

    # Define recommendation logic
    if task_type == "coding":
        if budget == "low":
            recommendations = ["gpt-3.5-turbo", "deepseek-coder", "codellama:70b"]
        elif budget == "medium":
            recommendations = [
                "gpt-4o-mini",
                "claude-3-haiku-20240307",
                "deepseek-coder",
            ]
        else:
            recommendations = ["gpt-4-turbo", "claude-3-5-sonnet-20241022", "gpt-4o"]

    elif task_type == "research":
        if budget == "low":
            recommendations = [
                "pplx-7b-online",
                "gpt-3.5-turbo",
                "mistral-small-latest",
            ]
        elif budget == "medium":
            recommendations = [
                "pplx-70b-online",
                "gpt-4o-mini",
                "claude-3-sonnet-20240229",
            ]
        else:
            recommendations = [
                "claude-3-opus-20240229",
                "gpt-4-turbo",
                "gemini-1.5-pro",
            ]

    elif task_type == "creative":
        if budget == "low":
            recommendations = ["gpt-3.5-turbo", "mistral-small-latest", "llama3.1:8b"]
        elif budget == "medium":
            recommendations = [
                "gpt-4o-mini",
                "claude-3-sonnet-20240229",
                "mistral-medium-latest",
            ]
        else:
            recommendations = ["claude-3-opus-20240229", "gpt-4o", "gemini-1.5-pro"]

    elif task_type == "fast":
        recommendations = [
            "gpt-4o-mini",
            "claude-3-haiku-20240307",
            "gemini-1.5-flash",
            "mistral-small-latest",
            "llama3.1:8b",
        ]

    else:  # general
        if budget == "low":
            recommendations = ["gpt-3.5-turbo", "mistral-small-latest", "llama3.1:8b"]
        elif budget == "medium":
            recommendations = [
                "gpt-4o-mini",
                "claude-3-sonnet-20240229",
                "gemini-1.5-flash",
            ]
        else:
            recommendations = ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]

    # Get full model details for recommendations
    recommended_models = []
    for model_id in recommendations:
        model = enhanced_ai_manager.get_model(model_id)
        if model:
            recommended_models.append(model.to_dict())

    return {
        "success": True,
        "task_type": task_type,
        "budget": budget,
        "recommendations": recommended_models,
    }


@router.get("/search")
async def search_models(
    query: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Search models by name, provider, or capabilities

    Args:
        query: Search query
    """
    all_models = enhanced_ai_manager.get_all_models()
    query_lower = query.lower()

    # Search in name, provider, description
    results = [
        model
        for model in all_models
        if (
            query_lower in model["name"].lower()
            or query_lower in model["provider"].lower()
            or query_lower in model["description"].lower()
            or query_lower in model["id"].lower()
        )
    ]

    return {
        "success": True,
        "query": query,
        "total_results": len(results),
        "results": results,
    }
