"""
Itechsmart-customer-success - Main Entry Point
Customer Success Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Itechsmart-customer-success...")
    yield
    logger.info("Shutting down Itechsmart-customer-success...")


app = FastAPI(
    title="Itechsmart-customer-success",
    description="Customer Success Platform - Part of iTechSmart Suite",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "Itechsmart-customer-success",
        "version": "1.0.0",
        "description": "Customer Success Platform",
        "status": "operational",
        "suite": "iTechSmart Suite",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Itechsmart-customer-success",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8026)
