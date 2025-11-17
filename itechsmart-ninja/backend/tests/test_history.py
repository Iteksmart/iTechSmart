"""
Tests for Action History Integration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from app.integrations.action_history import ActionHistoryManager, Action, ActionType


@pytest.fixture
def history_manager():
    """Create action history manager instance"""
    return ActionHistoryManager(max_history_size=100)


def test_add_action(history_manager):
    """Test adding action to history"""
    action_id = history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION,
        description="Modified main.py",
        previous_state={"content": "old"},
        new_state={"content": "new"},
        metadata={"file_path": "/path/to/main.py"},
    )

    assert action_id is not None
    assert len(history_manager.actions) == 1
    assert history_manager.current_index == 0


def test_add_multiple_actions(history_manager):
    """Test adding multiple actions"""
    for i in range(5):
        history_manager.add_action(
            action_type=ActionType.FILE_MODIFICATION,
            description=f"Action {i}",
            undoable=True,
        )

    assert len(history_manager.actions) == 5
    assert history_manager.current_index == 4


@pytest.mark.asyncio
async def test_undo_action(history_manager):
    """Test undoing an action"""
    # Register mock undo handler
    mock_handler = AsyncMock(return_value={"success": True})
    history_manager.register_undo_handler(ActionType.FILE_MODIFICATION, mock_handler)

    # Add action
    history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION,
        description="Test action",
        undoable=True,
    )

    # Undo
    result = await history_manager.undo()

    assert result["success"] is True
    assert history_manager.current_index == -1
    assert history_manager.actions[0].undone is True


@pytest.mark.asyncio
async def test_undo_no_actions(history_manager):
    """Test undoing when no actions available"""
    result = await history_manager.undo()

    assert result["success"] is False
    assert "No actions to undo" in result["error"]


@pytest.mark.asyncio
async def test_redo_action(history_manager):
    """Test redoing an action"""
    # Register mock handlers
    mock_undo = AsyncMock(return_value={"success": True})
    mock_redo = AsyncMock(return_value={"success": True})
    history_manager.register_undo_handler(ActionType.FILE_MODIFICATION, mock_undo)
    history_manager.register_redo_handler(ActionType.FILE_MODIFICATION, mock_redo)

    # Add and undo action
    history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION,
        description="Test action",
        undoable=True,
    )
    await history_manager.undo()

    # Redo
    result = await history_manager.redo()

    assert result["success"] is True
    assert history_manager.current_index == 0
    assert history_manager.actions[0].undone is False


@pytest.mark.asyncio
async def test_redo_no_actions(history_manager):
    """Test redoing when no actions available"""
    result = await history_manager.redo()

    assert result["success"] is False
    assert "No actions to redo" in result["error"]


@pytest.mark.asyncio
async def test_undo_multiple_actions(history_manager):
    """Test undoing multiple actions"""
    # Register mock handler
    mock_handler = AsyncMock(return_value={"success": True})
    history_manager.register_undo_handler(ActionType.FILE_MODIFICATION, mock_handler)

    # Add multiple actions
    for i in range(5):
        history_manager.add_action(
            action_type=ActionType.FILE_MODIFICATION,
            description=f"Action {i}",
            undoable=True,
        )

    # Undo 3 actions
    result = await history_manager.undo_multiple(3)

    assert result["success"] is True
    assert result["undone_count"] == 3
    assert history_manager.current_index == 1


@pytest.mark.asyncio
async def test_redo_multiple_actions(history_manager):
    """Test redoing multiple actions"""
    # Register mock handlers
    mock_undo = AsyncMock(return_value={"success": True})
    mock_redo = AsyncMock(return_value={"success": True})
    history_manager.register_undo_handler(ActionType.FILE_MODIFICATION, mock_undo)
    history_manager.register_redo_handler(ActionType.FILE_MODIFICATION, mock_redo)

    # Add and undo multiple actions
    for i in range(5):
        history_manager.add_action(
            action_type=ActionType.FILE_MODIFICATION,
            description=f"Action {i}",
            undoable=True,
        )
    await history_manager.undo_multiple(3)

    # Redo 2 actions
    result = await history_manager.redo_multiple(2)

    assert result["success"] is True
    assert result["redone_count"] == 2
    assert history_manager.current_index == 3


def test_get_history(history_manager):
    """Test getting action history"""
    # Add actions
    for i in range(10):
        history_manager.add_action(
            action_type=ActionType.FILE_MODIFICATION,
            description=f"Action {i}",
            undoable=True,
        )

    # Get history with limit
    history = history_manager.get_history(limit=5)

    assert len(history) == 5


def test_get_history_with_filter(history_manager):
    """Test getting filtered history"""
    # Add different types of actions
    history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="File action"
    )
    history_manager.add_action(
        action_type=ActionType.IMAGE_GENERATION, description="Image action"
    )

    # Filter by type
    history = history_manager.get_history(action_type=ActionType.FILE_MODIFICATION)

    assert len(history) == 1
    assert history[0]["action_type"] == ActionType.FILE_MODIFICATION


def test_get_action(history_manager):
    """Test getting specific action"""
    action_id = history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Test action"
    )

    action = history_manager.get_action(action_id)

    assert action is not None
    assert action["action_id"] == action_id


def test_search_history(history_manager):
    """Test searching action history"""
    # Add actions
    history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Modified main.py"
    )
    history_manager.add_action(
        action_type=ActionType.IMAGE_GENERATION, description="Generated image"
    )

    # Search
    results = history_manager.search_history("main.py")

    assert len(results) == 1
    assert "main.py" in results[0]["description"]


def test_bookmark_action(history_manager):
    """Test bookmarking an action"""
    action_id = history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Important action"
    )

    result = history_manager.bookmark_action(action_id)

    assert result["success"] is True
    assert history_manager.actions[0].bookmarked is True


def test_unbookmark_action(history_manager):
    """Test removing bookmark"""
    action_id = history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Important action"
    )
    history_manager.bookmark_action(action_id)

    result = history_manager.unbookmark_action(action_id)

    assert result["success"] is True
    assert history_manager.actions[0].bookmarked is False


def test_get_bookmarked_actions(history_manager):
    """Test getting bookmarked actions"""
    # Add and bookmark actions
    action_id1 = history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Action 1"
    )
    action_id2 = history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Action 2"
    )

    history_manager.bookmark_action(action_id1)

    bookmarks = history_manager.get_bookmarked_actions()

    assert len(bookmarks) == 1
    assert bookmarks[0]["action_id"] == action_id1


def test_clear_history(history_manager):
    """Test clearing history"""
    # Add actions
    for i in range(5):
        history_manager.add_action(
            action_type=ActionType.FILE_MODIFICATION, description=f"Action {i}"
        )

    result = history_manager.clear_history(keep_bookmarked=False)

    assert result["success"] is True
    assert len(history_manager.actions) == 0
    assert history_manager.current_index == -1


def test_clear_history_keep_bookmarks(history_manager):
    """Test clearing history while keeping bookmarks"""
    # Add actions and bookmark one
    action_id1 = history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Action 1"
    )
    history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Action 2"
    )

    history_manager.bookmark_action(action_id1)

    result = history_manager.clear_history(keep_bookmarked=True)

    assert result["success"] is True
    assert len(history_manager.actions) == 1
    assert history_manager.actions[0].bookmarked is True


def test_get_statistics(history_manager):
    """Test getting statistics"""
    # Add actions
    for i in range(5):
        history_manager.add_action(
            action_type=ActionType.FILE_MODIFICATION, description=f"Action {i}"
        )

    stats = history_manager.get_statistics()

    assert stats["total_actions"] == 5
    assert stats["active_actions"] == 5
    assert stats["can_undo"] is True
    assert stats["can_redo"] is False


def test_export_history_json(history_manager):
    """Test exporting history as JSON"""
    # Add actions
    history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Test action"
    )

    exported = history_manager.export_history(format="json")

    assert exported is not None
    assert "Test action" in exported


def test_export_history_csv(history_manager):
    """Test exporting history as CSV"""
    # Add actions
    history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION, description="Test action"
    )

    exported = history_manager.export_history(format="csv")

    assert exported is not None
    assert "action_id" in exported
    assert "Test action" in exported


def test_max_history_size(history_manager):
    """Test max history size enforcement"""
    # Set small max size
    history_manager.max_history_size = 5

    # Add more actions than max
    for i in range(10):
        history_manager.add_action(
            action_type=ActionType.FILE_MODIFICATION, description=f"Action {i}"
        )

    # Should only keep last 5
    assert len(history_manager.actions) == 5
    assert history_manager.actions[0].description == "Action 5"


def test_action_to_dict():
    """Test converting action to dictionary"""
    action = Action(
        action_id="test_123",
        action_type=ActionType.FILE_MODIFICATION,
        description="Test action",
        previous_state={"content": "old"},
        new_state={"content": "new"},
        metadata={"file": "test.py"},
    )

    action_dict = action.to_dict()

    assert action_dict["action_id"] == "test_123"
    assert action_dict["action_type"] == ActionType.FILE_MODIFICATION
    assert action_dict["description"] == "Test action"


def test_action_from_dict():
    """Test creating action from dictionary"""
    data = {
        "action_id": "test_123",
        "action_type": "file_modification",
        "description": "Test action",
        "previous_state": {"content": "old"},
        "new_state": {"content": "new"},
        "metadata": {"file": "test.py"},
        "undoable": True,
        "undone": False,
        "bookmarked": False,
        "created_at": datetime.utcnow().isoformat(),
    }

    action = Action.from_dict(data)

    assert action.action_id == "test_123"
    assert action.action_type == ActionType.FILE_MODIFICATION
    assert action.description == "Test action"


@pytest.mark.asyncio
async def test_undo_non_undoable_action(history_manager):
    """Test undoing non-undoable action"""
    # Register mock handler
    mock_handler = AsyncMock(return_value={"success": True})
    history_manager.register_undo_handler(ActionType.FILE_MODIFICATION, mock_handler)

    # Add non-undoable action
    history_manager.add_action(
        action_type=ActionType.FILE_MODIFICATION,
        description="Non-undoable action",
        undoable=False,
    )

    # Try to undo
    result = await history_manager.undo()

    assert result["success"] is False
    assert "not undoable" in result["error"]
