"""
iTechSmart Service Catalog API
RESTful endpoints for service catalog management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..service_catalog_engine import ServiceCatalogEngine
from ..service_catalog_models import (
    ServiceItem,
    ServiceRequest,
    RequestApproval,
    ServiceCategory,
    RequestStatus,
    ApprovalStatus,
    AutomationType,
)

router = APIRouter(prefix="/api/service-catalog", tags=["Service Catalog"])


# ==================== Pydantic Models ====================


class ServiceItemCreate(BaseModel):
    name: str
    description: str
    category: ServiceCategory
    icon: Optional[str] = None
    form_schema: dict
    requires_approval: bool = True
    automation_enabled: bool = False
    automation_script: Optional[str] = None
    automation_type: Optional[AutomationType] = None
    ai_assisted: bool = False
    approval_workflow: Optional[List[dict]] = None
    sla_hours: int = 24
    priority: int = 3


class ServiceItemResponse(BaseModel):
    id: int
    name: str
    description: str
    category: ServiceCategory
    icon: Optional[str]
    form_schema: dict
    requires_approval: bool
    automation_enabled: bool
    ai_assisted: bool
    sla_hours: int
    priority: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ServiceRequestCreate(BaseModel):
    service_item_id: int
    form_data: dict


class ServiceRequestResponse(BaseModel):
    id: int
    request_number: str
    service_item_id: int
    requester_name: str
    requester_email: str
    form_data: dict
    status: RequestStatus
    priority: int
    submitted_at: datetime
    due_date: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApprovalDecision(BaseModel):
    decision_notes: Optional[str] = None


# ==================== Service Item Endpoints ====================


@router.get("/categories")
def get_categories():
    """Get all service categories"""
    return {
        "categories": [
            {
                "id": "access_management",
                "name": "🔐 Access Management",
                "description": "User accounts, passwords, and access requests",
                "icon": "🔐",
            },
            {
                "id": "it_support",
                "name": "💻 IT Support",
                "description": "Technical support and troubleshooting",
                "icon": "💻",
            },
            {
                "id": "systems_servers",
                "name": "🖥 Systems & Servers",
                "description": "Server deployment and management",
                "icon": "🖥",
            },
            {
                "id": "devops_automation",
                "name": "🛠 DevOps & Automation",
                "description": "CI/CD, automation, and DevOps tools",
                "icon": "🛠",
            },
            {
                "id": "network_requests",
                "name": "🔧 Network Requests",
                "description": "Firewall, VPN, and network changes",
                "icon": "🔧",
            },
            {
                "id": "software_deployment",
                "name": "📦 Software Deployment",
                "description": "Software installation and updates",
                "icon": "📦",
            },
            {
                "id": "hardware_requests",
                "name": "🧾 Hardware Requests",
                "description": "Hardware procurement and setup",
                "icon": "🧾",
            },
            {
                "id": "hr_onboarding",
                "name": "🧑‍💼 HR / Employee Onboarding",
                "description": "New employee setup and onboarding",
                "icon": "🧑‍💼",
            },
        ]
    }


@router.post("/items", response_model=ServiceItemResponse)
def create_service_item(
    item: ServiceItemCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Get from auth
):
    """Create a new service catalog item"""

    engine = ServiceCatalogEngine(db)

    service_item = engine.create_service_item(
        name=item.name,
        description=item.description,
        category=item.category,
        form_schema=item.form_schema,
        requires_approval=item.requires_approval,
        automation_enabled=item.automation_enabled,
        automation_script=item.automation_script,
        automation_type=item.automation_type,
        ai_assisted=item.ai_assisted,
        approval_workflow=item.approval_workflow,
        sla_hours=item.sla_hours,
        user_id=current_user_id,
    )

    return service_item


@router.get("/items", response_model=List[ServiceItemResponse])
def get_service_items(
    category: Optional[ServiceCategory] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """Get service catalog items"""

    engine = ServiceCatalogEngine(db)
    items = engine.get_service_items_by_category(category, active_only)

    return items


@router.get("/items/{item_id}", response_model=ServiceItemResponse)
def get_service_item(item_id: int, db: Session = Depends(get_db)):
    """Get service item by ID"""

    item = db.query(ServiceItem).filter(ServiceItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service item {item_id} not found",
        )

    return item


# ==================== Service Request Endpoints ====================


@router.post("/requests", response_model=ServiceRequestResponse)
def create_service_request(
    request: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Get from auth
    current_user_email: str = "user@example.com",  # TODO: Get from auth
    current_user_name: str = "Test User",  # TODO: Get from auth
):
    """Create a new service request"""

    engine = ServiceCatalogEngine(db)

    service_request = engine.create_request(
        service_item_id=request.service_item_id,
        requester_id=current_user_id,
        requester_email=current_user_email,
        requester_name=current_user_name,
        form_data=request.form_data,
    )

    return service_request


@router.get("/requests", response_model=List[ServiceRequestResponse])
def get_service_requests(
    status: Optional[RequestStatus] = None,
    requester_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get service requests"""

    query = db.query(ServiceRequest)

    if status:
        query = query.filter(ServiceRequest.status == status)

    if requester_id:
        query = query.filter(ServiceRequest.requester_id == requester_id)

    requests = query.order_by(ServiceRequest.created_at.desc()).all()

    return requests


@router.get("/requests/{request_id}", response_model=ServiceRequestResponse)
def get_service_request(request_id: int, db: Session = Depends(get_db)):
    """Get service request by ID"""

    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request {request_id} not found",
        )

    return request


@router.get("/requests/{request_id}/activities")
def get_request_activities(request_id: int, db: Session = Depends(get_db)):
    """Get request activity log"""

    from ..service_catalog_models import RequestActivity

    activities = (
        db.query(RequestActivity)
        .filter(RequestActivity.request_id == request_id)
        .order_by(RequestActivity.created_at.desc())
        .all()
    )

    return {"activities": activities}


# ==================== Approval Endpoints ====================


@router.get("/approvals/pending")
def get_pending_approvals(
    db: Session = Depends(get_db), current_user_id: int = 1  # TODO: Get from auth
):
    """Get pending approvals for current user"""

    approvals = (
        db.query(RequestApproval)
        .filter(
            RequestApproval.approver_id == current_user_id,
            RequestApproval.status == ApprovalStatus.PENDING,
        )
        .all()
    )

    return {"approvals": approvals}


@router.post("/requests/{request_id}/approve")
def approve_request(
    request_id: int,
    decision: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Get from auth
):
    """Approve a service request"""

    engine = ServiceCatalogEngine(db)

    try:
        request = engine.approve_request(
            request_id=request_id,
            approver_id=current_user_id,
            decision_notes=decision.decision_notes,
        )

        return {"success": True, "request": request}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/requests/{request_id}/reject")
def reject_request(
    request_id: int,
    decision: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Get from auth
):
    """Reject a service request"""

    engine = ServiceCatalogEngine(db)

    if not decision.decision_notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision notes are required for rejection",
        )

    try:
        request = engine.reject_request(
            request_id=request_id,
            approver_id=current_user_id,
            decision_notes=decision.decision_notes,
        )

        return {"success": True, "request": request}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== Metrics Endpoints ====================


@router.get("/metrics")
def get_catalog_metrics(
    service_item_id: Optional[int] = None, db: Session = Depends(get_db)
):
    """Get service catalog metrics"""

    engine = ServiceCatalogEngine(db)
    metrics = engine.get_request_metrics(service_item_id=service_item_id)

    return metrics


# ==================== Pre-configured Service Items ====================


