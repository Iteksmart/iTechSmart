"""
Tests for Workflow Engine functionality
"""

import pytest
from app.integrations.workflow_engine import (
    WorkflowEngine,
    NodeType,
    ActionType,
    WorkflowStatus,
)


@pytest.fixture
def engine():
    """Create workflow engine instance"""
    return WorkflowEngine()


class TestWorkflowCreation:
    """Test workflow creation functionality"""

    @pytest.mark.asyncio
    async def test_create_simple_workflow(self, engine):
        """Test creating a simple workflow"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 100, "y": 0},
                "next_nodes": [],
            },
        ]

        workflow = await engine.create_workflow(
            name="Test Workflow", description="A test workflow", nodes=nodes
        )

        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
        assert len(workflow.nodes) == 2
        assert workflow.version == 1

    @pytest.mark.asyncio
    async def test_create_workflow_with_variables(self, engine):
        """Test creating workflow with variables"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 100, "y": 0},
                "next_nodes": [],
            },
        ]

        variables = {"test_var": "test_value"}

        workflow = await engine.create_workflow(
            name="Test Workflow",
            description="A test workflow",
            nodes=nodes,
            variables=variables,
        )

        assert workflow.variables == variables


class TestWorkflowManagement:
    """Test workflow management functionality"""

    @pytest.mark.asyncio
    async def test_get_workflow(self, engine):
        """Test getting a workflow"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 100, "y": 0},
                "next_nodes": [],
            },
        ]

        created = await engine.create_workflow(
            name="Test Workflow", description="A test workflow", nodes=nodes
        )

        retrieved = await engine.get_workflow(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name

    @pytest.mark.asyncio
    async def test_list_workflows(self, engine):
        """Test listing workflows"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 100, "y": 0},
                "next_nodes": [],
            },
        ]

        await engine.create_workflow("Workflow 1", "Description 1", nodes)
        await engine.create_workflow("Workflow 2", "Description 2", nodes)

        workflows = await engine.list_workflows()

        assert len(workflows) >= 2

    @pytest.mark.asyncio
    async def test_update_workflow(self, engine):
        """Test updating a workflow"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 100, "y": 0},
                "next_nodes": [],
            },
        ]

        workflow = await engine.create_workflow(
            name="Original Name", description="Original Description", nodes=nodes
        )

        updated = await engine.update_workflow(
            workflow_id=workflow.id,
            name="Updated Name",
            description="Updated Description",
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.description == "Updated Description"
        assert updated.version == 2

    @pytest.mark.asyncio
    async def test_delete_workflow(self, engine):
        """Test deleting a workflow"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 100, "y": 0},
                "next_nodes": [],
            },
        ]

        workflow = await engine.create_workflow(
            name="Test Workflow", description="A test workflow", nodes=nodes
        )

        success = await engine.delete_workflow(workflow.id)

        assert success is True

        retrieved = await engine.get_workflow(workflow.id)
        assert retrieved is None


class TestWorkflowExecution:
    """Test workflow execution functionality"""

    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self, engine):
        """Test executing a simple workflow"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 100, "y": 0},
                "next_nodes": [],
            },
        ]

        workflow = await engine.create_workflow(
            name="Test Workflow", description="A test workflow", nodes=nodes
        )

        execution = await engine.execute_workflow(workflow.id)

        assert execution.workflow_id == workflow.id
        assert execution.status == WorkflowStatus.COMPLETED
        assert len(execution.logs) > 0

    @pytest.mark.asyncio
    async def test_execute_workflow_with_action(self, engine):
        """Test executing workflow with action node"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["action"],
            },
            {
                "id": "action",
                "type": "action",
                "name": "Test Action",
                "config": {"action_type": "code_execution", "code": "result = 42"},
                "position": {"x": 100, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 200, "y": 0},
                "next_nodes": [],
            },
        ]

        workflow = await engine.create_workflow(
            name="Test Workflow", description="A test workflow", nodes=nodes
        )

        execution = await engine.execute_workflow(workflow.id)

        assert execution.status == WorkflowStatus.COMPLETED
        assert "action_result" in execution.context

    @pytest.mark.asyncio
    async def test_get_execution_history(self, engine):
        """Test getting execution history"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 100, "y": 0},
                "next_nodes": [],
            },
        ]

        workflow = await engine.create_workflow(
            name="Test Workflow", description="A test workflow", nodes=nodes
        )

        # Execute multiple times
        await engine.execute_workflow(workflow.id)
        await engine.execute_workflow(workflow.id)

        history = await engine.get_execution_history(workflow.id)

        assert len(history) == 2


class TestWorkflowTemplates:
    """Test workflow template functionality"""

    @pytest.mark.asyncio
    async def test_get_templates(self, engine):
        """Test getting workflow templates"""
        templates = await engine.get_templates()

        assert len(templates) > 0
        assert any(t.id == "template_data_processing" for t in templates)

    @pytest.mark.asyncio
    async def test_create_from_template(self, engine):
        """Test creating workflow from template"""
        workflow = await engine.create_from_template(
            template_id="template_data_processing", name="My Data Pipeline"
        )

        assert workflow is not None
        assert workflow.name == "My Data Pipeline"
        assert len(workflow.nodes) > 0


class TestActionHandlers:
    """Test action handler functionality"""

    @pytest.mark.asyncio
    async def test_code_execution_handler(self, engine):
        """Test code execution handler"""
        config = {"code": "result = 10 + 20"}
        context = {}

        result = await engine._handle_code_execution(config, context)

        # Handler should execute code
        assert result is not None or "result" in context

    @pytest.mark.asyncio
    async def test_notification_handler(self, engine):
        """Test notification handler"""
        config = {"message": "Test notification", "channel": "test"}
        context = {}

        result = await engine._handle_notification(config, context)

        assert result is not None
        assert result.get("sent") is True

    def test_register_custom_handler(self, engine):
        """Test registering custom action handler"""

        async def custom_handler(config, context):
            return {"custom": True}

        engine.register_action_handler("custom_action", custom_handler)

        assert "custom_action" in engine.action_handlers


class TestNodeTypes:
    """Test different node types"""

    @pytest.mark.asyncio
    async def test_delay_node(self, engine):
        """Test delay node execution"""
        nodes = [
            {
                "id": "start",
                "type": "start",
                "name": "Start",
                "config": {},
                "position": {"x": 0, "y": 0},
                "next_nodes": ["delay"],
            },
            {
                "id": "delay",
                "type": "delay",
                "name": "Delay",
                "config": {"delay": 0.1},
                "position": {"x": 100, "y": 0},
                "next_nodes": ["end"],
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "config": {},
                "position": {"x": 200, "y": 0},
                "next_nodes": [],
            },
        ]

        workflow = await engine.create_workflow(
            name="Delay Test", description="Test delay node", nodes=nodes
        )

        execution = await engine.execute_workflow(workflow.id)

        assert execution.status == WorkflowStatus.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
