"""
Itechsmart-devops - Main Entry Point
CI/CD Automation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Itechsmart-devops...")
    yield
    logger.info("Shutting down Itechsmart-devops...")


app = FastAPI(
    title="Itechsmart-devops",
    description="CI/CD Automation - Part of iTechSmart Suite",
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
        "name": "Itechsmart-devops",
        "version": "1.0.0",
        "description": "CI/CD Automation",
        "status": "operational",
        "suite": "iTechSmart Suite",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Itechsmart-devops", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8021)
