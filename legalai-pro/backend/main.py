"""
LegalAI Pro - Main Application Entry Point
The world's most advanced AI-powered attorney office software
Part of the iTechSmart Suite
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

# Import routers
from app.api import (
    auth,
    clients,
    cases,
    documents,
    billing,
    calendar,
    time_tracking,
    tasks,
    email,
    reports,
    ai_assistant,
    templates,
    users,
    settings
)

# Import database
from app.core.database import engine, Base

# Import iTechSmart Suite integration
from app.integrations.integration import initialize_integration, shutdown_integration

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 LegalAI Pro is starting up...")
    print("🔗 Connecting to iTechSmart Suite...")
    await initialize_integration()
    print("✅ iTechSmart Suite integration active")
    yield
    # Shutdown
    print("👋 LegalAI Pro is shutting down...")
    await shutdown_integration()

# Initialize FastAPI app
app = FastAPI(
    title="LegalAI Pro",
    description="The World's Most Advanced AI-Powered Attorney Office Software - iTechSmart Suite Member",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(time_tracking.router, prefix="/api/time", tags=["Time Tracking"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(email.router, prefix="/api/email", tags=["Email"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(ai_assistant.router, prefix="/api/ai", tags=["AI Assistant"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to LegalAI Pro",
        "version": "1.0.0",
        "description": "The World's Most Advanced AI-Powered Attorney Office Software",
        "suite": "iTechSmart Suite Member",
        "features": [
            "AI Document Auto-Fill",
            "AI Legal Research",
            "AI Contract Analysis",
            "AI Case Prediction",
            "Complete Case Management",
            "Time & Billing",
            "Document Management",
            "Calendar & Docketing",
            "Client Portal",
            "iTechSmart Suite Integration",
            "Self-Healing with Ninja",
            "Cross-Product Communication"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LegalAI Pro", "suite": "iTechSmart"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )