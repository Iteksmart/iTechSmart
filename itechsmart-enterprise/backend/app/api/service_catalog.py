"""
iTechSmart Enterprise - Service Catalog API
Self-service portal endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..core.service_catalog_engine import ServiceCatalogEngine
from ..models.service_catalog import (
    ServiceCategory, RequestStatus, RequestPriority
)

router = APIRouter(prefix="/service-catalog", tags=["Service Catalog"])
engine = ServiceCatalogEngine()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CatalogItemCreate(BaseModel):
    name: str
    description: str
    category: ServiceCategory
    short_description: Optional[str] = None
    cost: float = 0.0
    estimated_delivery_days: Optional[int] = None
    requires_approval: bool = True


class CatalogItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    cost: Optional[float] = None
    estimated_delivery_days: Optional[int] = None
    is_active: Optional[bool] = None


class ServiceRequestCreate(BaseModel):
    item_id: str
    form_data: dict
    priority: RequestPriority = RequestPriority.MEDIUM
    justification: Optional[str] = None
    requested_for: Optional[str] = None


class ApprovalDecision(BaseModel):
    comments: Optional[str] = None


class RequestAssignment(BaseModel):
    assigned_to: str
    assigned_group: Optional[str] = None


class TaskComplete(BaseModel):
    notes: Optional[str] = None


class RequestClose(BaseModel):
    satisfaction_rating: Optional[int] = None
    satisfaction_comment: Optional[str] = None


class CommentCreate(BaseModel):
    comment: str
    is_internal: bool = False


# ============================================================================
# CATALOG ITEM ENDPOINTS
# ============================================================================

@router.get("/catalog")
async def get_catalog(
    category: Optional[ServiceCategory] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get service catalog items"""
    items = engine.get_catalog_items(
        category=category,
        is_active=is_active,
        search=search
    )
    
    return {
        "total": len(items),
        "items": items
    }


@router.get("/catalog/{item_id}")
async def get_catalog_item(item_id: str):
    """Get catalog item details"""
    if item_id not in engine.catalog_items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = engine.catalog_items[item_id]
    
    return {
        "item_id": item.item_id,
        "name": item.name,
        "description": item.description,
        "short_description": item.short_description,
        "category": item.category.value,
        "icon": item.icon,
        "cost": item.cost,
        "estimated_delivery_days": item.estimated_delivery_days,
        "requires_approval": item.requires_approval,
        "auto_fulfill": item.auto_fulfill,
        "is_active": item.is_active,
        "tags": item.tags,
        "form_fields": item.form_fields,
        "request_count": item.request_count,
        "satisfaction_score": item.satisfaction_score,
        "owner": item.owner,
        "support_group": item.support_group
    }


