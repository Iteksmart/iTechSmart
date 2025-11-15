"""
Action History Integration
Provides undo/redo capabilities for user actions
"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Supported action types"""
    CODE_GENERATION = "code_generation"
    FILE_MODIFICATION = "file_modification"
    FILE_CREATION = "file_creation"
    FILE_DELETION = "file_deletion"
    IMAGE_GENERATION = "image_generation"
    GITHUB_OPERATION = "github_operation"
    CONFIGURATION_CHANGE = "configuration_change"
    TASK_EXECUTION = "task_execution"
    DATA_VISUALIZATION = "data_visualization"
    DOCUMENT_PROCESSING = "document_processing"
    VM_OPERATION = "vm_operation"
    SCHEDULED_TASK = "scheduled_task"
    MCP_OPERATION = "mcp_operation"


class Action:
    """Represents a single action in history"""
    
    def __init__(
        self,
        action_id: str,
        action_type: ActionType,
        description: str,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        undoable: bool = True
    ):
        self.action_id = action_id
        self.action_type = action_type
        self.description = description
        self.previous_state = previous_state or {}
        self.new_state = new_state or {}
        self.metadata = metadata or {}
        self.undoable = undoable
        self.undone = False
        self.redone = False
        self.created_at = datetime.utcnow()
        self.bookmarked = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary"""
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "description": self.description,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "metadata": self.metadata,
            "undoable": self.undoable,
            "undone": self.undone,
            "redone": self.redone,
            "created_at": self.created_at.isoformat(),
            "bookmarked": self.bookmarked
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """Create action from dictionary"""
        action = cls(
            action_id=data["action_id"],
            action_type=ActionType(data["action_type"]),
            description=data["description"],
            previous_state=data.get("previous_state"),
            new_state=data.get("new_state"),
            metadata=data.get("metadata"),
            undoable=data.get("undoable", True)
        )
        action.undone = data.get("undone", False)
        action.redone = data.get("redone", False)
        action.bookmarked = data.get("bookmarked", False)
        if "created_at" in data:
            action.created_at = datetime.fromisoformat(data["created_at"])
        return action


class ActionHistoryManager:
    """Manages action history with undo/redo capabilities"""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.actions: List[Action] = []
        self.current_index = -1  # Points to the last executed action
        self.undo_handlers: Dict[ActionType, Callable] = {}
        self.redo_handlers: Dict[ActionType, Callable] = {}
        
    def register_undo_handler(
        self,
        action_type: ActionType,
        handler: Callable
    ):
        """Register undo handler for action type"""
        self.undo_handlers[action_type] = handler
        logger.info(f"Registered undo handler for {action_type}")
        
    def register_redo_handler(
        self,
        action_type: ActionType,
        handler: Callable
    ):
        """Register redo handler for action type"""
        self.redo_handlers[action_type] = handler
        logger.info(f"Registered redo handler for {action_type}")
        
    def add_action(
        self,
        action_type: ActionType,
        description: str,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        undoable: bool = True
    ) -> str:
        """Add new action to history"""
        # Generate unique action ID
        action_id = self._generate_action_id(action_type, description)
        
        # Create action
        action = Action(
            action_id=action_id,
            action_type=action_type,
            description=description,
            previous_state=previous_state,
            new_state=new_state,
            metadata=metadata,
            undoable=undoable
        )
        
        # Remove any actions after current index (they become unreachable)
        if self.current_index < len(self.actions) - 1:
            self.actions = self.actions[:self.current_index + 1]
            
        # Add new action
        self.actions.append(action)
        self.current_index += 1
        
        # Enforce max history size
        if len(self.actions) > self.max_history_size:
            removed = self.actions.pop(0)
            self.current_index -= 1
            logger.info(f"Removed oldest action: {removed.action_id}")
            
        logger.info(f"Added action: {action_id} ({action_type})")
        return action_id
        
    async def undo(self) -> Dict[str, Any]:
        """Undo the last action"""
        if self.current_index < 0:
            return {
                "success": False,
                "error": "No actions to undo"
            }
            
        action = self.actions[self.current_index]
        
        if not action.undoable:
            return {
                "success": False,
                "error": f"Action '{action.description}' is not undoable"
            }
            
        if action.undone:
            return {
                "success": False,
                "error": "Action already undone"
            }
            
        # Get undo handler
        handler = self.undo_handlers.get(action.action_type)
        if not handler:
            return {
                "success": False,
                "error": f"No undo handler registered for {action.action_type}"
            }
            
        try:
            # Execute undo
            result = await handler(action)
            
            if result.get("success"):
                action.undone = True
                action.redone = False
                self.current_index -= 1
                
                logger.info(f"Undone action: {action.action_id}")
                
                return {
                    "success": True,
                    "action": action.to_dict(),
                    "message": f"Undone: {action.description}"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to undo action {action.action_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def redo(self) -> Dict[str, Any]:
        """Redo the last undone action"""
        if self.current_index >= len(self.actions) - 1:
            return {
                "success": False,
                "error": "No actions to redo"
            }
            
        # Get next action (the one that was undone)
        next_action = self.actions[self.current_index + 1]
        
        if not next_action.undone:
            return {
                "success": False,
                "error": "Action was not undone"
            }
            
        # Get redo handler
        handler = self.redo_handlers.get(next_action.action_type)
        if not handler:
            return {
                "success": False,
                "error": f"No redo handler registered for {next_action.action_type}"
            }
            
        try:
            # Execute redo
            result = await handler(next_action)
            
            if result.get("success"):
                next_action.undone = False
                next_action.redone = True
                self.current_index += 1
                
                logger.info(f"Redone action: {next_action.action_id}")
                
                return {
                    "success": True,
                    "action": next_action.to_dict(),
                    "message": f"Redone: {next_action.description}"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to redo action {next_action.action_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def undo_multiple(self, count: int) -> Dict[str, Any]:
        """Undo multiple actions"""
        if count <= 0:
            return {
                "success": False,
                "error": "Count must be positive"
            }
            
        undone_actions = []
        errors = []
        
        for i in range(count):
            result = await self.undo()
            
            if result.get("success"):
                undone_actions.append(result["action"])
            else:
                errors.append(result.get("error"))
                break  # Stop on first error
                
        return {
            "success": len(undone_actions) > 0,
            "undone_count": len(undone_actions),
            "actions": undone_actions,
            "errors": errors
        }
        
    async def redo_multiple(self, count: int) -> Dict[str, Any]:
        """Redo multiple actions"""
        if count <= 0:
            return {
                "success": False,
                "error": "Count must be positive"
            }
            
        redone_actions = []
        errors = []
        
        for i in range(count):
            result = await self.redo()
            
            if result.get("success"):
                redone_actions.append(result["action"])
            else:
                errors.append(result.get("error"))
                break  # Stop on first error
                
        return {
            "success": len(redone_actions) > 0,
            "redone_count": len(redone_actions),
            "actions": redone_actions,
            "errors": errors
        }
        
    def get_history(
        self,
        limit: int = 100,
        offset: int = 0,
        action_type: Optional[ActionType] = None,
        include_undone: bool = True
    ) -> List[Dict[str, Any]]:
        """Get action history"""
        # Filter actions
        filtered_actions = self.actions
        
        if action_type:
            filtered_actions = [
                a for a in filtered_actions
                if a.action_type == action_type
            ]
            
        if not include_undone:
            filtered_actions = [
                a for a in filtered_actions
                if not a.undone
            ]
            
        # Apply pagination
        start = offset
        end = offset + limit
        paginated_actions = filtered_actions[start:end]
        
        return [action.to_dict() for action in paginated_actions]
        
    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get specific action by ID"""
        for action in self.actions:
            if action.action_id == action_id:
                return action.to_dict()
        return None
        
    def search_history(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search action history"""
        query_lower = query.lower()
        
        matching_actions = [
            action for action in self.actions
            if (query_lower in action.description.lower() or
                query_lower in action.action_type.lower() or
                query_lower in str(action.metadata).lower())
        ]
        
        return [action.to_dict() for action in matching_actions[:limit]]
        
    def bookmark_action(self, action_id: str) -> Dict[str, Any]:
        """Bookmark an action"""
        for action in self.actions:
            if action.action_id == action_id:
                action.bookmarked = True
                logger.info(f"Bookmarked action: {action_id}")
                return {
                    "success": True,
                    "message": f"Bookmarked: {action.description}"
                }
                
        return {
            "success": False,
            "error": "Action not found"
        }
        
    def unbookmark_action(self, action_id: str) -> Dict[str, Any]:
        """Remove bookmark from action"""
        for action in self.actions:
            if action.action_id == action_id:
                action.bookmarked = False
                logger.info(f"Unbookmarked action: {action_id}")
                return {
                    "success": True,
                    "message": f"Unbookmarked: {action.description}"
                }
                
        return {
            "success": False,
            "error": "Action not found"
        }
        
    def get_bookmarked_actions(self) -> List[Dict[str, Any]]:
        """Get all bookmarked actions"""
        bookmarked = [
            action for action in self.actions
            if action.bookmarked
        ]
        return [action.to_dict() for action in bookmarked]
        
    def clear_history(
        self,
        keep_bookmarked: bool = True
    ) -> Dict[str, Any]:
        """Clear action history"""
        if keep_bookmarked:
            # Keep only bookmarked actions
            bookmarked = [a for a in self.actions if a.bookmarked]
            removed_count = len(self.actions) - len(bookmarked)
            self.actions = bookmarked
            self.current_index = len(self.actions) - 1
            
            logger.info(f"Cleared {removed_count} actions, kept {len(bookmarked)} bookmarked")
            
            return {
                "success": True,
                "message": f"Cleared {removed_count} actions, kept {len(bookmarked)} bookmarked"
            }
        else:
            # Clear all actions
            count = len(self.actions)
            self.actions = []
            self.current_index = -1
            
            logger.info(f"Cleared all {count} actions")
            
            return {
                "success": True,
                "message": f"Cleared all {count} actions"
            }
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics"""
        total_actions = len(self.actions)
        undone_actions = sum(1 for a in self.actions if a.undone)
        bookmarked_actions = sum(1 for a in self.actions if a.bookmarked)
        
        # Count by action type
        action_type_counts = {}
        for action in self.actions:
            action_type = action.action_type
            action_type_counts[action_type] = action_type_counts.get(action_type, 0) + 1
            
        return {
            "total_actions": total_actions,
            "active_actions": total_actions - undone_actions,
            "undone_actions": undone_actions,
            "bookmarked_actions": bookmarked_actions,
            "current_index": self.current_index,
            "can_undo": self.current_index >= 0,
            "can_redo": self.current_index < len(self.actions) - 1,
            "action_type_counts": action_type_counts,
            "max_history_size": self.max_history_size
        }
        
    def export_history(
        self,
        format: str = "json",
        include_undone: bool = True
    ) -> str:
        """Export action history"""
        actions = self.get_history(
            limit=len(self.actions),
            include_undone=include_undone
        )
        
        if format == "json":
            return json.dumps(actions, indent=2)
        elif format == "csv":
            # Simple CSV export
            lines = ["action_id,action_type,description,created_at,undone,bookmarked"]
            for action in actions:
                lines.append(
                    f"{action['action_id']},"
                    f"{action['action_type']},"
                    f"&quot;{action['description']}&quot;,"
                    f"{action['created_at']},"
                    f"{action['undone']},"
                    f"{action['bookmarked']}"
                )
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _generate_action_id(
        self,
        action_type: ActionType,
        description: str
    ) -> str:
        """Generate unique action ID"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{action_type}:{description}:{timestamp}"
        hash_value = hashlib.md5(data.encode()).hexdigest()[:12]
        return f"action_{hash_value}"


# Global action history manager
action_history_manager = ActionHistoryManager()


# Default undo/redo handlers
async def default_file_modification_undo(action: Action) -> Dict[str, Any]:
    """Default undo handler for file modifications"""
    try:
        file_path = action.metadata.get("file_path")
        previous_content = action.previous_state.get("content")
        
        if not file_path or previous_content is None:
            return {
                "success": False,
                "error": "Missing file path or previous content"
            }
            
        # Restore previous content
        import aiofiles
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(previous_content)
            
        return {
            "success": True,
            "message": f"Restored {file_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def default_file_modification_redo(action: Action) -> Dict[str, Any]:
    """Default redo handler for file modifications"""
    try:
        file_path = action.metadata.get("file_path")
        new_content = action.new_state.get("content")
        
        if not file_path or new_content is None:
            return {
                "success": False,
                "error": "Missing file path or new content"
            }
            
        # Apply new content
        import aiofiles
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(new_content)
            
        return {
            "success": True,
            "message": f"Reapplied changes to {file_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Register default handlers
action_history_manager.register_undo_handler(
    ActionType.FILE_MODIFICATION,
    default_file_modification_undo
)
action_history_manager.register_redo_handler(
    ActionType.FILE_MODIFICATION,
    default_file_modification_redo
)