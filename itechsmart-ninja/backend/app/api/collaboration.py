"""
Team Collaboration API Routes
Provides endpoints for team management and collaboration
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, Team, TeamMember, Workspace, Comment
from app.integrations.collaboration import CollaborationManager

router = APIRouter(prefix="/api", tags=["collaboration"])

# Initialize collaboration manager
collab_manager = CollaborationManager()


# Request models
class CreateTeamRequest(BaseModel):
    name: str
    description: Optional[str] = None
    plan: str = "free"


class UpdateTeamRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    plan: Optional[str] = None


class InviteMemberRequest(BaseModel):
    email: str
    role: str = "member"


class UpdateMemberRoleRequest(BaseModel):
    role: str


class CreateWorkspaceRequest(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateWorkspaceRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CreateCommentRequest(BaseModel):
    resource_type: str
    resource_id: int
    content: str
    team_id: Optional[int] = None


class UpdateCommentRequest(BaseModel):
    content: str


# Team endpoints
@router.post("/teams/create")
async def create_team(
    request: CreateTeamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new team"""
    try:
        team = await collab_manager.create_team(
            name=request.name,
            owner_id=current_user.id,
            description=request.description,
            plan=request.plan
        )
        
        # Save to database
        db_team = Team(
            team_id=team["id"],
            name=team["name"],
            description=team["description"],
            owner_id=team["owner_id"],
            plan=team["plan"]
        )
        db.add(db_team)
        db.commit()
        
        return {
            "success": True,
            "team": team,
            "message": "Team created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams")
async def list_teams(
    current_user: User = Depends(get_current_user)
):
    """List all teams for current user"""
    try:
        teams = await collab_manager.list_teams(current_user.id)
        
        return {
            "success": True,
            "teams": teams,
            "count": len(teams),
            "message": "Teams retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/{team_id}")
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get team details"""
    try:
        team = await collab_manager.get_team(team_id)
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Check if user is a member
        members = await collab_manager.get_team_members(team_id)
        if not any(m["user_id"] == current_user.id for m in members):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "team": team,
            "message": "Team retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/teams/{team_id}")
async def update_team(
    team_id: int,
    request: UpdateTeamRequest,
    current_user: User = Depends(get_current_user)
):
    """Update team details"""
    try:
        # Check permission
        has_permission = await collab_manager.check_permission(
            team_id, current_user.id, "manage_team"
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        team = await collab_manager.update_team(
            team_id=team_id,
            name=request.name,
            description=request.description,
            plan=request.plan
        )
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return {
            "success": True,
            "team": team,
            "message": "Team updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a team"""
    try:
        # Check permission
        has_permission = await collab_manager.check_permission(
            team_id, current_user.id, "delete_team"
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        success = await collab_manager.delete_team(team_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Delete from database
        db_team = db.query(Team).filter(Team.team_id == team_id).first()
        if db_team:
            db.delete(db_team)
            db.commit()
        
        return {
            "success": True,
            "message": "Team deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Team member endpoints
@router.post("/teams/{team_id}/invite")
async def invite_member(
    team_id: int,
    request: InviteMemberRequest,
    current_user: User = Depends(get_current_user)
):
    """Invite a member to the team"""
    try:
        # Check permission
        has_permission = await collab_manager.check_permission(
            team_id, current_user.id, "manage_members"
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        invitation = await collab_manager.invite_member(
            team_id=team_id,
            email=request.email,
            role=request.role,
            invited_by=current_user.id
        )
        
        return {
            "success": True,
            "invitation": invitation,
            "message": f"Invitation sent to {request.email}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/{team_id}/members")
async def get_team_members(
    team_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get all team members"""
    try:
        # Check if user is a member
        members = await collab_manager.get_team_members(team_id)
        if not any(m["user_id"] == current_user.id for m in members):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "members": members,
            "count": len(members),
            "message": "Members retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/teams/{team_id}/members/{user_id}")
async def remove_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Remove a member from the team"""
    try:
        # Check permission
        has_permission = await collab_manager.check_permission(
            team_id, current_user.id, "manage_members"
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        success = await collab_manager.remove_team_member(team_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        
        return {
            "success": True,
            "message": "Member removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/teams/{team_id}/members/{user_id}/role")
async def update_member_role(
    team_id: int,
    user_id: int,
    request: UpdateMemberRoleRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a member's role"""
    try:
        # Check permission
        has_permission = await collab_manager.check_permission(
            team_id, current_user.id, "manage_members"
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        success = await collab_manager.update_member_role(
            team_id, user_id, request.role
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        
        return {
            "success": True,
            "message": "Member role updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Workspace endpoints
@router.post("/teams/{team_id}/workspaces")
async def create_workspace(
    team_id: int,
    request: CreateWorkspaceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a workspace"""
    try:
        # Check permission
        has_permission = await collab_manager.check_permission(
            team_id, current_user.id, "manage_workspaces"
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        workspace = await collab_manager.create_workspace(
            team_id=team_id,
            name=request.name,
            description=request.description,
            created_by=current_user.id
        )
        
        # Save to database
        db_workspace = Workspace(
            workspace_id=workspace["id"],
            team_id=team_id,
            name=workspace["name"],
            description=workspace["description"],
            created_by=current_user.id
        )
        db.add(db_workspace)
        db.commit()
        
        return {
            "success": True,
            "workspace": workspace,
            "message": "Workspace created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/{team_id}/workspaces")
async def list_workspaces(
    team_id: int,
    current_user: User = Depends(get_current_user)
):
    """List all workspaces for a team"""
    try:
        # Check if user is a member
        members = await collab_manager.get_team_members(team_id)
        if not any(m["user_id"] == current_user.id for m in members):
            raise HTTPException(status_code=403, detail="Access denied")
        
        workspaces = await collab_manager.list_workspaces(team_id)
        
        return {
            "success": True,
            "workspaces": workspaces,
            "count": len(workspaces),
            "message": "Workspaces retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workspaces/{workspace_id}")
async def get_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get workspace details"""
    try:
        workspace = await collab_manager.get_workspace(workspace_id)
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Check if user is a team member
        members = await collab_manager.get_team_members(workspace["team_id"])
        if not any(m["user_id"] == current_user.id for m in members):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "workspace": workspace,
            "message": "Workspace retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/workspaces/{workspace_id}")
async def update_workspace(
    workspace_id: int,
    request: UpdateWorkspaceRequest,
    current_user: User = Depends(get_current_user)
):
    """Update workspace details"""
    try:
        workspace = await collab_manager.get_workspace(workspace_id)
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Check permission
        has_permission = await collab_manager.check_permission(
            workspace["team_id"], current_user.id, "manage_workspaces"
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        updated = await collab_manager.update_workspace(
            workspace_id=workspace_id,
            name=request.name,
            description=request.description
        )
        
        return {
            "success": True,
            "workspace": updated,
            "message": "Workspace updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workspace"""
    try:
        workspace = await collab_manager.get_workspace(workspace_id)
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Check permission
        has_permission = await collab_manager.check_permission(
            workspace["team_id"], current_user.id, "manage_workspaces"
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        success = await collab_manager.delete_workspace(workspace_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Delete from database
        db_workspace = db.query(Workspace).filter(
            Workspace.workspace_id == workspace_id
        ).first()
        if db_workspace:
            db.delete(db_workspace)
            db.commit()
        
        return {
            "success": True,
            "message": "Workspace deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Comment endpoints
@router.post("/comments/create")
async def create_comment(
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a comment"""
    try:
        comment = await collab_manager.add_comment(
            user_id=current_user.id,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            content=request.content,
            team_id=request.team_id
        )
        
        # Save to database
        db_comment = Comment(
            comment_id=comment["id"],
            user_id=current_user.id,
            resource_type=comment["resource_type"],
            resource_id=comment["resource_id"],
            content=comment["content"],
            team_id=request.team_id
        )
        db.add(db_comment)
        db.commit()
        
        return {
            "success": True,
            "comment": comment,
            "message": "Comment created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comments")
async def get_comments(
    resource_type: str,
    resource_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get comments for a resource"""
    try:
        comments = await collab_manager.get_comments(resource_type, resource_id)
        
        return {
            "success": True,
            "comments": comments,
            "count": len(comments),
            "message": "Comments retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    request: UpdateCommentRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a comment"""
    try:
        comment = await collab_manager.update_comment(comment_id, request.content)
        
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        return {
            "success": True,
            "comment": comment,
            "message": "Comment updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment"""
    try:
        success = await collab_manager.delete_comment(comment_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Delete from database
        db_comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
        if db_comment:
            db.delete(db_comment)
            db.commit()
        
        return {
            "success": True,
            "message": "Comment deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Activity endpoints
@router.get("/teams/{team_id}/activity")
async def get_team_activity(
    team_id: int,
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """Get team activity log"""
    try:
        # Check if user is a member
        members = await collab_manager.get_team_members(team_id)
        if not any(m["user_id"] == current_user.id for m in members):
            raise HTTPException(status_code=403, detail="Access denied")
        
        activities = await collab_manager.get_team_activity(team_id, limit)
        
        return {
            "success": True,
            "activities": activities,
            "count": len(activities),
            "message": "Activity retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/{team_id}/stats")
async def get_team_stats(
    team_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get team statistics"""
    try:
        # Check if user is a member
        members = await collab_manager.get_team_members(team_id)
        if not any(m["user_id"] == current_user.id for m in members):
            raise HTTPException(status_code=403, detail="Access denied")
        
        stats = await collab_manager.get_team_stats(team_id)
        
        return {
            "success": True,
            "stats": stats,
            "message": "Stats retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))