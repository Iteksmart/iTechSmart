"""
iTechSmart Enterprise - Service Catalog Engine
Self-service portal with ITIL alignment
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4

from ..models.service_catalog import (
    ServiceCatalogItem, ServiceRequest, ServiceApproval, FulfillmentTask,
    ServiceSLA, ServiceCostCenter, RequestWorkflow, RequestComment,
    RequestAttachment, ServiceMetrics, ServiceCategory, RequestStatus,
    RequestPriority, ApprovalStatus, FulfillmentStatus
)


class ServiceCatalogEngine:
    """
    Service catalog management engine with ITIL alignment
    """
    
    def __init__(self):
        self.catalog_items: Dict[str, ServiceCatalogItem] = {}
        self.requests: Dict[str, ServiceRequest] = {}
        self.approvals: Dict[str, ServiceApproval] = {}
        self.fulfillment_tasks: Dict[str, FulfillmentTask] = {}
        self.slas: Dict[str, ServiceSLA] = {}
        self.cost_centers: Dict[str, ServiceCostCenter] = {}
        self.workflows: Dict[str, RequestWorkflow] = {}
        self.comments: Dict[str, RequestComment] = {}
        self.attachments: Dict[str, RequestAttachment] = {}
        self.metrics: Dict[str, ServiceMetrics] = {}
        
        # Initialize default data
        self._initialize_default_sla()
        self._initialize_sample_services()
    
    # ========================================================================
    # INITIALIZATION
    # ========================================================================
    
    def _initialize_default_sla(self):
        """Initialize default SLA"""
        sla = ServiceSLA(
            sla_id="sla_default",
            name="Standard SLA",
            description="Default service level agreement"
        )
        self.slas[sla.sla_id] = sla
    
    def _initialize_sample_services(self):
        """Initialize sample service catalog items"""
        services = [
            {
                "name": "New User Account",
                "description": "Request a new user account for employee or contractor",
                "category": ServiceCategory.ACCESS_REQUEST,
                "cost": 0.0,
                "estimated_delivery_days": 1
            },
            {
                "name": "Software License",
                "description": "Request software license for approved applications",
                "category": ServiceCategory.SOFTWARE,
                "cost": 100.0,
                "estimated_delivery_days": 2
            },
            {
                "name": "Laptop Request",
                "description": "Request new laptop or workstation",
                "category": ServiceCategory.HARDWARE,
                "cost": 1500.0,
                "estimated_delivery_days": 5
            },
            {
                "name": "VPN Access",
                "description": "Request VPN access for remote work",
                "category": ServiceCategory.ACCESS_REQUEST,
                "cost": 0.0,
                "estimated_delivery_days": 1
            },
            {
                "name": "Cloud Resources",
                "description": "Request cloud infrastructure resources",
                "category": ServiceCategory.INFRASTRUCTURE,
                "cost": 500.0,
                "estimated_delivery_days": 3
            }
        ]
        
        for service_data in services:
            item_id = f"item_{uuid4().hex[:12]}"
            item = ServiceCatalogItem(
                item_id=item_id,
                name=service_data["name"],
                description=service_data["description"],
                category=service_data["category"],
                owner="service_admin"
            )
            item.cost = service_data["cost"]
            item.estimated_delivery_days = service_data["estimated_delivery_days"]
            item.sla_id = "sla_default"
            self.catalog_items[item_id] = item
    
    # ========================================================================
    # CATALOG ITEM MANAGEMENT
    # ========================================================================
    
    def create_catalog_item(
        self,
        name: str,
        description: str,
        category: ServiceCategory,
        owner: str,
        user: str
    ) -> Dict[str, Any]:
        """Create new catalog item"""
        item_id = f"item_{uuid4().hex[:12]}"
        item = ServiceCatalogItem(
            item_id=item_id,
            name=name,
            description=description,
            category=category,
            owner=owner
        )
        item.created_by = user
        item.sla_id = "sla_default"
        
        self.catalog_items[item_id] = item
        
        return {
            "success": True,
            "item_id": item_id,
            "name": name
        }
    
    def get_catalog_items(
        self,
        category: Optional[ServiceCategory] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get catalog items with filters"""
        items = list(self.catalog_items.values())
        
        if category:
            items = [i for i in items if i.category == category]
        if is_active is not None:
            items = [i for i in items if i.is_active == is_active]
        if search:
            search_lower = search.lower()
            items = [
                i for i in items
                if search_lower in i.name.lower() or search_lower in i.description.lower()
            ]
        
        return [
            {
                "item_id": i.item_id,
                "name": i.name,
                "description": i.description,
                "short_description": i.short_description,
                "category": i.category.value,
                "icon": i.icon,
                "cost": i.cost,
                "estimated_delivery_days": i.estimated_delivery_days,
                "requires_approval": i.requires_approval,
                "is_active": i.is_active,
                "request_count": i.request_count,
                "satisfaction_score": i.satisfaction_score
            }
            for i in items
        ]
    
    def update_catalog_item(
        self,
        item_id: str,
        updates: Dict[str, Any],
        user: str
    ) -> Dict[str, Any]:
        """Update catalog item"""
        if item_id not in self.catalog_items:
            return {"success": False, "error": "Item not found"}
        
        item = self.catalog_items[item_id]
        
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        item.updated_by = user
        
        return {"success": True, "item_id": item_id}
    
    # ========================================================================
    # SERVICE REQUEST MANAGEMENT
    # ========================================================================
    
    def create_request(
        self,
        item_id: str,
        requester_id: str,
        requester_name: str,
        requester_email: str,
        form_data: Dict[str, Any],
        priority: RequestPriority = RequestPriority.MEDIUM
    ) -> Dict[str, Any]:
        """Create new service request"""
        if item_id not in self.catalog_items:
            return {"success": False, "error": "Catalog item not found"}
        
        item = self.catalog_items[item_id]
        request_id = f"req_{uuid4().hex[:12]}"
        
        request = ServiceRequest(
            request_id=request_id,
            item_id=item_id,
            requester_id=requester_id,
            requester_name=requester_name,
            requester_email=requester_email
        )
        request.title = f"{item.name} - {requester_name}"
        request.priority = priority
        request.form_data = form_data
        request.estimated_cost = item.cost
        request.status = RequestStatus.DRAFT
        
        # Set due date based on SLA
        if item.sla_id and item.sla_id in self.slas:
            sla = self.slas[item.sla_id]
            hours = self._get_sla_resolution_time(sla, priority)
            request.due_date = datetime.utcnow() + timedelta(hours=hours)
        
        self.requests[request_id] = request
        
        return {
            "success": True,
            "request_id": request_id,
            "status": request.status.value
        }
    
    def submit_request(self, request_id: str) -> Dict[str, Any]:
        """Submit request for approval"""
        if request_id not in self.requests:
            return {"success": False, "error": "Request not found"}
        
        request = self.requests[request_id]
        item = self.catalog_items.get(request.item_id)
        
        if not item:
            return {"success": False, "error": "Catalog item not found"}
        
        request.status = RequestStatus.SUBMITTED
        request.submitted_at = datetime.utcnow()
        
        # Create approval chain if required
        if item.requires_approval and item.approval_chain:
            request.status = RequestStatus.PENDING_APPROVAL
            self._create_approval_chain(request_id, item.approval_chain)
        else:
            # Auto-approve if no approval required
            request.status = RequestStatus.APPROVED
            request.approved_at = datetime.utcnow()
            self._start_fulfillment(request_id)
        
        # Update item request count
        item.request_count += 1
        
        return {
            "success": True,
            "request_id": request_id,
            "status": request.status.value
        }
    
    def _create_approval_chain(self, request_id: str, approvers: List[str]):
        """Create approval chain for request"""
        for sequence, approver_id in enumerate(approvers, 1):
            approval_id = f"appr_{uuid4().hex[:12]}"
            approval = ServiceApproval(
                approval_id=approval_id,
                request_id=request_id,
                approver_id=approver_id,
                approver_name=f"Approver {sequence}",
                sequence=sequence
            )
            approval.due_date = datetime.utcnow() + timedelta(days=2)
            self.approvals[approval_id] = approval
    
    def approve_request(
        self,
        approval_id: str,
        approver_id: str,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve service request"""
        if approval_id not in self.approvals:
            return {"success": False, "error": "Approval not found"}
        
        approval = self.approvals[approval_id]
        
        if approval.approver_id != approver_id:
            return {"success": False, "error": "Not authorized"}
        
        approval.status = ApprovalStatus.APPROVED
        approval.decision = "approved"
        approval.comments = comments
        approval.decided_at = datetime.utcnow()
        
        # Check if all approvals are complete
        request_id = approval.request_id
        request_approvals = [
            a for a in self.approvals.values()
            if a.request_id == request_id
        ]
        
        all_approved = all(
            a.status == ApprovalStatus.APPROVED
            for a in request_approvals
        )
        
        if all_approved:
            request = self.requests[request_id]
            request.status = RequestStatus.APPROVED
            request.approved_at = datetime.utcnow()
            self._start_fulfillment(request_id)
        
        return {
            "success": True,
            "approval_id": approval_id,
            "all_approved": all_approved
        }
    
    def reject_request(
        self,
        approval_id: str,
        approver_id: str,
        comments: str
    ) -> Dict[str, Any]:
        """Reject service request"""
        if approval_id not in self.approvals:
            return {"success": False, "error": "Approval not found"}
        
        approval = self.approvals[approval_id]
        
        if approval.approver_id != approver_id:
            return {"success": False, "error": "Not authorized"}
        
        approval.status = ApprovalStatus.REJECTED
        approval.decision = "rejected"
        approval.comments = comments
        approval.decided_at = datetime.utcnow()
        
        # Reject the request
        request = self.requests[approval.request_id]
        request.status = RequestStatus.REJECTED
        
        return {
            "success": True,
            "approval_id": approval_id,
            "request_id": approval.request_id
        }
    
    # ========================================================================
    # FULFILLMENT MANAGEMENT
    # ========================================================================
    
    def _start_fulfillment(self, request_id: str):
        """Start fulfillment process"""
        request = self.requests[request_id]
        request.status = RequestStatus.IN_PROGRESS
        
        # Create default fulfillment task
        task_id = f"task_{uuid4().hex[:12]}"
        task = FulfillmentTask(
            task_id=task_id,
            request_id=request_id,
            title=f"Fulfill: {request.title}",
            assigned_to=request.assigned_to or "fulfillment_team"
        )
        task.status = FulfillmentStatus.PENDING
        self.fulfillment_tasks[task_id] = task
    
    def assign_request(
        self,
        request_id: str,
        assigned_to: str,
        assigned_group: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assign request to user or group"""
        if request_id not in self.requests:
            return {"success": False, "error": "Request not found"}
        
        request = self.requests[request_id]
        request.assigned_to = assigned_to
        request.assigned_group = assigned_group
        request.updated_at = datetime.utcnow()
        
        return {
            "success": True,
            "request_id": request_id,
            "assigned_to": assigned_to
        }
    
    def complete_fulfillment_task(
        self,
        task_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete fulfillment task"""
        if task_id not in self.fulfillment_tasks:
            return {"success": False, "error": "Task not found"}
        
        task = self.fulfillment_tasks[task_id]
        task.status = FulfillmentStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.notes = notes
        
        # Check if all tasks for request are complete
        request_id = task.request_id
        request_tasks = [
            t for t in self.fulfillment_tasks.values()
            if t.request_id == request_id
        ]
        
        all_complete = all(
            t.status == FulfillmentStatus.COMPLETED
            for t in request_tasks
        )
        
        if all_complete:
            request = self.requests[request_id]
            request.status = RequestStatus.FULFILLED
            request.fulfilled_at = datetime.utcnow()
        
        return {
            "success": True,
            "task_id": task_id,
            "all_complete": all_complete
        }
    
    def close_request(
        self,
        request_id: str,
        satisfaction_rating: Optional[int] = None,
        satisfaction_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close service request"""
        if request_id not in self.requests:
            return {"success": False, "error": "Request not found"}
        
        request = self.requests[request_id]
        request.status = RequestStatus.CLOSED
        request.closed_at = datetime.utcnow()
        request.satisfaction_rating = satisfaction_rating
        request.satisfaction_comment = satisfaction_comment
        
        # Update item metrics
        item = self.catalog_items.get(request.item_id)
        if item and satisfaction_rating:
            if item.satisfaction_score:
                item.satisfaction_score = (
                    item.satisfaction_score * 0.9 + satisfaction_rating * 0.1
                )
            else:
                item.satisfaction_score = float(satisfaction_rating)
        
        return {
            "success": True,
            "request_id": request_id
        }
    
    # ========================================================================
    # REQUEST QUERIES
    # ========================================================================
    
    def get_my_requests(
        self,
        requester_id: str,
        status: Optional[RequestStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get requests for a user"""
        requests = [
            r for r in self.requests.values()
            if r.requester_id == requester_id
        ]
        
        if status:
            requests = [r for r in requests if r.status == status]
        
        return [
            {
                "request_id": r.request_id,
                "title": r.title,
                "status": r.status.value,
                "priority": r.priority.value,
                "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
                "due_date": r.due_date.isoformat() if r.due_date else None,
                "item_name": self.catalog_items.get(r.item_id).name if r.item_id in self.catalog_items else None
            }
            for r in requests
        ]
    
    def get_pending_approvals(self, approver_id: str) -> List[Dict[str, Any]]:
        """Get pending approvals for user"""
        approvals = [
            a for a in self.approvals.values()
            if a.approver_id == approver_id and a.status == ApprovalStatus.PENDING
        ]
        
        return [
            {
                "approval_id": a.approval_id,
                "request_id": a.request_id,
                "request_title": self.requests.get(a.request_id).title if a.request_id in self.requests else None,
                "sequence": a.sequence,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "created_at": a.created_at.isoformat()
            }
            for a in approvals
        ]
    
    def get_assigned_requests(
        self,
        assigned_to: str,
        status: Optional[RequestStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get requests assigned to user"""
        requests = [
            r for r in self.requests.values()
            if r.assigned_to == assigned_to
        ]
        
        if status:
            requests = [r for r in requests if r.status == status]
        
        return [
            {
                "request_id": r.request_id,
                "title": r.title,
                "status": r.status.value,
                "priority": r.priority.value,
                "requester_name": r.requester_name,
                "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
                "due_date": r.due_date.isoformat() if r.due_date else None
            }
            for r in requests
        ]
    
    # ========================================================================
    # COMMENTS & ATTACHMENTS
    # ========================================================================
    
    def add_comment(
        self,
        request_id: str,
        user_id: str,
        user_name: str,
        comment: str,
        is_internal: bool = False
    ) -> Dict[str, Any]:
        """Add comment to request"""
        if request_id not in self.requests:
            return {"success": False, "error": "Request not found"}
        
        comment_id = f"comment_{uuid4().hex[:12]}"
        comment_obj = RequestComment(
            comment_id=comment_id,
            request_id=request_id,
            user_id=user_id,
            user_name=user_name,
            comment=comment
        )
        comment_obj.is_internal = is_internal
        
        self.comments[comment_id] = comment_obj
        
        return {"success": True, "comment_id": comment_id}
    
    def add_attachment(
        self,
        request_id: str,
        filename: str,
        file_path: str,
        uploaded_by: str
    ) -> Dict[str, Any]:
        """Add attachment to request"""
        if request_id not in self.requests:
            return {"success": False, "error": "Request not found"}
        
        attachment_id = f"attach_{uuid4().hex[:12]}"
        attachment = RequestAttachment(
            attachment_id=attachment_id,
            request_id=request_id,
            filename=filename,
            file_path=file_path,
            uploaded_by=uploaded_by
        )
        
        self.attachments[attachment_id] = attachment
        
        return {"success": True, "attachment_id": attachment_id}
    
    # ========================================================================
    # SLA & METRICS
    # ========================================================================
    
    def _get_sla_resolution_time(self, sla: ServiceSLA, priority: RequestPriority) -> int:
        """Get SLA resolution time based on priority"""
        if priority == RequestPriority.CRITICAL:
            return sla.resolution_time_critical or 8
        elif priority == RequestPriority.HIGH:
            return sla.resolution_time_high or 24
        elif priority == RequestPriority.MEDIUM:
            return sla.resolution_time_medium or 48
        else:
            return sla.resolution_time_low or 120
    
    def calculate_metrics(
        self,
        item_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Calculate metrics for catalog item"""
        requests = [
            r for r in self.requests.values()
            if r.item_id == item_id and
            r.created_at >= period_start and
            r.created_at <= period_end
        ]
        
        total = len(requests)
        fulfilled = len([r for r in requests if r.status == RequestStatus.FULFILLED])
        rejected = len([r for r in requests if r.status == RequestStatus.REJECTED])
        cancelled = len([r for r in requests if r.status == RequestStatus.CANCELLED])
        
        # Calculate average fulfillment time
        fulfilled_requests = [
            r for r in requests
            if r.fulfilled_at and r.submitted_at
        ]
        avg_fulfillment = None
        if fulfilled_requests:
            times = [
                (r.fulfilled_at - r.submitted_at).total_seconds() / 3600
                for r in fulfilled_requests
            ]
            avg_fulfillment = sum(times) / len(times)
        
        # Calculate satisfaction score
        rated_requests = [r for r in requests if r.satisfaction_rating]
        avg_satisfaction = None
        if rated_requests:
            avg_satisfaction = sum(r.satisfaction_rating for r in rated_requests) / len(rated_requests)
        
        return {
            "item_id": item_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "total_requests": total,
            "fulfilled_requests": fulfilled,
            "rejected_requests": rejected,
            "cancelled_requests": cancelled,
            "fulfillment_rate": (fulfilled / total * 100) if total > 0 else 0,
            "average_fulfillment_time_hours": avg_fulfillment,
            "average_satisfaction_score": avg_satisfaction
        }
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get overall dashboard metrics"""
        total_requests = len(self.requests)
        pending_approvals = len([
            a for a in self.approvals.values()
            if a.status == ApprovalStatus.PENDING
        ])
        in_progress = len([
            r for r in self.requests.values()
            if r.status == RequestStatus.IN_PROGRESS
        ])
        fulfilled_today = len([
            r for r in self.requests.values()
            if r.fulfilled_at and
            r.fulfilled_at.date() == datetime.utcnow().date()
        ])
        
        return {
            "total_requests": total_requests,
            "pending_approvals": pending_approvals,
            "in_progress": in_progress,
            "fulfilled_today": fulfilled_today,
            "catalog_items": len(self.catalog_items),
            "active_items": len([i for i in self.catalog_items.values() if i.is_active])
        }