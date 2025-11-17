"""
Team Collaboration Integration
Provides team management, workspaces, and collaboration features
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TeamRole(Enum):
    """Team member roles"""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TeamPlan(Enum):
    """Team subscription plans"""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ResourceType(Enum):
    """Resource types for comments"""

    CODE = "code"
    FILE = "file"
    TASK = "task"
    WORKFLOW = "workflow"
    DOCUMENT = "document"


class CollaborationManager:
    """Manages team collaboration features"""

    def __init__(self):
        self.teams: Dict[int, Dict[str, Any]] = {}
        self.workspaces: Dict[int, Dict[str, Any]] = {}
        self.comments: Dict[int, Dict[str, Any]] = {}
        self.activity_log: List[Dict[str, Any]] = []

        # Role permissions
        self.permissions = {
            TeamRole.OWNER: [
                "manage_team",
                "delete_team",
                "manage_members",
                "manage_workspaces",
                "manage_billing",
                "all_access",
            ],
            TeamRole.ADMIN: [
                "manage_members",
                "manage_workspaces",
                "create_resources",
                "delete_resources",
                "manage_permissions",
            ],
            TeamRole.MEMBER: [
                "create_resources",
                "edit_own_resources",
                "comment",
                "view_resources",
            ],
            TeamRole.VIEWER: ["view_resources", "comment"],
        }

    async def create_team(
        self,
        name: str,
        owner_id: int,
        description: Optional[str] = None,
        plan: str = "free",
    ) -> Dict[str, Any]:
        """
        Create a new team

        Args:
            name: Team name
            owner_id: User ID of team owner
            description: Team description
            plan: Subscription plan

        Returns:
            Created team
        """
        team_id = len(self.teams) + 1

        team = {
            "id": team_id,
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "plan": plan,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "member_count": 1,
            "workspace_count": 0,
        }

        self.teams[team_id] = team

        # Add owner as team member
        await self.add_team_member(
            team_id=team_id, user_id=owner_id, role=TeamRole.OWNER.value
        )

        # Log activity
        self._log_activity(
            team_id=team_id,
            user_id=owner_id,
            action="team_created",
            details={"team_name": name},
        )

        logger.info(f"Created team: {team_id} - {name}")

        return team

    async def get_team(self, team_id: int) -> Optional[Dict[str, Any]]:
        """Get team by ID"""
        return self.teams.get(team_id)

    async def list_teams(self, user_id: int) -> List[Dict[str, Any]]:
        """List all teams for a user"""
        user_teams = []

        for team in self.teams.values():
            # Check if user is a member
            members = await self.get_team_members(team["id"])
            if any(m["user_id"] == user_id for m in members):
                user_teams.append(team)

        return user_teams

    async def update_team(
        self,
        team_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        plan: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update team details"""
        team = self.teams.get(team_id)

        if not team:
            return None

        if name:
            team["name"] = name
        if description is not None:
            team["description"] = description
        if plan:
            team["plan"] = plan

        team["updated_at"] = datetime.now().isoformat()

        logger.info(f"Updated team: {team_id}")

        return team

    async def delete_team(self, team_id: int) -> bool:
        """Delete a team"""
        if team_id in self.teams:
            # Delete associated workspaces
            workspaces_to_delete = [
                ws_id
                for ws_id, ws in self.workspaces.items()
                if ws["team_id"] == team_id
            ]
            for ws_id in workspaces_to_delete:
                del self.workspaces[ws_id]

            del self.teams[team_id]
            logger.info(f"Deleted team: {team_id}")
            return True

        return False

    async def add_team_member(
        self, team_id: int, user_id: int, role: str = "member"
    ) -> Dict[str, Any]:
        """Add a member to a team"""
        member = {
            "team_id": team_id,
            "user_id": user_id,
            "role": role,
            "joined_at": datetime.now().isoformat(),
            "status": "active",
        }

        # Store in team data
        team = self.teams.get(team_id)
        if team:
            if "members" not in team:
                team["members"] = []
            team["members"].append(member)
            team["member_count"] = len(team["members"])

        # Log activity
        self._log_activity(
            team_id=team_id,
            user_id=user_id,
            action="member_added",
            details={"role": role},
        )

        logger.info(f"Added member {user_id} to team {team_id} with role {role}")

        return member

    async def remove_team_member(self, team_id: int, user_id: int) -> bool:
        """Remove a member from a team"""
        team = self.teams.get(team_id)

        if not team or "members" not in team:
            return False

        # Remove member
        team["members"] = [m for m in team["members"] if m["user_id"] != user_id]
        team["member_count"] = len(team["members"])

        # Log activity
        self._log_activity(
            team_id=team_id, user_id=user_id, action="member_removed", details={}
        )

        logger.info(f"Removed member {user_id} from team {team_id}")

        return True

    async def update_member_role(
        self, team_id: int, user_id: int, new_role: str
    ) -> bool:
        """Update a team member's role"""
        team = self.teams.get(team_id)

        if not team or "members" not in team:
            return False

        # Update role
        for member in team["members"]:
            if member["user_id"] == user_id:
                old_role = member["role"]
                member["role"] = new_role

                # Log activity
                self._log_activity(
                    team_id=team_id,
                    user_id=user_id,
                    action="role_updated",
                    details={"old_role": old_role, "new_role": new_role},
                )

                logger.info(
                    f"Updated member {user_id} role to {new_role} in team {team_id}"
                )
                return True

        return False

    async def get_team_members(self, team_id: int) -> List[Dict[str, Any]]:
        """Get all members of a team"""
        team = self.teams.get(team_id)

        if not team or "members" not in team:
            return []

        return team["members"]

    async def check_permission(
        self, team_id: int, user_id: int, permission: str
    ) -> bool:
        """Check if user has a specific permission"""
        members = await self.get_team_members(team_id)

        user_member = next((m for m in members if m["user_id"] == user_id), None)

        if not user_member:
            return False

        role = TeamRole(user_member["role"])

        # Owner has all permissions
        if role == TeamRole.OWNER:
            return True

        # Check role permissions
        return permission in self.permissions.get(role, [])

    async def create_workspace(
        self,
        team_id: int,
        name: str,
        description: Optional[str] = None,
        created_by: int = None,
    ) -> Dict[str, Any]:
        """Create a workspace for a team"""
        workspace_id = len(self.workspaces) + 1

        workspace = {
            "id": workspace_id,
            "team_id": team_id,
            "name": name,
            "description": description,
            "created_by": created_by,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resource_count": 0,
        }

        self.workspaces[workspace_id] = workspace

        # Update team workspace count
        team = self.teams.get(team_id)
        if team:
            team["workspace_count"] = team.get("workspace_count", 0) + 1

        # Log activity
        self._log_activity(
            team_id=team_id,
            user_id=created_by,
            action="workspace_created",
            details={"workspace_name": name},
        )

        logger.info(f"Created workspace: {workspace_id} - {name}")

        return workspace

    async def get_workspace(self, workspace_id: int) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        return self.workspaces.get(workspace_id)

    async def list_workspaces(self, team_id: int) -> List[Dict[str, Any]]:
        """List all workspaces for a team"""
        return [ws for ws in self.workspaces.values() if ws["team_id"] == team_id]

    async def update_workspace(
        self,
        workspace_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update workspace details"""
        workspace = self.workspaces.get(workspace_id)

        if not workspace:
            return None

        if name:
            workspace["name"] = name
        if description is not None:
            workspace["description"] = description

        workspace["updated_at"] = datetime.now().isoformat()

        logger.info(f"Updated workspace: {workspace_id}")

        return workspace

    async def delete_workspace(self, workspace_id: int) -> bool:
        """Delete a workspace"""
        if workspace_id in self.workspaces:
            workspace = self.workspaces[workspace_id]
            team_id = workspace["team_id"]

            del self.workspaces[workspace_id]

            # Update team workspace count
            team = self.teams.get(team_id)
            if team:
                team["workspace_count"] = max(0, team.get("workspace_count", 1) - 1)

            logger.info(f"Deleted workspace: {workspace_id}")
            return True

        return False

    async def add_comment(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        content: str,
        team_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Add a comment to a resource"""
        comment_id = len(self.comments) + 1

        comment = {
            "id": comment_id,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "content": content,
            "team_id": team_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "replies": [],
        }

        self.comments[comment_id] = comment

        # Log activity
        if team_id:
            self._log_activity(
                team_id=team_id,
                user_id=user_id,
                action="comment_added",
                details={"resource_type": resource_type, "resource_id": resource_id},
            )

        logger.info(f"Added comment: {comment_id}")

        return comment

    async def get_comments(
        self, resource_type: str, resource_id: int
    ) -> List[Dict[str, Any]]:
        """Get all comments for a resource"""
        return [
            c
            for c in self.comments.values()
            if c["resource_type"] == resource_type and c["resource_id"] == resource_id
        ]

    async def update_comment(
        self, comment_id: int, content: str
    ) -> Optional[Dict[str, Any]]:
        """Update a comment"""
        comment = self.comments.get(comment_id)

        if not comment:
            return None

        comment["content"] = content
        comment["updated_at"] = datetime.now().isoformat()

        logger.info(f"Updated comment: {comment_id}")

        return comment

    async def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment"""
        if comment_id in self.comments:
            del self.comments[comment_id]
            logger.info(f"Deleted comment: {comment_id}")
            return True

        return False

    async def get_team_activity(
        self, team_id: int, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get activity log for a team"""
        team_activities = [
            activity for activity in self.activity_log if activity["team_id"] == team_id
        ]

        # Sort by timestamp (most recent first)
        team_activities.sort(key=lambda x: x["timestamp"], reverse=True)

        return team_activities[:limit]

    def _log_activity(
        self, team_id: int, user_id: int, action: str, details: Dict[str, Any]
    ):
        """Log team activity"""
        activity = {
            "team_id": team_id,
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }

        self.activity_log.append(activity)

    async def invite_member(
        self, team_id: int, email: str, role: str, invited_by: int
    ) -> Dict[str, Any]:
        """Create an invitation for a new team member"""
        invitation = {
            "team_id": team_id,
            "email": email,
            "role": role,
            "invited_by": invited_by,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": None,  # Could add expiration logic
        }

        # Log activity
        self._log_activity(
            team_id=team_id,
            user_id=invited_by,
            action="member_invited",
            details={"email": email, "role": role},
        )

        logger.info(f"Invited {email} to team {team_id}")

        return invitation

    async def get_team_stats(self, team_id: int) -> Dict[str, Any]:
        """Get statistics for a team"""
        team = self.teams.get(team_id)

        if not team:
            return {}

        workspaces = await self.list_workspaces(team_id)
        members = await self.get_team_members(team_id)
        activities = await self.get_team_activity(team_id, limit=100)

        return {
            "member_count": len(members),
            "workspace_count": len(workspaces),
            "activity_count": len(activities),
            "plan": team["plan"],
            "created_at": team["created_at"],
        }
