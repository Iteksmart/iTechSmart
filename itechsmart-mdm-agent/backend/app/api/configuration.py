"""
Configuration API Endpoints for iTechSmart MDM Deployment Agent
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["configuration"])


class GenerateConfigRequest(BaseModel):
    """Request model for generating configuration"""
    product_name: str = Field(..., description="Product name")
    environment: str = Field(..., description="Environment")
    overrides: Optional[Dict[str, Any]] = Field(None, description="Configuration overrides")


class ValidateConfigRequest(BaseModel):
    """Request model for validating configuration"""
    product_name: str = Field(..., description="Product name")
    configuration: Dict[str, Any] = Field(..., description="Configuration to validate")


@router.get("/templates")
async def list_templates():
    """List all configuration templates"""
    templates = [
        {"product": "itechsmart-enterprise", "environments": ["dev", "staging", "prod"]},
        {"product": "itechsmart-ninja", "environments": ["dev", "staging", "prod"]},
        {"product": "itechsmart-analytics", "environments": ["dev", "staging", "prod"]},
        {"product": "legalai-pro", "environments": ["dev", "staging", "prod"]},
    ]
    
    return {
        "templates": templates,
        "total": len(templates)
    }


@router.get("/template/{product_name}")
async def get_template(product_name: str, environment: str = "production"):
    """Get configuration template for a product"""
    template = {
        "product_name": product_name,
        "environment": environment,
        "template": {
            "database": {
                "host": "${DB_HOST}",
                "port": "${DB_PORT}",
                "name": "${DB_NAME}",
                "user": "${DB_USER}",
                "password": "${DB_PASSWORD}"
            },
            "redis": {
                "host": "${REDIS_HOST}",
                "port": "${REDIS_PORT}"
            },
            "app": {
                "port": "${APP_PORT}",
                "workers": "${WORKERS}",
                "log_level": "${LOG_LEVEL}"
            }
        },
        "variables": {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": product_name,
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "APP_PORT": "8000",
            "WORKERS": "4",
            "LOG_LEVEL": "info"
        }
    }
    
    return template


@router.post("/generate")
async def generate_configuration(request: GenerateConfigRequest):
    """Generate configuration for a product"""
    logger.info(f"Generating configuration for {request.product_name}")
    
    config = {
        "product_name": request.product_name,
        "environment": request.environment,
        "generated_config": {
            "database_url": f"postgresql://user:pass@localhost:5432/{request.product_name}",
            "redis_url": "redis://localhost:6379",
            "app_port": 8000,
            "workers": 4,
            "log_level": "info"
        }
    }
    
    if request.overrides:
        config["generated_config"].update(request.overrides)
    
    return config


@router.post("/validate")
async def validate_configuration(request: ValidateConfigRequest):
    """Validate a configuration"""
    logger.info(f"Validating configuration for {request.product_name}")
    
    errors = []
    warnings = []
    
    # Basic validation
    if not request.configuration:
        errors.append("Configuration is empty")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "product_name": request.product_name
    }


@router.get("/export/{product_name}")
async def export_configuration(product_name: str, format: str = "json"):
    """Export configuration in specified format"""
    if format not in ["json", "yaml", "env"]:
        raise HTTPException(status_code=400, detail="Invalid format. Use json, yaml, or env")
    
    config = {
        "product_name": product_name,
        "format": format,
        "content": "# Configuration export\nKEY=value\n"
    }
    
    return config


@router.get("/variables/{product_name}")
async def get_variables(product_name: str):
    """Get available variables for a product"""
    variables = {
        "required": ["DB_HOST", "DB_PORT", "DB_NAME", "APP_PORT"],
        "optional": ["REDIS_HOST", "REDIS_PORT", "LOG_LEVEL", "WORKERS"],
        "defaults": {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "APP_PORT": "8000",
            "LOG_LEVEL": "info",
            "WORKERS": "4"
        }
    }
    
    return variables
