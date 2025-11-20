from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.logging import setup_logging
from app.services.workflow_generator import WorkflowGenerator
from app.services.workflow_executor import WorkflowExecutor
from app.services.service_discovery import ServiceDiscovery
from app.models.schemas import (
    WorkflowGenerationRequest,
    WorkflowGenerationResponse,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    ServiceDiscoveryResponse
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global services
workflow_generator = None
workflow_executor = None
service_discovery = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("🤖 iTechSmart Generative Workflow starting up...")
    global workflow_generator, workflow_executor, service_discovery
    
    try:
        service_discovery = ServiceDiscovery()
        workflow_generator = WorkflowGenerator(service_discovery)
        workflow_executor = WorkflowExecutor(service_discovery)
        
        await service_discovery.initialize()
        await workflow_generator.initialize()
        await workflow_executor.initialize()
        
        logger.info("✅ iTechSmart Generative Workflow ready for workflow generation")
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Generative Workflow: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("🔄 iTechSmart Generative Workflow shutting down...")
        if workflow_executor:
            await workflow_executor.cleanup()
        if workflow_generator:
            await workflow_generator.cleanup()
        if service_discovery:
            await service_discovery.cleanup()
        logger.info("👋 iTechSmart Generative Workflow shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="iTechSmart Generative Workflow",
    description="Text-to-Workflow Engine",
    version="1.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "iTechSmart Generative Workflow",
        "version": "1.6.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "description": "Text-to-Workflow Engine"
    }

@app.get("/api/v1/status")
async def get_status():
    """Get system status"""
    return {
        "status": "healthy",
        "workflow_generator": await workflow_generator.health_check(),
        "workflow_executor": await workflow_executor.health_check(),
        "service_discovery": await service_discovery.health_check(),
        "active_workflows": await workflow_executor.get_active_count(),
        "available_services": await service_discovery.get_service_count(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/generate", response_model=WorkflowGenerationResponse)
async def generate_workflow(request: WorkflowGenerationRequest):
    """
    Generate a workflow from natural language description
    """
    try:
        logger.info(f"🤖 Generating workflow from: {request.description[:100]}...")
        
        # Generate workflow
        workflow = await workflow_generator.generate_from_text(
            description=request.description,
            context=request.context or {},
            refine=request.refine or False
        )
        
        logger.info(f"✅ Workflow generated: {workflow['id']}")
        return WorkflowGenerationResponse(**workflow)
        
    except Exception as e:
        logger.error(f"❌ Error generating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow generation failed: {str(e)}")

@app.post("/api/v1/refine", response_model=WorkflowGenerationResponse)
async def refine_workflow(
    workflow_id: str,
    feedback: str,
    context: Optional[Dict[str, Any]] = None
):
    """
    Refine an existing workflow based on user feedback
    """
    try:
        logger.info(f"🔧 Refining workflow {workflow_id} with feedback: {feedback[:50]}...")
        
        refined_workflow = await workflow_generator.refine_workflow(
            workflow_id=workflow_id,
            feedback=feedback,
            context=context or {}
        )
        
        logger.info(f"✅ Workflow refined: {refined_workflow['id']}")
        return WorkflowGenerationResponse(**refined_workflow)
        
    except Exception as e:
        logger.error(f"❌ Error refining workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow refinement failed: {str(e)}")

@app.get("/api/v1/templates")
async def get_templates(category: Optional[str] = None):
    """
    Get available workflow templates
    """
    try:
        templates = await workflow_generator.get_templates(category=category)
        return {
            "templates": templates,
            "total": len(templates),
            "category": category
        }
    except Exception as e:
        logger.error(f"❌ Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve templates")

@app.post("/api/v1/workflows", response_model=WorkflowGenerationResponse)
async def create_workflow(workflow_data: Dict[str, Any]):
    """
    Create a new workflow from structured data
    """
    try:
        logger.info(f"📝 Creating structured workflow: {workflow_data.get('name', 'Unknown')}")
        
        workflow = await workflow_generator.create_workflow(workflow_data)
        
        logger.info(f"✅ Workflow created: {workflow['id']}")
        return WorkflowGenerationResponse(**workflow)
        
    except Exception as e:
        logger.error(f"❌ Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow creation failed: {str(e)}")

@app.get("/api/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details"""
    try:
        workflow = await workflow_generator.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return workflow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve workflow: {str(e)}")

@app.put("/api/v1/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, workflow_data: Dict[str, Any]):
    """Update workflow"""
    try:
        logger.info(f"🔄 Updating workflow {workflow_id}")
        
        updated_workflow = await workflow_generator.update_workflow(
            workflow_id=workflow_id,
            workflow_data=workflow_data
        )
        
        logger.info(f"✅ Workflow updated: {workflow_id}")
        return updated_workflow
        
    except Exception as e:
        logger.error(f"❌ Error updating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow update failed: {str(e)}")

@app.delete("/api/v1/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete workflow"""
    try:
        logger.info(f"🗑️ Deleting workflow {workflow_id}")
        
        await workflow_generator.delete_workflow(workflow_id)
        
        return {
            "status": "deleted",
            "workflow_id": workflow_id,
            "message": "Workflow deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error deleting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow deletion failed: {str(e)}")

@app.post("/api/v1/workflows/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a workflow
    """
    try:
        logger.info(f"🚀 Executing workflow {workflow_id}")
        
        # Start execution in background
        execution_id = await workflow_executor.start_execution(
            workflow_id=workflow_id,
            input_data=request.input_data or {},
            options=request.options or {}
        )
        
        # Add background task to monitor execution
        background_tasks.add_task(monitor_execution, execution_id)
        
        logger.info(f"✅ Workflow execution started: {execution_id}")
        return WorkflowExecutionResponse(
            execution_id=execution_id,
            status="running",
            started_at=datetime.utcnow(),
            message="Workflow execution started successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting workflow execution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start workflow execution: {str(e)}")

async def monitor_execution(execution_id: str):
    """Monitor workflow execution in background"""
    try:
        async for update in workflow_executor.monitor_execution(execution_id):
            # Send updates via WebSocket or other notification mechanism
            logger.info(f"📊 Execution {execution_id} update: {update['status']}")
            
            if update['status'] in ['completed', 'failed', 'cancelled']:
                break
                
    except Exception as e:
        logger.error(f"❌ Error monitoring execution {execution_id}: {str(e)}")

@app.get("/api/v1/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get workflow execution status"""
    try:
        status = await workflow_executor.get_execution_status(workflow_id)
        return status
        
    except Exception as e:
        logger.error(f"❌ Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@app.post("/api/v1/workflows/{workflow_id}/pause")
async def pause_workflow(workflow_id: str):
    """Pause workflow execution"""
    try:
        logger.info(f"⏸️ Pausing workflow {workflow_id}")
        
        await workflow_executor.pause_execution(workflow_id)
        
        return {
            "status": "paused",
            "workflow_id": workflow_id,
            "message": "Workflow paused successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error pausing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to pause workflow: {str(e)}")

@app.post("/api/v1/workflows/{workflow_id}/resume")
async def resume_workflow(workflow_id: str):
    """Resume workflow execution"""
    try:
        logger.info(f"▶️ Resuming workflow {workflow_id}")
        
        await workflow_executor.resume_execution(workflow_id)
        
        return {
            "status": "resumed",
            "workflow_id": workflow_id,
            "message": "Workflow resumed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error resuming workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resume workflow: {str(e)}")

@app.get("/api/v1/services", response_model=ServiceDiscoveryResponse)
async def get_services(refresh: bool = False):
    """
    Get discovered iTechSmart services
    """
    try:
        if refresh:
            await service_discovery.refresh_services()
        
        services = await service_discovery.get_services()
        
        return ServiceDiscoveryResponse(
            services=services,
            total=len(services),
            last_updated=service_discovery.last_updated
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting services: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve services")

@app.get("/api/v1/services/{service_id}")
async def get_service_details(service_id: str):
    """Get detailed information about a specific service"""
    try:
        service = await service_discovery.get_service(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return service
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting service details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve service details: {str(e)}")

@app.post("/api/v1/services/discover")
async def discover_services(background_tasks: BackgroundTasks):
    """
    Trigger service discovery
    """
    try:
        logger.info("🔍 Starting service discovery...")
        
        # Run discovery in background
        background_tasks.add_task(service_discovery.full_discovery)
        
        return {
            "status": "started",
            "message": "Service discovery started in background"
        }
        
    except Exception as e:
        logger.error(f"❌ Error starting service discovery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start service discovery")

@app.get("/api/v1/analytics")
async def get_analytics(
    days: int = 30,
    workflow_id: Optional[str] = None
):
    """
    Get workflow analytics and metrics
    """
    try:
        analytics = await workflow_generator.get_analytics(
            days=days,
            workflow_id=workflow_id
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"❌ Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

# Include API router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8100,
        reload=settings.DEBUG,
        log_level="info"
    )