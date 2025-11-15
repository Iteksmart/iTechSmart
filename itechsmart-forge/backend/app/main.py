"""
iTechSmart Forge - Main Application
Low-Code/No-Code Application Builder with AI
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import os

from app.core.database import init_db, get_db
from app.core.app_builder_engine import AppBuilderEngine
from app.core.ai_engine import AIEngine
from app.core.data_connector_engine import DataConnectorEngine
from app.core.workflow_engine import WorkflowEngine
from app.core.deployment_engine import DeploymentEngine


# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for application startup and shutdown"""
    print("🚀 Starting iTechSmart Forge...")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Initialize integrations
    try:
        from app.integrations.hub_integration import hub_client
        from app.integrations.ninja_integration import ninja_client
        
        await hub_client.initialize()
        await ninja_client.initialize()
        print("✅ Suite integrations initialized")
    except Exception as e:
        print(f"⚠️  Suite integrations not available: {e}")
    
    print("✅ iTechSmart Forge is ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down iTechSmart Forge...")
    
    try:
        from app.integrations.hub_integration import hub_client
        from app.integrations.ninja_integration import ninja_client
        
        await hub_client.shutdown()
        await ninja_client.shutdown()
    except Exception as e:
        print(f"⚠️  Error during shutdown: {e}")
    
    print("👋 iTechSmart Forge stopped")


