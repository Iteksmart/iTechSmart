"""
Itechsmart-data-platform - Main Entry Point
Data Governance
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Itechsmart-data-platform...")
    yield
    logger.info("Shutting down Itechsmart-data-platform...")

app = FastAPI(
    title="Itechsmart-data-platform",
    description="Data Governance - Part of iTechSmart Suite",
    version="1.0.0",
    lifespan=lifespan
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
        "name": "Itechsmart-data-platform",
        "version": "1.0.0",
        "description": "Data Governance",
        "status": "operational",
        "suite": "iTechSmart Suite"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Itechsmart-data-platform", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8025)
