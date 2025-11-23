"""
Itechsmart-customer-success - Main Entry Point
Customer Success Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from cdp_engine import CDPEngine
from app.api.crm_endpoints import router as crm_router, set_cdp_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global CDP engine instance
cdp_engine_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global cdp_engine_instance
    logger.info("Starting Itechsmart-customer-success...")

    try:
        # Initialize CDP engine
        config = {
            "database_url": os.getenv(
                "DATABASE_URL", "postgresql://user:pass@localhost/itechsmart_cdp"
            ),
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", 6379)),
            "neo4j_uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "neo4j_user": os.getenv("NEO4J_USER", "neo4j"),
            "neo4j_password": os.getenv("NEO4J_PASSWORD", "password"),
            "kafka_servers": os.getenv("KAFKA_SERVERS", "localhost:9092").split(","),
            "crm_integrations": {
                "salesforce": (
                    {
                        "client_id": os.getenv("SALESFORCE_CLIENT_ID"),
                        "client_secret": os.getenv("SALESFORCE_CLIENT_SECRET"),
                        "username": os.getenv("SALESFORCE_USERNAME"),
                        "password": os.getenv("SALESFORCE_PASSWORD"),
                    }
                    if os.getenv("SALESFORCE_CLIENT_ID")
                    else None
                ),
                "hubspot": (
                    {"access_token": os.getenv("HUBSPOT_ACCESS_TOKEN")}
                    if os.getenv("HUBSPOT_ACCESS_TOKEN")
                    else None
                ),
                "marketo": (
                    {
                        "endpoint": os.getenv("MARKETO_ENDPOINT"),
                        "client_id": os.getenv("MARKETO_CLIENT_ID"),
                        "client_secret": os.getenv("MARKETO_CLIENT_SECRET"),
                    }
                    if os.getenv("MARKETO_ENDPOINT")
                    else None
                ),
            },
        }

        # Filter out None values from CRM configs
        crm_configs = {
            k: v for k, v in config["crm_integrations"].items() if v is not None
        }
        config["crm_integrations"] = crm_configs

        cdp_engine_instance = CDPEngine(config)
        await cdp_engine_instance.initialize()

        # Initialize CRM integrations if configured
        if crm_configs:
            await cdp_engine_instance.initialize_crm_integrations(crm_configs)

        # Set CDP engine for CRM endpoints
        set_cdp_engine(cdp_engine_instance)

        logger.info("CDP engine initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize CDP engine: {str(e)}")
        # Continue without CDP engine for basic functionality

    yield

    logger.info("Shutting down Itechsmart-customer-success...")

    # Cleanup CDP engine
    if cdp_engine_instance:
        try:
            await cdp_engine_instance.close()
        except Exception as e:
            logger.error(f"Error during CDP engine cleanup: {str(e)}")


app = FastAPI(
    title="Itechsmart-customer-success",
    description="Customer Data Platform (CDP) - Part of iTechSmart Suite",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include CRM endpoints
app.include_router(crm_router)


@app.get("/")
def root():
    return {
        "name": "Itechsmart-customer-success",
        "version": "2.0.0",
        "description": "Customer Data Platform (CDP)",
        "status": "operational",
        "suite": "iTechSmart Suite",
        "features": [
            "Customer Profile Unification",
            "Journey Orchestration",
            "Real-time Personalization",
            "CRM Integrations (Salesforce, HubSpot, Marketo)",
            "Advanced Analytics",
            "Predictive Insights",
        ],
    }


@app.get("/health")
def health_check():
    health_status = {
        "status": "healthy",
        "service": "Itechsmart-customer-success",
        "version": "2.0.0",
        "cdp_engine": "initialized" if cdp_engine_instance else "not_initialized",
    }

    # Check CRM integrations if CDP engine is available
    if cdp_engine_instance:
        try:
            # This would be async in a real health check
            # For now, just indicate CRM availability
            health_status["crm_integrations"] = "configured"
        except:
            health_status["crm_integrations"] = "error"
    else:
        health_status["crm_integrations"] = "unavailable"

    return health_status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8026)