@router.post("/catalog")
async def create_catalog_item(item: CatalogItemCreate):
    """Create new catalog item (admin only)"""
    result = engine.create_catalog_item(
        name=item.name,
        description=item.description,
        category=item.category,
        owner="admin",  # Should come from auth
        user="admin"
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Update additional fields
    if result["success"]:
        updates = {}
        if item.short_description:
            updates["short_description"] = item.short_description
        if item.cost:
            updates["cost"] = item.cost
        if item.estimated_delivery_days:
            updates["estimated_delivery_days"] = item.estimated_delivery_days
        updates["requires_approval"] = item.requires_approval
        
        if updates:
            engine.update_catalog_item(
                result["item_id"],
                updates,
                "admin"
            )
    
    return result


@router.put("/catalog/{item_id}")
async def update_catalog_item(item_id: str, updates: CatalogItemUpdate):
    """Update catalog item (admin only)"""
    update_dict = updates.dict(exclude_unset=True)
    
    result = engine.update_catalog_item(
        item_id=item_id,
        updates=update_dict,
        user="admin"
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# ============================================================================
# SERVICE REQUEST ENDPOINTS
# ============================================================================

@router.post("/requests")
async def create_request(request: ServiceRequestCreate):
    """Create new service request"""
    result = engine.create_request(
        item_id=request.item_id,
        requester_id="user123",  # Should come from auth
        requester_name="John Doe",  # Should come from auth
        requester_email="john.doe@example.com",  # Should come from auth
        form_data=request.form_data,
        priority=request.priority
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/requests/{request_id}/submit")
async def submit_request(request_id: str):
    """Submit request for approval"""
    result = engine.submit_request(request_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/requests/my-requests")
async def get_my_requests(
    status: Optional[RequestStatus] = Query(None)
):
    """Get current user's requests"""
    requests = engine.get_my_requests(
        requester_id="user123",  # Should come from auth
        status=status
    )
    
    return {
        "total": len(requests),
        "requests": requests
    }


@router.get("/requests/{request_id}")
async def get_request(request_id: str):
    """Get request details"""
    if request_id not in engine.requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request = engine.requests[request_id]
    
    # Get approvals
    approvals = [
        {
            "approval_id": a.approval_id,
            "approver_name": a.approver_name,
            "sequence": a.sequence,
            "status": a.status.value,
            "decided_at": a.decided_at.isoformat() if a.decided_at else None,
            "comments": a.comments
        }
        for a in engine.approvals.values()
        if a.request_id == request_id
    ]
    
    # Get comments
    comments = [
        {
            "comment_id": c.comment_id,
            "user_name": c.user_name,
            "comment": c.comment,
            "is_internal": c.is_internal,
            "created_at": c.created_at.isoformat()
        }
        for c in engine.comments.values()
        if c.request_id == request_id
    ]
    
    # Get tasks
    tasks = [
        {
            "task_id": t.task_id,
            "title": t.title,
            "assigned_to": t.assigned_to,
            "status": t.status.value,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None
        }
        for t in engine.fulfillment_tasks.values()
        if t.request_id == request_id
    ]
    
    return {
        "request_id": request.request_id,
        "title": request.title,
        "status": request.status.value,
        "priority": request.priority.value,
        "requester_name": request.requester_name,
        "requester_email": request.requester_email,
        "description": request.description,
        "justification": request.justification,
        "form_data": request.form_data,
        "estimated_cost": request.estimated_cost,
        "submitted_at": request.submitted_at.isoformat() if request.submitted_at else None,
        "approved_at": request.approved_at.isoformat() if request.approved_at else None,
        "fulfilled_at": request.fulfilled_at.isoformat() if request.fulfilled_at else None,
        "due_date": request.due_date.isoformat() if request.due_date else None,
        "assigned_to": request.assigned_to,
        "approvals": approvals,
        "comments": comments,
        "tasks": tasks,
        "created_at": request.created_at.isoformat()
    }


@router.put("/requests/{request_id}/assign")
async def assign_request(request_id: str, assignment: RequestAssignment):
    """Assign request to user or group"""
    result = engine.assign_request(
        request_id=request_id,
        assigned_to=assignment.assigned_to,
        assigned_group=assignment.assigned_group
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/requests/{request_id}/close")
async def close_request(request_id: str, close_data: RequestClose):
    """Close service request"""
    result = engine.close_request(
        request_id=request_id,
        satisfaction_rating=close_data.satisfaction_rating,
        satisfaction_comment=close_data.satisfaction_comment
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# ============================================================================
# APPROVAL ENDPOINTS
# ============================================================================

@router.get("/approvals/pending")
async def get_pending_approvals():
    """Get pending approvals for current user"""
    approvals = engine.get_pending_approvals(
        approver_id="approver123"  # Should come from auth
    )
    
    return {
        "total": len(approvals),
        "approvals": approvals
    }


@router.post("/approvals/{approval_id}/approve")
async def approve_request(approval_id: str, decision: ApprovalDecision):
    """Approve service request"""
    result = engine.approve_request(
        approval_id=approval_id,
        approver_id="approver123",  # Should come from auth
        comments=decision.comments
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/approvals/{approval_id}/reject")
async def reject_request(approval_id: str, decision: ApprovalDecision):
    """Reject service request"""
    if not decision.comments:
        raise HTTPException(status_code=400, detail="Comments required for rejection")
    
    result = engine.reject_request(
        approval_id=approval_id,
        approver_id="approver123",  # Should come from auth
        comments=decision.comments
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# ============================================================================
# FULFILLMENT ENDPOINTS
# ============================================================================

@router.get("/fulfillment/assigned")
async def get_assigned_requests(
    status: Optional[RequestStatus] = Query(None)
):
    """Get requests assigned to current user"""
    requests = engine.get_assigned_requests(
        assigned_to="fulfiller123",  # Should come from auth
        status=status
    )
    
    return {
        "total": len(requests),
        "requests": requests
    }


@router.post("/fulfillment/tasks/{task_id}/complete")
async def complete_task(task_id: str, completion: TaskComplete):
    """Complete fulfillment task"""
    result = engine.complete_fulfillment_task(
        task_id=task_id,
        notes=completion.notes
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# ============================================================================
# COMMENT ENDPOINTS
# ============================================================================

@router.post("/requests/{request_id}/comments")
async def add_comment(request_id: str, comment: CommentCreate):
    """Add comment to request"""
    result = engine.add_comment(
        request_id=request_id,
        user_id="user123",  # Should come from auth
        user_name="John Doe",  # Should come from auth
        comment=comment.comment,
        is_internal=comment.is_internal
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

@router.get("/metrics/dashboard")
async def get_dashboard_metrics():
    """Get dashboard metrics"""
    return engine.get_dashboard_metrics()


@router.get("/metrics/item/{item_id}")
async def get_item_metrics(
    item_id: str,
    days: int = Query(30, ge=1, le=365)
):
    """Get metrics for catalog item"""
    from datetime import timedelta
    
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=days)
    
    return engine.calculate_metrics(
        item_id=item_id,
        period_start=period_start,
        period_end=period_end
    )


# ============================================================================
# CATEGORIES ENDPOINT
# ============================================================================

@router.get("/categories")
async def get_categories():
    """Get available service categories"""
    return {
        "categories": [
            {
                "value": cat.value,
                "label": cat.value.replace("_", " ").title()
            }
            for cat in ServiceCategory
        ]
    }