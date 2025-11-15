"""
iTechSmart Think-Tank - Main Application
Internal platform for creating custom apps with AI assistance
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from datetime import datetime

from app.core.database import init_db, check_db_connection
from app.core.superninja_agent import SuperNinjaAgent
from app.core.project_engine import ProjectEngine
from app.core.collaboration_engine import CollaborationEngine

# Global instances
superninja_agent = None
project_engine = None
collaboration_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    global superninja_agent, project_engine, collaboration_engine
    
    print("🚀 Starting iTechSmart Think-Tank...")
    
    # Initialize database
    init_db()
    
    # Check database connection
    if not check_db_connection():
        print("⚠️  Warning: Database connection failed")
    
    # Initialize engines
    superninja_agent = SuperNinjaAgent()
    project_engine = ProjectEngine()
    collaboration_engine = CollaborationEngine()
    print("✅ Core engines initialized")
    
    # TODO: Initialize integrations with Hub, Ninja, QA/QC
    
    print("✅ iTechSmart Think-Tank is ready!")
    print(f"📊 Dashboard: http://localhost:8030")
    print(f"🤖 SuperNinja Agent: Active")
    print(f"💬 Team Chat: Enabled")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down iTechSmart Think-Tank...")
    print("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="iTechSmart Think-Tank",
    description="Internal platform for creating custom apps with AI assistance",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "iTechSmart Think-Tank",
        "version": "1.0.0",
        "status": "operational",
        "description": "Internal platform for creating custom apps with AI assistance",
        "features": [
            "Custom app creation with AI",
            "SuperNinja Agent integration",
            "Real-time team collaboration",
            "Progress tracking",
            "Client portal",
            "Suite integration (Enterprise, Ninja, QA/QC)",
            "Project management",
            "Idea board"
        ],
        "endpoints": {
            "api_docs": "/docs",
            "health": "/health",
            "superninja": "/api/v1/ai",
            "projects": "/api/v1/projects",
            "chat": "/api/v1/chat",
            "websocket": "/ws/{project_id}"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# Health endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    db_healthy = check_db_connection()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "iTechSmart Think-Tank",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "superninja_agent": "active" if superninja_agent else "inactive",
            "project_engine": "active" if project_engine else "inactive",
            "collaboration_engine": "active" if collaboration_engine else "inactive"
        }
    }


# WebSocket endpoint for real-time chat
@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: int):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    # Add connection to collaboration engine
    if project_id not in collaboration_engine.active_connections:
        collaboration_engine.active_connections[project_id] = []
    collaboration_engine.active_connections[project_id].append(websocket)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "message":
                # Broadcast to all clients in the project
                for connection in collaboration_engine.active_connections[project_id]:
                    if connection != websocket:
                        await connection.send_json(data)
    
    except WebSocketDisconnect:
        # Remove connection
        collaboration_engine.active_connections[project_id].remove(websocket)
        if not collaboration_engine.active_connections[project_id]:
            del collaboration_engine.active_connections[project_id]


# SuperNinja Agent endpoint
@app.post("/api/v1/ai/generate-code")
async def generate_code(request: dict):
    """Generate code using SuperNinja Agent"""
    result = await superninja_agent.generate_code(
        prompt=request.get("prompt"),
        language=request.get("language", "python"),
        framework=request.get("framework"),
        context=request.get("context")
    )
    return result


@app.post("/api/v1/ai/scaffold-app")
async def scaffold_app(request: dict):
    """Scaffold a complete application"""
    result = await superninja_agent.scaffold_app(
        app_name=request.get("app_name"),
        app_type=request.get("app_type"),
        features=request.get("features", []),
        tech_stack=request.get("tech_stack", {})
    )
    return result


@app.post("/api/v1/ai/chat")
async def chat_with_agent(request: dict):
    """Chat with SuperNinja Agent"""
    result = await superninja_agent.chat(
        message=request.get("message"),
        context=request.get("context")
    )
    return result


@app.get("/api/v1/ai/status")
async def agent_status():
    """Get SuperNinja Agent status"""
    return await superninja_agent.get_status()


# Info endpoint
@app.get("/info")
async def info():
    """System information endpoint"""
    return {
        "service": "iTechSmart Think-Tank",
        "version": "1.0.0",
        "description": "Internal platform for creating custom apps with AI assistance",
        "port": 8030,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "features": {
            "superninja_agent": {
                "status": "active",
                "capabilities": [
                    "code_generation",
                    "app_scaffolding",
                    "bug_fixing",
                    "optimization",
                    "documentation",
                    "testing",
                    "deployment"
                ]
            },
            "collaboration": {
                "real_time_chat": True,
                "file_sharing": True,
                "video_calls": "planned",
                "screen_sharing": "planned"
            },
            "project_management": {
                "kanban_board": True,
                "task_tracking": True,
                "progress_updates": True,
                "client_portal": True
            },
            "integrations": {
                "itechsmart_enterprise": True,
                "itechsmart_ninja": True,
                "itechsmart_qaqc": True,
                "suite_products": "all_29"
            }
        },
        "api_version": "v1",
        "documentation_url": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8030))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )