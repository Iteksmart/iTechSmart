"""
Multi-Tenant Workspace API Endpoints
Provides REST API for workspace management
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

from ..services.workspace_service import (
    workspace_service,
    WorkspaceRole,
    WorkspacePlan,
    ResourceType
)

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])


# Request Models
class CreateWorkspaceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=3, max_length=50, regex="^[a-z0-9-]+$")
    description: Optional[str] = Field(None, max_length=500)
    plan: WorkspacePlan = WorkspacePlan.FREE


class UpdateWorkspaceRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    settings: Optional[dict] = None


class AddMemberRequest(BaseModel):
    user_id: str
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.MEMBER


class UpdateMemberRoleRequest(BaseModel):
    role: WorkspaceRole


class CreateInvitationRequest(BaseModel):
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.MEMBER


class AcceptInvitationRequest(BaseModel):
    user_id: str
    email: EmailStr


# Response Models
class WorkspaceResponse(BaseModel):
    success: bool
    workspace: Optional[dict] = None
    error: Optional[str] = None


class MemberResponse(BaseModel):
    success: bool
    member: Optional[dict] = None
    error: Optional[str] = None


class InvitationResponse(BaseModel):
    success: bool
    invitation: Optional[dict] = None
    error: Optional[str] = None


# Helper function to get current user (mock for now)
def get_current_user(user_id: str = Query(...)) -> dict:
    """Get current authenticated user"""
    return {"user_id": user_id, "email": f"{user_id}@example.com"}


# Endpoints

@router.post("/create", response_model=WorkspaceResponse)
async def create_workspace(
    request: CreateWorkspaceRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new workspace
    
    Creates an isolated workspace for team collaboration
    The creator becomes the workspace owner
    """
    result = workspace_service.create_workspace(
        name=request.name,
        slug=request.slug,
        owner_id=current_user["user_id"],
        owner_email=current_user["email"],
        plan=request.plan,
        description=request.description
    )
    
    return WorkspaceResponse(**result)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get workspace details
    
    Returns complete workspace information including members and settings
    """
    workspace = workspace_service.get_workspace(workspace_id)
    
    if not workspace:
        return WorkspaceResponse(success=False, error="Workspace not found")
    
    # Check if user is member
    if current_user["user_id"] not in workspace.members:
        return WorkspaceResponse(success=False, error="Access denied")
    
    return WorkspaceResponse(success=True, workspace=workspace.to_dict())


@router.get("/slug/{slug}", response_model=WorkspaceResponse)
async def get_workspace_by_slug(
    slug: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get workspace by slug
    
    Retrieves workspace using its unique slug identifier
    """
    workspace = workspace_service.get_workspace_by_slug(slug)
    
    if not workspace:
        return WorkspaceResponse(success=False, error="Workspace not found")
    
    # Check if user is member
    if current_user["user_id"] not in workspace.members:
        return WorkspaceResponse(success=False, error="Access denied")
    
    return WorkspaceResponse(success=True, workspace=workspace.to_dict())


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    request: UpdateWorkspaceRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update workspace details
    
    Requires admin or owner permissions
    """
    updates = request.dict(exclude_unset=True)
    
    result = workspace_service.update_workspace(
        workspace_id=workspace_id,
        user_id=current_user["user_id"],
        **updates
    )
    
    return WorkspaceResponse(**result)


@router.delete("/{workspace_id}", response_model=WorkspaceResponse)
async def delete_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete workspace
    
    Only workspace owner can delete
    This action is irreversible
    """
    result = workspace_service.delete_workspace(
        workspace_id=workspace_id,
        user_id=current_user["user_id"]
    )
    
    return WorkspaceResponse(**result)


@router.get("/user/list")
async def list_user_workspaces(
    current_user: dict = Depends(get_current_user)
):
    """
    List all workspaces for current user
    
    Returns all workspaces where user is a member
    """
    workspaces = workspace_service.get_user_workspaces(current_user["user_id"])
    
    return {
        "success": True,
        "total": len(workspaces),
        "workspaces": workspaces
    }


@router.post("/{workspace_id}/members/add", response_model=MemberResponse)
async def add_member(
    workspace_id: str,
    request: AddMemberRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Add member to workspace
    
    Requires admin or owner permissions
    """
    result = workspace_service.add_member(
        workspace_id=workspace_id,
        user_id=current_user["user_id"],
        new_member_id=request.user_id,
        new_member_email=request.email,
        role=request.role
    )
    
    return MemberResponse(**result)


@router.delete("/{workspace_id}/members/{member_id}", response_model=MemberResponse)
async def remove_member(
    workspace_id: str,
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove member from workspace
    
    Requires admin or owner permissions
    Cannot remove workspace owner
    """
    result = workspace_service.remove_member(
        workspace_id=workspace_id,
        user_id=current_user["user_id"],
        member_id=member_id
    )
    
    return MemberResponse(**result)


@router.put("/{workspace_id}/members/{member_id}/role", response_model=MemberResponse)
async def update_member_role(
    workspace_id: str,
    member_id: str,
    request: UpdateMemberRoleRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update member role
    
    Requires admin or owner permissions
    Cannot change owner role
    """
    result = workspace_service.update_member_role(
        workspace_id=workspace_id,
        user_id=current_user["user_id"],
        member_id=member_id,
        new_role=request.role
    )
    
    return MemberResponse(**result)


@router.get("/{workspace_id}/members")
async def list_members(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    List all workspace members
    
    Returns member details including roles and permissions
    """
    workspace = workspace_service.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if user is member
    if current_user["user_id"] not in workspace.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    members = [member.to_dict() for member in workspace.members.values()]
    
    return {
        "success": True,
        "total": len(members),
        "members": members
    }


@router.post("/{workspace_id}/invitations/create", response_model=InvitationResponse)
async def create_invitation(
    workspace_id: str,
    request: CreateInvitationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create workspace invitation
    
    Sends invitation to email address
    Requires admin or owner permissions
    """
    result = workspace_service.create_invitation(
        workspace_id=workspace_id,
        user_id=current_user["user_id"],
        email=request.email,
        role=request.role
    )
    
    return InvitationResponse(**result)


@router.post("/invitations/{invitation_id}/accept", response_model=MemberResponse)
async def accept_invitation(
    invitation_id: str,
    request: AcceptInvitationRequest
):
    """
    Accept workspace invitation
    
    User accepts invitation and joins workspace
    """
    result = workspace_service.accept_invitation(
        invitation_id=invitation_id,
        user_id=request.user_id,
        user_email=request.email
    )
    
    return MemberResponse(**result)


@router.get("/{workspace_id}/limits")
async def get_workspace_limits(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get workspace resource limits
    
    Returns current usage and limits for all resources
    """
    workspace = workspace_service.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if user is member
    if current_user["user_id"] not in workspace.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    limits = workspace.limits.to_dict()
    usage = workspace.resource_counts
    
    # Calculate usage percentages
    usage_percentages = {}
    for resource_type in ResourceType:
        resource_key = resource_type.value
        limit_key = f"max_{resource_key}s"
        
        if limit_key in limits:
            current = usage.get(resource_key, 0)
            maximum = limits[limit_key]
            percentage = (current / maximum * 100) if maximum > 0 else 0
            
            usage_percentages[resource_key] = {
                "current": current,
                "maximum": maximum,
                "percentage": round(percentage, 2)
            }
    
    return {
        "success": True,
        "plan": workspace.plan.value,
        "limits": limits,
        "usage": usage_percentages
    }


@router.post("/{workspace_id}/resources/increment")
async def increment_resource(
    workspace_id: str,
    resource_type: ResourceType,
    current_user: dict = Depends(get_current_user)
):
    """
    Increment resource count
    
    Used internally when creating new resources
    Checks against workspace limits
    """
    workspace = workspace_service.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if user is member
    if current_user["user_id"] not in workspace.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = workspace_service.increment_resource_count(
        workspace_id=workspace_id,
        resource_type=resource_type
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/{workspace_id}/settings")
async def get_workspace_settings(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get workspace settings
    
    Returns all workspace configuration settings
    """
    workspace = workspace_service.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if user is member
    if current_user["user_id"] not in workspace.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "success": True,
        "settings": workspace.settings
    }


@router.get("/{workspace_id}/stats")
async def get_workspace_stats(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get workspace statistics
    
    Returns overview of workspace activity and resources
    """
    workspace = workspace_service.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if user is member
    if current_user["user_id"] not in workspace.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "success": True,
        "stats": {
            "member_count": len(workspace.members),
            "resource_counts": workspace.resource_counts,
            "plan": workspace.plan.value,
            "created_at": workspace.created_at.isoformat(),
            "is_active": workspace.is_active
        }
    }