"""
Multi-Tenant Workspace Service
Manages isolated workspaces for different teams and organizations
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import logging

logger = logging.getLogger(__name__)


class WorkspaceRole(str, Enum):
    """User roles within a workspace"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class WorkspacePlan(str, Enum):
    """Workspace subscription plans"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ResourceType(str, Enum):
    """Types of workspace resources"""
    PROJECT = "project"
    AGENT = "agent"
    WORKFLOW = "workflow"
    DOCUMENT = "document"
    API_KEY = "api_key"
    INTEGRATION = "integration"


@dataclass
class WorkspaceLimits:
    """Resource limits for workspace"""
    max_members: int
    max_projects: int
    max_agents: int
    max_workflows: int
    max_storage_gb: int
    max_api_calls_per_month: int
    max_concurrent_tasks: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkspaceMember:
    """Workspace member information"""
    user_id: str
    email: str
    role: WorkspaceRole
    joined_at: datetime
    last_active: Optional[datetime]
    permissions: Set[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "permissions": list(self.permissions)
        }


@dataclass
class Workspace:
    """Workspace entity"""
    workspace_id: str
    name: str
    slug: str
    description: Optional[str]
    owner_id: str
    plan: WorkspacePlan
    created_at: datetime
    updated_at: datetime
    members: Dict[str, WorkspaceMember]
    limits: WorkspaceLimits
    settings: Dict[str, Any]
    resource_counts: Dict[str, int]
    is_active: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "owner_id": self.owner_id,
            "plan": self.plan.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "members": {k: v.to_dict() for k, v in self.members.items()},
            "limits": self.limits.to_dict(),
            "settings": self.settings,
            "resource_counts": self.resource_counts,
            "is_active": self.is_active,
            "member_count": len(self.members)
        }


@dataclass
class WorkspaceInvitation:
    """Workspace invitation"""
    invitation_id: str
    workspace_id: str
    email: str
    role: WorkspaceRole
    invited_by: str
    created_at: datetime
    expires_at: datetime
    accepted: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "invitation_id": self.invitation_id,
            "workspace_id": self.workspace_id,
            "email": self.email,
            "role": self.role.value,
            "invited_by": self.invited_by,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "accepted": self.accepted
        }


class WorkspaceService:
    """Manages multi-tenant workspaces"""
    
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.user_workspaces: Dict[str, Set[str]] = {}  # user_id -> workspace_ids
        self.invitations: Dict[str, WorkspaceInvitation] = {}
        self.workspace_slugs: Dict[str, str] = {}  # slug -> workspace_id
        
        # Plan limits
        self.plan_limits = {
            WorkspacePlan.FREE: WorkspaceLimits(
                max_members=3,
                max_projects=5,
                max_agents=2,
                max_workflows=10,
                max_storage_gb=1,
                max_api_calls_per_month=1000,
                max_concurrent_tasks=2
            ),
            WorkspacePlan.STARTER: WorkspaceLimits(
                max_members=10,
                max_projects=20,
                max_agents=5,
                max_workflows=50,
                max_storage_gb=10,
                max_api_calls_per_month=10000,
                max_concurrent_tasks=5
            ),
            WorkspacePlan.PROFESSIONAL: WorkspaceLimits(
                max_members=50,
                max_projects=100,
                max_agents=20,
                max_workflows=200,
                max_storage_gb=100,
                max_api_calls_per_month=100000,
                max_concurrent_tasks=20
            ),
            WorkspacePlan.ENTERPRISE: WorkspaceLimits(
                max_members=999999,
                max_projects=999999,
                max_agents=999999,
                max_workflows=999999,
                max_storage_gb=999999,
                max_api_calls_per_month=999999999,
                max_concurrent_tasks=100
            )
        }
    
    def create_workspace(
        self,
        name: str,
        slug: str,
        owner_id: str,
        owner_email: str,
        plan: WorkspacePlan = WorkspacePlan.FREE,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new workspace"""
        try:
            # Validate slug uniqueness
            if slug in self.workspace_slugs:
                return {"success": False, "error": "Workspace slug already exists"}
            
            workspace_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Create owner member
            owner = WorkspaceMember(
                user_id=owner_id,
                email=owner_email,
                role=WorkspaceRole.OWNER,
                joined_at=now,
                last_active=now,
                permissions=self._get_role_permissions(WorkspaceRole.OWNER)
            )
            
            # Create workspace
            workspace = Workspace(
                workspace_id=workspace_id,
                name=name,
                slug=slug,
                description=description,
                owner_id=owner_id,
                plan=plan,
                created_at=now,
                updated_at=now,
                members={owner_id: owner},
                limits=self.plan_limits[plan],
                settings={
                    "allow_public_sharing": False,
                    "require_2fa": False,
                    "data_retention_days": 90
                },
                resource_counts={
                    ResourceType.PROJECT.value: 0,
                    ResourceType.AGENT.value: 0,
                    ResourceType.WORKFLOW.value: 0,
                    ResourceType.DOCUMENT.value: 0,
                    ResourceType.API_KEY.value: 0,
                    ResourceType.INTEGRATION.value: 0
                },
                is_active=True
            )
            
            self.workspaces[workspace_id] = workspace
            self.workspace_slugs[slug] = workspace_id
            
            if owner_id not in self.user_workspaces:
                self.user_workspaces[owner_id] = set()
            self.user_workspaces[owner_id].add(workspace_id)
            
            logger.info(f"Created workspace {workspace_id} for user {owner_id}")
            
            return {
                "success": True,
                "workspace": workspace.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            return {"success": False, "error": str(e)}
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID"""
        return self.workspaces.get(workspace_id)
    
    def get_workspace_by_slug(self, slug: str) -> Optional[Workspace]:
        """Get workspace by slug"""
        workspace_id = self.workspace_slugs.get(slug)
        return self.workspaces.get(workspace_id) if workspace_id else None
    
    def update_workspace(
        self,
        workspace_id: str,
        user_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update workspace details"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"success": False, "error": "Workspace not found"}
        
        # Check permissions
        if not self._has_permission(workspace, user_id, "workspace.update"):
            return {"success": False, "error": "Insufficient permissions"}
        
        try:
            # Update allowed fields
            allowed_fields = ["name", "description", "settings"]
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(workspace, field, value)
            
            workspace.updated_at = datetime.utcnow()
            
            return {
                "success": True,
                "workspace": workspace.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to update workspace: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_workspace(
        self,
        workspace_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Delete workspace (owner only)"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"success": False, "error": "Workspace not found"}
        
        if workspace.owner_id != user_id:
            return {"success": False, "error": "Only owner can delete workspace"}
        
        try:
            # Remove from all members
            for member_id in workspace.members.keys():
                if member_id in self.user_workspaces:
                    self.user_workspaces[member_id].discard(workspace_id)
            
            # Remove workspace
            del self.workspaces[workspace_id]
            del self.workspace_slugs[workspace.slug]
            
            logger.info(f"Deleted workspace {workspace_id}")
            
            return {"success": True, "workspace_id": workspace_id}
        
        except Exception as e:
            logger.error(f"Failed to delete workspace: {e}")
            return {"success": False, "error": str(e)}
    
    def add_member(
        self,
        workspace_id: str,
        user_id: str,
        new_member_id: str,
        new_member_email: str,
        role: WorkspaceRole = WorkspaceRole.MEMBER
    ) -> Dict[str, Any]:
        """Add member to workspace"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"success": False, "error": "Workspace not found"}
        
        # Check permissions
        if not self._has_permission(workspace, user_id, "members.add"):
            return {"success": False, "error": "Insufficient permissions"}
        
        # Check member limit
        if len(workspace.members) >= workspace.limits.max_members:
            return {"success": False, "error": "Member limit reached"}
        
        # Check if already member
        if new_member_id in workspace.members:
            return {"success": False, "error": "User is already a member"}
        
        try:
            member = WorkspaceMember(
                user_id=new_member_id,
                email=new_member_email,
                role=role,
                joined_at=datetime.utcnow(),
                last_active=None,
                permissions=self._get_role_permissions(role)
            )
            
            workspace.members[new_member_id] = member
            workspace.updated_at = datetime.utcnow()
            
            if new_member_id not in self.user_workspaces:
                self.user_workspaces[new_member_id] = set()
            self.user_workspaces[new_member_id].add(workspace_id)
            
            logger.info(f"Added member {new_member_id} to workspace {workspace_id}")
            
            return {
                "success": True,
                "member": member.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to add member: {e}")
            return {"success": False, "error": str(e)}
    
    def remove_member(
        self,
        workspace_id: str,
        user_id: str,
        member_id: str
    ) -> Dict[str, Any]:
        """Remove member from workspace"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"success": False, "error": "Workspace not found"}
        
        # Cannot remove owner
        if member_id == workspace.owner_id:
            return {"success": False, "error": "Cannot remove workspace owner"}
        
        # Check permissions
        if not self._has_permission(workspace, user_id, "members.remove"):
            return {"success": False, "error": "Insufficient permissions"}
        
        if member_id not in workspace.members:
            return {"success": False, "error": "Member not found"}
        
        try:
            del workspace.members[member_id]
            workspace.updated_at = datetime.utcnow()
            
            if member_id in self.user_workspaces:
                self.user_workspaces[member_id].discard(workspace_id)
            
            logger.info(f"Removed member {member_id} from workspace {workspace_id}")
            
            return {"success": True, "member_id": member_id}
        
        except Exception as e:
            logger.error(f"Failed to remove member: {e}")
            return {"success": False, "error": str(e)}
    
    def update_member_role(
        self,
        workspace_id: str,
        user_id: str,
        member_id: str,
        new_role: WorkspaceRole
    ) -> Dict[str, Any]:
        """Update member role"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"success": False, "error": "Workspace not found"}
        
        # Cannot change owner role
        if member_id == workspace.owner_id:
            return {"success": False, "error": "Cannot change owner role"}
        
        # Check permissions
        if not self._has_permission(workspace, user_id, "members.update"):
            return {"success": False, "error": "Insufficient permissions"}
        
        member = workspace.members.get(member_id)
        if not member:
            return {"success": False, "error": "Member not found"}
        
        try:
            member.role = new_role
            member.permissions = self._get_role_permissions(new_role)
            workspace.updated_at = datetime.utcnow()
            
            logger.info(f"Updated member {member_id} role to {new_role.value}")
            
            return {
                "success": True,
                "member": member.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to update member role: {e}")
            return {"success": False, "error": str(e)}
    
    def create_invitation(
        self,
        workspace_id: str,
        user_id: str,
        email: str,
        role: WorkspaceRole = WorkspaceRole.MEMBER
    ) -> Dict[str, Any]:
        """Create workspace invitation"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"success": False, "error": "Workspace not found"}
        
        # Check permissions
        if not self._has_permission(workspace, user_id, "invitations.create"):
            return {"success": False, "error": "Insufficient permissions"}
        
        # Check member limit
        if len(workspace.members) >= workspace.limits.max_members:
            return {"success": False, "error": "Member limit reached"}
        
        try:
            invitation_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            invitation = WorkspaceInvitation(
                invitation_id=invitation_id,
                workspace_id=workspace_id,
                email=email,
                role=role,
                invited_by=user_id,
                created_at=now,
                expires_at=now.replace(day=now.day + 7),  # 7 days expiry
                accepted=False
            )
            
            self.invitations[invitation_id] = invitation
            
            logger.info(f"Created invitation {invitation_id} for {email}")
            
            return {
                "success": True,
                "invitation": invitation.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to create invitation: {e}")
            return {"success": False, "error": str(e)}
    
    def accept_invitation(
        self,
        invitation_id: str,
        user_id: str,
        user_email: str
    ) -> Dict[str, Any]:
        """Accept workspace invitation"""
        invitation = self.invitations.get(invitation_id)
        if not invitation:
            return {"success": False, "error": "Invitation not found"}
        
        if invitation.accepted:
            return {"success": False, "error": "Invitation already accepted"}
        
        if datetime.utcnow() > invitation.expires_at:
            return {"success": False, "error": "Invitation expired"}
        
        if invitation.email != user_email:
            return {"success": False, "error": "Email mismatch"}
        
        # Add member to workspace
        result = self.add_member(
            workspace_id=invitation.workspace_id,
            user_id=invitation.invited_by,  # Use inviter's ID for permission check
            new_member_id=user_id,
            new_member_email=user_email,
            role=invitation.role
        )
        
        if result["success"]:
            invitation.accepted = True
            logger.info(f"Accepted invitation {invitation_id}")
        
        return result
    
    def get_user_workspaces(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all workspaces for user"""
        workspace_ids = self.user_workspaces.get(user_id, set())
        workspaces = []
        
        for workspace_id in workspace_ids:
            workspace = self.get_workspace(workspace_id)
            if workspace and workspace.is_active:
                workspaces.append(workspace.to_dict())
        
        return workspaces
    
    def increment_resource_count(
        self,
        workspace_id: str,
        resource_type: ResourceType
    ) -> Dict[str, Any]:
        """Increment resource count"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"success": False, "error": "Workspace not found"}
        
        current_count = workspace.resource_counts.get(resource_type.value, 0)
        limit = getattr(workspace.limits, f"max_{resource_type.value}s", 999999)
        
        if current_count >= limit:
            return {"success": False, "error": f"{resource_type.value} limit reached"}
        
        workspace.resource_counts[resource_type.value] = current_count + 1
        
        return {"success": True, "count": current_count + 1}
    
    def _has_permission(
        self,
        workspace: Workspace,
        user_id: str,
        permission: str
    ) -> bool:
        """Check if user has permission"""
        member = workspace.members.get(user_id)
        if not member:
            return False
        
        return permission in member.permissions
    
    def _get_role_permissions(self, role: WorkspaceRole) -> Set[str]:
        """Get permissions for role"""
        permissions = {
            WorkspaceRole.OWNER: {
                "workspace.read", "workspace.update", "workspace.delete",
                "members.read", "members.add", "members.remove", "members.update",
                "invitations.create", "invitations.delete",
                "resources.create", "resources.read", "resources.update", "resources.delete",
                "settings.update", "billing.manage"
            },
            WorkspaceRole.ADMIN: {
                "workspace.read", "workspace.update",
                "members.read", "members.add", "members.remove",
                "invitations.create",
                "resources.create", "resources.read", "resources.update", "resources.delete",
                "settings.update"
            },
            WorkspaceRole.MEMBER: {
                "workspace.read",
                "members.read",
                "resources.create", "resources.read", "resources.update"
            },
            WorkspaceRole.VIEWER: {
                "workspace.read",
                "members.read",
                "resources.read"
            }
        }
        
        return permissions.get(role, set())


# Global service instance
workspace_service = WorkspaceService()