@router.post("/items/seed")
def seed_service_items(db: Session = Depends(get_db)):
    """Seed pre-configured service items"""

    engine = ServiceCatalogEngine(db)

    # Check if already seeded
    existing = db.query(ServiceItem).count()
    if existing > 0:
        return {"message": "Service items already seeded", "count": existing}

    service_items = [
        {
            "name": "Request New User Account",
            "description": "Create a new user account with required access, licenses, and onboarding tasks. Automatically provisions accounts across all systems.",
            "category": ServiceCategory.ACCESS_MANAGEMENT,
            "icon": "👤",
            "form_schema": {
                "fields": [
                    {
                        "name": "first_name",
                        "label": "First Name",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "last_name",
                        "label": "Last Name",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "email",
                        "label": "Email Address",
                        "type": "email",
                        "required": True,
                    },
                    {
                        "name": "department",
                        "label": "Department",
                        "type": "select",
                        "options": ["IT", "HR", "Finance", "Sales", "Marketing"],
                        "required": True,
                    },
                    {
                        "name": "job_title",
                        "label": "Job Title",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "manager_email",
                        "label": "Manager Email",
                        "type": "email",
                        "required": True,
                    },
                    {
                        "name": "start_date",
                        "label": "Start Date",
                        "type": "date",
                        "required": True,
                    },
                    {
                        "name": "access_level",
                        "label": "Access Level",
                        "type": "select",
                        "options": ["Standard", "Elevated", "Admin"],
                        "required": True,
                    },
                ]
            },
            "requires_approval": True,
            "automation_enabled": True,
            "automation_type": AutomationType.AI_AGENT,
            "ai_assisted": True,
            "approval_workflow": [
                {
                    "name": "Manager Approval",
                    "approver_id": 2,
                    "approver_email": "manager@example.com",
                    "approver_name": "Manager",
                }
            ],
            "sla_hours": 24,
        },
        {
            "name": "Reset Password",
            "description": "Reset user password and send temporary credentials. Automated password reset with security verification.",
            "category": ServiceCategory.ACCESS_MANAGEMENT,
            "icon": "🔑",
            "form_schema": {
                "fields": [
                    {
                        "name": "username",
                        "label": "Username or Email",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "reason",
                        "label": "Reason for Reset",
                        "type": "textarea",
                        "required": True,
                    },
                ]
            },
            "requires_approval": False,
            "automation_enabled": True,
            "automation_type": AutomationType.POWERSHELL,
            "automation_script": "Reset-ADPassword -Identity {username} -NewPassword (ConvertTo-SecureString -AsPlainText 'TempPass123!' -Force)",
            "ai_assisted": False,
            "sla_hours": 1,
        },
        {
            "name": "Request Software Installation",
            "description": "Request installation of software on your workstation. Includes license verification and automated deployment.",
            "category": ServiceCategory.SOFTWARE_DEPLOYMENT,
            "icon": "📦",
            "form_schema": {
                "fields": [
                    {
                        "name": "software_name",
                        "label": "Software Name",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "version",
                        "label": "Version (if specific)",
                        "type": "text",
                        "required": False,
                    },
                    {
                        "name": "business_justification",
                        "label": "Business Justification",
                        "type": "textarea",
                        "required": True,
                    },
                    {
                        "name": "computer_name",
                        "label": "Computer Name",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "urgency",
                        "label": "Urgency",
                        "type": "select",
                        "options": ["Low", "Medium", "High", "Critical"],
                        "required": True,
                    },
                ]
            },
            "requires_approval": True,
            "automation_enabled": True,
            "automation_type": AutomationType.AI_AGENT,
            "ai_assisted": True,
            "approval_workflow": [
                {
                    "name": "IT Manager Approval",
                    "approver_id": 3,
                    "approver_email": "it-manager@example.com",
                    "approver_name": "IT Manager",
                }
            ],
            "sla_hours": 48,
        },
        {
            "name": "Request VPN Access",
            "description": "Request VPN access for remote work. Automated provisioning with security policy enforcement.",
            "category": ServiceCategory.NETWORK_REQUESTS,
            "icon": "🔒",
            "form_schema": {
                "fields": [
                    {
                        "name": "vpn_type",
                        "label": "VPN Type",
                        "type": "select",
                        "options": ["Standard", "Admin", "Contractor"],
                        "required": True,
                    },
                    {
                        "name": "duration",
                        "label": "Access Duration",
                        "type": "select",
                        "options": [
                            "1 Month",
                            "3 Months",
                            "6 Months",
                            "1 Year",
                            "Permanent",
                        ],
                        "required": True,
                    },
                    {
                        "name": "business_justification",
                        "label": "Business Justification",
                        "type": "textarea",
                        "required": True,
                    },
                    {
                        "name": "remote_location",
                        "label": "Primary Remote Location",
                        "type": "text",
                        "required": True,
                    },
                ]
            },
            "requires_approval": True,
            "automation_enabled": True,
            "automation_type": AutomationType.AI_AGENT,
            "ai_assisted": True,
            "approval_workflow": [
                {
                    "name": "Manager Approval",
                    "approver_id": 2,
                    "approver_email": "manager@example.com",
                    "approver_name": "Manager",
                },
                {
                    "name": "Security Approval",
                    "approver_id": 4,
                    "approver_email": "security@example.com",
                    "approver_name": "Security Team",
                },
            ],
            "sla_hours": 24,
        },
        {
            "name": "Request Server/VM Deployment",
            "description": "Request deployment of a new server or virtual machine. Automated provisioning with configuration management.",
            "category": ServiceCategory.SYSTEMS_SERVERS,
            "icon": "🖥",
            "form_schema": {
                "fields": [
                    {
                        "name": "server_type",
                        "label": "Server Type",
                        "type": "select",
                        "options": ["Physical Server", "Virtual Machine", "Container"],
                        "required": True,
                    },
                    {
                        "name": "os",
                        "label": "Operating System",
                        "type": "select",
                        "options": [
                            "Windows Server 2022",
                            "Ubuntu 22.04",
                            "RHEL 9",
                            "CentOS 9",
                        ],
                        "required": True,
                    },
                    {
                        "name": "cpu_cores",
                        "label": "CPU Cores",
                        "type": "number",
                        "required": True,
                    },
                    {
                        "name": "ram_gb",
                        "label": "RAM (GB)",
                        "type": "number",
                        "required": True,
                    },
                    {
                        "name": "storage_gb",
                        "label": "Storage (GB)",
                        "type": "number",
                        "required": True,
                    },
                    {
                        "name": "purpose",
                        "label": "Server Purpose",
                        "type": "textarea",
                        "required": True,
                    },
                    {
                        "name": "environment",
                        "label": "Environment",
                        "type": "select",
                        "options": ["Development", "Staging", "Production"],
                        "required": True,
                    },
                ]
            },
            "requires_approval": True,
            "automation_enabled": True,
            "automation_type": AutomationType.AI_AGENT,
            "ai_assisted": True,
            "approval_workflow": [
                {
                    "name": "IT Manager Approval",
                    "approver_id": 3,
                    "approver_email": "it-manager@example.com",
                    "approver_name": "IT Manager",
                }
            ],
            "sla_hours": 72,
        },
        {
            "name": "Report Outage",
            "description": "Report a system outage or service disruption. Immediate notification to on-call team with automated diagnostics.",
            "category": ServiceCategory.IT_SUPPORT,
            "icon": "🚨",
            "form_schema": {
                "fields": [
                    {
                        "name": "affected_system",
                        "label": "Affected System/Service",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "severity",
                        "label": "Severity",
                        "type": "select",
                        "options": [
                            "Critical - Complete Outage",
                            "High - Major Impact",
                            "Medium - Partial Impact",
                            "Low - Minor Issue",
                        ],
                        "required": True,
                    },
                    {
                        "name": "users_affected",
                        "label": "Number of Users Affected",
                        "type": "select",
                        "options": ["1-10", "11-50", "51-100", "100+", "All Users"],
                        "required": True,
                    },
                    {
                        "name": "description",
                        "label": "Description of Issue",
                        "type": "textarea",
                        "required": True,
                    },
                    {
                        "name": "started_at",
                        "label": "When Did It Start?",
                        "type": "datetime",
                        "required": True,
                    },
                ]
            },
            "requires_approval": False,
            "automation_enabled": True,
            "automation_type": AutomationType.AI_AGENT,
            "ai_assisted": True,
            "sla_hours": 1,
            "priority": 1,
        },
        {
            "name": "Request Firewall Change",
            "description": "Request firewall rule changes or port openings. Automated validation and deployment with security review.",
            "category": ServiceCategory.NETWORK_REQUESTS,
            "icon": "🛡",
            "form_schema": {
                "fields": [
                    {
                        "name": "change_type",
                        "label": "Change Type",
                        "type": "select",
                        "options": [
                            "Open Port",
                            "Close Port",
                            "Modify Rule",
                            "Add IP Whitelist",
                        ],
                        "required": True,
                    },
                    {
                        "name": "source_ip",
                        "label": "Source IP/Range",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "destination_ip",
                        "label": "Destination IP/Range",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "port",
                        "label": "Port Number",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "protocol",
                        "label": "Protocol",
                        "type": "select",
                        "options": ["TCP", "UDP", "ICMP", "Any"],
                        "required": True,
                    },
                    {
                        "name": "business_justification",
                        "label": "Business Justification",
                        "type": "textarea",
                        "required": True,
                    },
                    {
                        "name": "duration",
                        "label": "Duration",
                        "type": "select",
                        "options": ["Temporary (30 days)", "Permanent"],
                        "required": True,
                    },
                ]
            },
            "requires_approval": True,
            "automation_enabled": True,
            "automation_type": AutomationType.AI_AGENT,
            "ai_assisted": True,
            "approval_workflow": [
                {
                    "name": "Network Team Approval",
                    "approver_id": 5,
                    "approver_email": "network@example.com",
                    "approver_name": "Network Team",
                },
                {
                    "name": "Security Approval",
                    "approver_id": 4,
                    "approver_email": "security@example.com",
                    "approver_name": "Security Team",
                },
            ],
            "sla_hours": 48,
        },
    ]

    created_items = []
    for item_data in service_items:
        item = engine.create_service_item(**item_data, user_id=1)
        created_items.append(item)

    return {
        "message": "Service items seeded successfully",
        "count": len(created_items),
        "items": created_items,
    }
