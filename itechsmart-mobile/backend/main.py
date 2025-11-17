"""
Itechsmart-mobile - Main Entry Point
Mobile Development Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Itechsmart-mobile...")
    yield
    logger.info("Shutting down Itechsmart-mobile...")


app = FastAPI(
    title="Itechsmart-mobile",
    description="Mobile Development Platform - Part of iTechSmart Suite",
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
        "name": "Itechsmart-mobile",
        "version": "1.0.0",
        "description": "Mobile Development Platform",
        "status": "operational",
        "suite": "iTechSmart Suite",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Itechsmart-mobile", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8022)