# Create FastAPI app
app = FastAPI(
    title="iTechSmart Forge",
    description="""
    **Low-Code/No-Code Application Builder with AI**
    
    Build custom applications without coding:
    
    - 🎨 **Visual App Builder**: Drag-and-drop UI components
    - 🤖 **AI-Powered Generation**: Generate apps from natural language
    - 🔌 **Data Connectors**: Connect to all iTechSmart products and external sources
    - ⚡ **Workflow Automation**: Visual workflow builder with triggers
    - 🚀 **One-Click Deployment**: Deploy to production instantly
    - 🏪 **App Marketplace**: Share and monetize your apps
    
    **Part of the iTechSmart Suite** - Product #32
    """,
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


# Pydantic models
class CreateAppRequest(BaseModel):
    name: str
    description: Optional[str] = None
    template_id: Optional[int] = None


class AddPageRequest(BaseModel):
    name: str
    slug: Optional[str] = None
    title: Optional[str] = None


class AddComponentRequest(BaseModel):
    component_type: str
    props: dict
    position: dict


class AIGenerateAppRequest(BaseModel):
    prompt: str
    context: Optional[dict] = None


class CreateDataSourceRequest(BaseModel):
    name: str
    source_type: str
    connection_config: dict


class CreateWorkflowRequest(BaseModel):
    name: str
    trigger_type: str
    trigger_config: dict
    steps: List[dict]


class DeployAppRequest(BaseModel):
    environment: str = "production"
    build_config: Optional[dict] = None


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "iTechSmart Forge",
        "version": "1.0.0",
        "description": "Low-Code/No-Code Application Builder with AI",
        "status": "operational",
        "suite": "iTechSmart Suite",
        "product_number": 32,
        "capabilities": [
            "Visual App Builder",
            "AI-Powered Generation",
            "Data Connectors",
            "Workflow Automation",
            "One-Click Deployment",
            "App Marketplace"
        ],
        "endpoints": {
            "apps": "/api/apps",
            "ai": "/api/ai",
            "data_sources": "/api/data-sources",
            "workflows": "/api/workflows",
            "deployments": "/api/deployments",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iTechSmart Forge",
        "version": "1.0.0"
    }


# App Builder API
@app.post("/api/apps")
async def create_app(
    request: CreateAppRequest,
    user_id: int = Query(1),  # Mock user ID
    db: Session = Depends(get_db)
):
    """Create a new application"""
    engine = AppBuilderEngine(db)
    app = await engine.create_app(user_id, request.name, request.description, request.template_id)
    return {"id": app.id, "name": app.name, "slug": app.slug}


@app.get("/api/apps")
async def get_user_apps(
    user_id: int = Query(1),
    status: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get user's applications"""
    engine = AppBuilderEngine(db)
    apps = await engine.get_user_apps(user_id, status, limit, offset)
    return {"apps": apps, "count": len(apps)}


@app.get("/api/apps/{app_id}")
async def get_app_structure(
    app_id: int,
    db: Session = Depends(get_db)
):
    """Get complete app structure"""
    engine = AppBuilderEngine(db)
    structure = await engine.get_app_structure(app_id)
    return structure


@app.post("/api/apps/{app_id}/pages")
async def add_page(
    app_id: int,
    request: AddPageRequest,
    db: Session = Depends(get_db)
):
    """Add a page to an app"""
    engine = AppBuilderEngine(db)
    page = await engine.add_page(app_id, request.name, request.slug, request.title)
    return {"id": page.id, "name": page.name, "slug": page.slug}


@app.post("/api/apps/{app_id}/pages/{page_id}/components")
async def add_component(
    app_id: int,
    page_id: int,
    request: AddComponentRequest,
    db: Session = Depends(get_db)
):
    """Add a component to a page"""
    engine = AppBuilderEngine(db)
    component = await engine.add_component_to_page(
        page_id,
        request.component_type,
        request.props,
        request.position
    )
    return component


@app.post("/api/apps/{app_id}/publish")
async def publish_app(
    app_id: int,
    db: Session = Depends(get_db)
):
    """Publish an app"""
    engine = AppBuilderEngine(db)
    app = await engine.publish_app(app_id)
    return {"id": app.id, "status": app.status, "published_at": app.published_at.isoformat()}


@app.post("/api/apps/{app_id}/clone")
async def clone_app(
    app_id: int,
    user_id: int = Query(1),
    new_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Clone an existing app"""
    engine = AppBuilderEngine(db)
    new_app = await engine.clone_app(app_id, user_id, new_name)
    return {"id": new_app.id, "name": new_app.name, "slug": new_app.slug}


# AI API
@app.post("/api/ai/generate-app")
async def generate_app_from_prompt(
    request: AIGenerateAppRequest,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Generate app from natural language prompt"""
    engine = AIEngine(db)
    app_config = await engine.generate_app_from_prompt(user_id, request.prompt, request.context)
    return app_config


@app.post("/api/ai/generate-component")
async def generate_component_from_prompt(
    request: AIGenerateAppRequest,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Generate component from natural language prompt"""
    engine = AIEngine(db)
    component_config = await engine.generate_component_from_prompt(user_id, request.prompt, request.context)
    return component_config


@app.post("/api/ai/generate-query")
async def generate_query_from_nl(
    natural_language: str,
    data_source_type: str,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Generate database query from natural language"""
    engine = AIEngine(db)
    query_config = await engine.generate_query_from_nl(user_id, natural_language, data_source_type)
    return query_config


# Data Sources API
@app.post("/api/data-sources")
async def create_data_source(
    app_id: int,
    request: CreateDataSourceRequest,
    db: Session = Depends(get_db)
):
    """Create a new data source"""
    engine = DataConnectorEngine(db)
    data_source = await engine.create_data_source(
        app_id,
        request.name,
        request.source_type,
        request.connection_config
    )
    return {"id": data_source.id, "name": data_source.name}


@app.post("/api/data-sources/{data_source_id}/test")
async def test_data_source(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    """Test data source connection"""
    engine = DataConnectorEngine(db)
    result = await engine.test_connection(data_source_id)
    return result


@app.get("/api/data-sources/itechsmart-products")
async def get_itechsmart_products(
    db: Session = Depends(get_db)
):
    """Get list of available iTechSmart products"""
    engine = DataConnectorEngine(db)
    products = await engine.get_available_itechsmart_products()
    return {"products": products, "count": len(products)}


# Workflows API
@app.post("/api/workflows")
async def create_workflow(
    app_id: int,
    request: CreateWorkflowRequest,
    db: Session = Depends(get_db)
):
    """Create a new workflow"""
    engine = WorkflowEngine(db)
    workflow = await engine.create_workflow(
        app_id,
        request.name,
        request.trigger_type,
        request.trigger_config,
        request.steps
    )
    return {"id": workflow.id, "name": workflow.name}


@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: int,
    input_data: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Execute a workflow"""
    engine = WorkflowEngine(db)
    execution = await engine.execute_workflow(workflow_id, input_data)
    return {
        "id": execution.id,
        "status": execution.status,
        "duration_ms": execution.duration_ms,
        "output_data": execution.output_data
    }


# Deployments API
@app.post("/api/deployments")
async def deploy_app(
    app_id: int,
    request: DeployAppRequest,
    db: Session = Depends(get_db)
):
    """Deploy an app to production"""
    engine = DeploymentEngine(db)
    deployment = await engine.deploy_app(app_id, request.environment, request.build_config)
    return {
        "id": deployment.id,
        "status": deployment.status,
        "deployment_url": deployment.deployment_url,
        "preview_url": deployment.preview_url
    }


@app.get("/api/deployments/{deployment_id}")
async def get_deployment(
    deployment_id: int,
    db: Session = Depends(get_db)
):
    """Get deployment details"""
    from app.models.models import Deployment
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return {
        "id": deployment.id,
        "app_id": deployment.app_id,
        "version": deployment.version,
        "environment": deployment.environment,
        "status": deployment.status,
        "deployment_url": deployment.deployment_url,
        "deployed_at": deployment.deployed_at.isoformat() if deployment.deployed_at else None
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8320"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )