"""
Tests for Team Collaboration functionality
"""

import pytest
from app.integrations.collaboration import CollaborationManager, TeamRole


@pytest.fixture
def collab_manager():
    """Create collaboration manager instance"""
    return CollaborationManager()


class TestTeamManagement:
    """Test team management functionality"""
    
    @pytest.mark.asyncio
    async def test_create_team(self, collab_manager):
        """Test creating a team"""
        team = await collab_manager.create_team(
            name="Test Team",
            owner_id=1,
            description="A test team",
            plan="free"
        )
        
        assert team["name"] == "Test Team"
        assert team["owner_id"] == 1
        assert team["plan"] == "free"
        assert team["member_count"] == 1
    
    @pytest.mark.asyncio
    async def test_get_team(self, collab_manager):
        """Test getting a team"""
        created = await collab_manager.create_team("Test Team", 1)
        retrieved = await collab_manager.get_team(created["id"])
        
        assert retrieved is not None
        assert retrieved["id"] == created["id"]
    
    @pytest.mark.asyncio
    async def test_list_teams(self, collab_manager):
        """Test listing teams"""
        await collab_manager.create_team("Team 1", 1)
        await collab_manager.create_team("Team 2", 1)
        
        teams = await collab_manager.list_teams(1)
        
        assert len(teams) >= 2
    
    @pytest.mark.asyncio
    async def test_update_team(self, collab_manager):
        """Test updating a team"""
        team = await collab_manager.create_team("Original Name", 1)
        
        updated = await collab_manager.update_team(
            team_id=team["id"],
            name="Updated Name",
            description="Updated description"
        )
        
        assert updated["name"] == "Updated Name"
        assert updated["description"] == "Updated description"
    
    @pytest.mark.asyncio
    async def test_delete_team(self, collab_manager):
        """Test deleting a team"""
        team = await collab_manager.create_team("Test Team", 1)
        
        success = await collab_manager.delete_team(team["id"])
        
        assert success is True
        
        retrieved = await collab_manager.get_team(team["id"])
        assert retrieved is None


class TestTeamMembers:
    """Test team member management"""
    
    @pytest.mark.asyncio
    async def test_add_member(self, collab_manager):
        """Test adding a team member"""
        team = await collab_manager.create_team("Test Team", 1)
        
        member = await collab_manager.add_team_member(
            team_id=team["id"],
            user_id=2,
            role="member"
        )
        
        assert member["user_id"] == 2
        assert member["role"] == "member"
    
    @pytest.mark.asyncio
    async def test_get_team_members(self, collab_manager):
        """Test getting team members"""
        team = await collab_manager.create_team("Test Team", 1)
        await collab_manager.add_team_member(team["id"], 2, "member")
        
        members = await collab_manager.get_team_members(team["id"])
        
        assert len(members) == 2  # Owner + added member
    
    @pytest.mark.asyncio
    async def test_remove_member(self, collab_manager):
        """Test removing a team member"""
        team = await collab_manager.create_team("Test Team", 1)
        await collab_manager.add_team_member(team["id"], 2, "member")
        
        success = await collab_manager.remove_team_member(team["id"], 2)
        
        assert success is True
        
        members = await collab_manager.get_team_members(team["id"])
        assert len(members) == 1  # Only owner remains
    
    @pytest.mark.asyncio
    async def test_update_member_role(self, collab_manager):
        """Test updating member role"""
        team = await collab_manager.create_team("Test Team", 1)
        await collab_manager.add_team_member(team["id"], 2, "member")
        
        success = await collab_manager.update_member_role(team["id"], 2, "admin")
        
        assert success is True
        
        members = await collab_manager.get_team_members(team["id"])
        member = next(m for m in members if m["user_id"] == 2)
        assert member["role"] == "admin"


class TestPermissions:
    """Test permission system"""
    
    @pytest.mark.asyncio
    async def test_owner_has_all_permissions(self, collab_manager):
        """Test that owner has all permissions"""
        team = await collab_manager.create_team("Test Team", 1)
        
        has_permission = await collab_manager.check_permission(
            team["id"], 1, "manage_team"
        )
        
        assert has_permission is True
    
    @pytest.mark.asyncio
    async def test_member_limited_permissions(self, collab_manager):
        """Test that member has limited permissions"""
        team = await collab_manager.create_team("Test Team", 1)
        await collab_manager.add_team_member(team["id"], 2, "member")
        
        has_permission = await collab_manager.check_permission(
            team["id"], 2, "delete_team"
        )
        
        assert has_permission is False


class TestWorkspaces:
    """Test workspace management"""
    
    @pytest.mark.asyncio
    async def test_create_workspace(self, collab_manager):
        """Test creating a workspace"""
        team = await collab_manager.create_team("Test Team", 1)
        
        workspace = await collab_manager.create_workspace(
            team_id=team["id"],
            name="Test Workspace",
            description="A test workspace",
            created_by=1
        )
        
        assert workspace["name"] == "Test Workspace"
        assert workspace["team_id"] == team["id"]
    
    @pytest.mark.asyncio
    async def test_list_workspaces(self, collab_manager):
        """Test listing workspaces"""
        team = await collab_manager.create_team("Test Team", 1)
        await collab_manager.create_workspace(team["id"], "Workspace 1", created_by=1)
        await collab_manager.create_workspace(team["id"], "Workspace 2", created_by=1)
        
        workspaces = await collab_manager.list_workspaces(team["id"])
        
        assert len(workspaces) == 2
    
    @pytest.mark.asyncio
    async def test_update_workspace(self, collab_manager):
        """Test updating a workspace"""
        team = await collab_manager.create_team("Test Team", 1)
        workspace = await collab_manager.create_workspace(
            team["id"], "Original Name", created_by=1
        )
        
        updated = await collab_manager.update_workspace(
            workspace_id=workspace["id"],
            name="Updated Name"
        )
        
        assert updated["name"] == "Updated Name"
    
    @pytest.mark.asyncio
    async def test_delete_workspace(self, collab_manager):
        """Test deleting a workspace"""
        team = await collab_manager.create_team("Test Team", 1)
        workspace = await collab_manager.create_workspace(
            team["id"], "Test Workspace", created_by=1
        )
        
        success = await collab_manager.delete_workspace(workspace["id"])
        
        assert success is True


class TestComments:
    """Test comment functionality"""
    
    @pytest.mark.asyncio
    async def test_add_comment(self, collab_manager):
        """Test adding a comment"""
        comment = await collab_manager.add_comment(
            user_id=1,
            resource_type="code",
            resource_id=1,
            content="Test comment"
        )
        
        assert comment["content"] == "Test comment"
        assert comment["resource_type"] == "code"
    
    @pytest.mark.asyncio
    async def test_get_comments(self, collab_manager):
        """Test getting comments"""
        await collab_manager.add_comment(1, "code", 1, "Comment 1")
        await collab_manager.add_comment(1, "code", 1, "Comment 2")
        
        comments = await collab_manager.get_comments("code", 1)
        
        assert len(comments) == 2
    
    @pytest.mark.asyncio
    async def test_update_comment(self, collab_manager):
        """Test updating a comment"""
        comment = await collab_manager.add_comment(
            1, "code", 1, "Original content"
        )
        
        updated = await collab_manager.update_comment(
            comment["id"], "Updated content"
        )
        
        assert updated["content"] == "Updated content"
    
    @pytest.mark.asyncio
    async def test_delete_comment(self, collab_manager):
        """Test deleting a comment"""
        comment = await collab_manager.add_comment(1, "code", 1, "Test comment")
        
        success = await collab_manager.delete_comment(comment["id"])
        
        assert success is True


class TestActivity:
    """Test activity logging"""
    
    @pytest.mark.asyncio
    async def test_activity_logged(self, collab_manager):
        """Test that activities are logged"""
        team = await collab_manager.create_team("Test Team", 1)
        
        activities = await collab_manager.get_team_activity(team["id"])
        
        assert len(activities) > 0
        assert activities[0]["action"] == "team_created"
    
    @pytest.mark.asyncio
    async def test_get_team_stats(self, collab_manager):
        """Test getting team statistics"""
        team = await collab_manager.create_team("Test Team", 1)
        await collab_manager.add_team_member(team["id"], 2, "member")
        await collab_manager.create_workspace(team["id"], "Workspace 1", created_by=1)
        
        stats = await collab_manager.get_team_stats(team["id"])
        
        assert stats["member_count"] == 2
        assert stats["workspace_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])