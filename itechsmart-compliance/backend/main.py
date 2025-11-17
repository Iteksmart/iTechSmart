"""
iTechSmart Compliance - Main Application Entry Point
Regulatory compliance tracking and management platform with Compliance Center
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import API routers
from app.api.compliance_center import router as compliance_center_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting iTechSmart Compliance with Compliance Center...")
    yield
    logger.info("Shutting down iTechSmart Compliance...")


app = FastAPI(
    title="iTechSmart Compliance",
    description="Regulatory Compliance Tracking and Management Platform with Multi-Framework Support",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(compliance_center_router)


@app.get("/")
def root():
    return {
        "name": "iTechSmart Compliance",
        "version": "1.1.0",
        "description": "Compliance Management with Compliance Center",
        "status": "operational",
        "suite": "iTechSmart Suite",
        "features": [
            "Multi-framework compliance tracking (SOC2, ISO 27001, HIPAA, GDPR, PCI-DSS)",
            "Compliance Center with policy alignment",
            "Evidence management",
            "Assessment and audit workflows",
            "Gap analysis and reporting",
            "Policy document management",
            "Audit trail tracking",
        ],
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "iTechSmart Compliance", "version": "1.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8019)
