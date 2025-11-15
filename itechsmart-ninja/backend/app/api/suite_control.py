"""
API endpoints for suite control
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.suite_controller import SuiteController

router = APIRouter(prefix="/api/suite", tags=["suite-control"])


# Pydantic models
class FixRequest(BaseModel):
    service_name: str
    issue_type: str
    auto_apply: bool = False


class UpdateRequest(BaseModel):
    service_name: str
    update_type: str = "patch"


class OptimizeRequest(BaseModel):
    service_name: str
    optimization_type: str = "performance"


class WorkflowRequest(BaseModel):
    workflow_name: str
    services: List[str]
    steps: List[dict]


# Endpoints
@router.post("/register")
async def register_with_hub(db: Session = Depends(get_db)):
    """Register Ninja with Enterprise hub"""
    
    controller = SuiteController(db)
    result = await controller.register_with_hub()
    
    return result


@router.get("/monitor")
async def monitor_suite(db: Session = Depends(get_db)):
    """Monitor health of entire iTechSmart suite"""
    
    controller = SuiteController(db)
    health = await controller.monitor_suite()
    
    return health


@router.post("/fix")
async def fix_service(
    request: FixRequest,
    db: Session = Depends(get_db)
):
    """Fix an issue in a specific service"""
    
    controller = SuiteController(db)
    
    result = await controller.fix_service(
        service_name=request.service_name,
        issue_type=request.issue_type,
        auto_apply=request.auto_apply
    )
    
    return result


@router.post("/update")
async def update_service(
    request: UpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a service to latest version"""
    
    controller = SuiteController(db)
    
    result = await controller.update_service(
        service_name=request.service_name,
        update_type=request.update_type
    )
    
    return result


@router.post("/optimize")
async def optimize_service(
    request: OptimizeRequest,
    db: Session = Depends(get_db)
):
    """Optimize a service"""
    
    controller = SuiteController(db)
    
    result = await controller.optimize_service(
        service_name=request.service_name,
        optimization_type=request.optimization_type
    )
    
    return result


@router.post("/workflow")
async def coordinate_workflow(
    request: WorkflowRequest,
    db: Session = Depends(get_db)
):
    """Coordinate a workflow across multiple services"""
    
    controller = SuiteController(db)
    
    result = await controller.coordinate_workflow(
        workflow_name=request.workflow_name,
        services=request.services,
        steps=request.steps
    )
    
    return result


@router.post("/consistency/check")
async def check_consistency(db: Session = Depends(get_db)):
    """Ensure consistency across all services"""
    
    controller = SuiteController(db)
    result = await controller.ensure_consistency()
    
    return result


@router.post("/update-all")
async def suite_wide_update(
    update_type: str = "patch",
    db: Session = Depends(get_db)
):
    """Update all services in the suite"""
    
    controller = SuiteController(db)
    
    result = await controller.suite_wide_update(update_type)
    
    return result


@router.get("/services")
async def list_services(db: Session = Depends(get_db)):
    """List all services in the suite"""
    
    controller = SuiteController(db)
    
    return {
        "services": controller.services,
        "count": len(controller.services)
    }