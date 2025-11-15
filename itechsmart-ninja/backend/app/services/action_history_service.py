"""
Action History and Undo/Redo Service
Tracks AI actions and provides rollback capabilities
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import json
import logging
from collections import deque

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Types of actions that can be undone"""
    FILE_CREATE = "file_create"
    FILE_EDIT = "file_edit"
    FILE_DELETE = "file_delete"
    FILE_MOVE = "file_move"
    CODE_GENERATION = "code_generation"
    TEXT_GENERATION = "text_generation"
    IMAGE_EDIT = "image_edit"
    DATA_TRANSFORMATION = "data_transformation"
    API_CALL = "api_call"
    WORKFLOW_EXECUTION = "workflow_execution"
    AGENT_ACTION = "agent_action"
    SYSTEM_COMMAND = "system_command"


class ActionStatus(str, Enum):
    """Action execution status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    UNDONE = "undone"
    REDONE = "redone"


@dataclass
class ActionSnapshot:
    """Snapshot of state before action"""
    snapshot_id: str
    action_id: str
    timestamp: datetime
    state_data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "action_id": self.action_id,
            "timestamp": self.timestamp.isoformat(),
            "state_data": self.state_data,
            "metadata": self.metadata
        }


@dataclass
class Action:
    """Represents a single AI action"""
    action_id: str
    workspace_id: str
    user_id: str
    action_type: ActionType
    description: str
    timestamp: datetime
    status: ActionStatus
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    before_snapshot: Optional[ActionSnapshot]
    after_snapshot: Optional[ActionSnapshot]
    parent_action_id: Optional[str]
    child_action_ids: List[str]
    can_undo: bool
    can_redo: bool
    undo_handler: Optional[str]
    redo_handler: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "action_type": self.action_type.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "parameters": self.parameters,
            "result": self.result,
            "error": self.error,
            "before_snapshot": self.before_snapshot.to_dict() if self.before_snapshot else None,
            "after_snapshot": self.after_snapshot.to_dict() if self.after_snapshot else None,
            "parent_action_id": self.parent_action_id,
            "child_action_ids": self.child_action_ids,
            "can_undo": self.can_undo,
            "can_redo": self.can_redo
        }


@dataclass
class ActionGroup:
    """Group of related actions"""
    group_id: str
    workspace_id: str
    name: str
    description: str
    created_at: datetime
    action_ids: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Checkpoint:
    """System checkpoint for rollback"""
    checkpoint_id: str
    workspace_id: str
    name: str
    description: str
    created_at: datetime
    state_snapshot: Dict[str, Any]
    action_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "action_count": self.action_count
        }


class ActionHistoryService:
    """Manages action history and undo/redo operations"""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.actions: Dict[str, Action] = {}
        self.workspace_actions: Dict[str, deque] = {}  # workspace_id -> action_ids
        self.undo_stacks: Dict[str, List[str]] = {}  # workspace_id -> action_ids
        self.redo_stacks: Dict[str, List[str]] = {}  # workspace_id -> action_ids
        self.action_groups: Dict[str, ActionGroup] = {}
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.workspace_checkpoints: Dict[str, List[str]] = {}  # workspace_id -> checkpoint_ids
        
        # Register undo/redo handlers
        self.undo_handlers: Dict[str, Callable] = {}
        self.redo_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default undo/redo handlers"""
        # File operations
        self.undo_handlers["file_create"] = self._undo_file_create
        self.redo_handlers["file_create"] = self._redo_file_create
        
        self.undo_handlers["file_edit"] = self._undo_file_edit
        self.redo_handlers["file_edit"] = self._redo_file_edit
        
        self.undo_handlers["file_delete"] = self._undo_file_delete
        self.redo_handlers["file_delete"] = self._redo_file_delete
    
    def record_action(
        self,
        workspace_id: str,
        user_id: str,
        action_type: ActionType,
        description: str,
        parameters: Dict[str, Any],
        before_state: Optional[Dict[str, Any]] = None,
        can_undo: bool = True,
        undo_handler: Optional[str] = None,
        redo_handler: Optional[str] = None,
        parent_action_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record a new action"""
        try:
            action_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Create before snapshot if state provided
            before_snapshot = None
            if before_state:
                snapshot_id = str(uuid.uuid4())
                before_snapshot = ActionSnapshot(
                    snapshot_id=snapshot_id,
                    action_id=action_id,
                    timestamp=now,
                    state_data=before_state,
                    metadata={}
                )
            
            action = Action(
                action_id=action_id,
                workspace_id=workspace_id,
                user_id=user_id,
                action_type=action_type,
                description=description,
                timestamp=now,
                status=ActionStatus.PENDING,
                parameters=parameters,
                result=None,
                error=None,
                before_snapshot=before_snapshot,
                after_snapshot=None,
                parent_action_id=parent_action_id,
                child_action_ids=[],
                can_undo=can_undo,
                can_redo=False,
                undo_handler=undo_handler,
                redo_handler=redo_handler
            )
            
            self.actions[action_id] = action
            
            # Add to workspace history
            if workspace_id not in self.workspace_actions:
                self.workspace_actions[workspace_id] = deque(maxlen=self.max_history_size)
            self.workspace_actions[workspace_id].append(action_id)
            
            # Initialize undo/redo stacks
            if workspace_id not in self.undo_stacks:
                self.undo_stacks[workspace_id] = []
            if workspace_id not in self.redo_stacks:
                self.redo_stacks[workspace_id] = []
            
            # Link to parent action
            if parent_action_id and parent_action_id in self.actions:
                self.actions[parent_action_id].child_action_ids.append(action_id)
            
            logger.info(f"Recorded action {action_id}: {description}")
            
            return {
                "success": True,
                "action": action.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to record action: {e}")
            return {"success": False, "error": str(e)}
    
    def complete_action(
        self,
        action_id: str,
        result: Dict[str, Any],
        after_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mark action as completed"""
        action = self.actions.get(action_id)
        if not action:
            return {"success": False, "error": "Action not found"}
        
        try:
            action.status = ActionStatus.COMPLETED
            action.result = result
            
            # Create after snapshot if state provided
            if after_state:
                snapshot_id = str(uuid.uuid4())
                action.after_snapshot = ActionSnapshot(
                    snapshot_id=snapshot_id,
                    action_id=action_id,
                    timestamp=datetime.utcnow(),
                    state_data=after_state,
                    metadata={}
                )
            
            # Add to undo stack if undoable
            if action.can_undo:
                self.undo_stacks[action.workspace_id].append(action_id)
                # Clear redo stack when new action is completed
                self.redo_stacks[action.workspace_id].clear()
            
            logger.info(f"Completed action {action_id}")
            
            return {
                "success": True,
                "action": action.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to complete action: {e}")
            return {"success": False, "error": str(e)}
    
    def fail_action(self, action_id: str, error: str) -> Dict[str, Any]:
        """Mark action as failed"""
        action = self.actions.get(action_id)
        if not action:
            return {"success": False, "error": "Action not found"}
        
        action.status = ActionStatus.FAILED
        action.error = error
        
        logger.warning(f"Action {action_id} failed: {error}")
        
        return {
            "success": True,
            "action": action.to_dict()
        }
    
    def undo_action(self, workspace_id: str) -> Dict[str, Any]:
        """Undo last action"""
        if workspace_id not in self.undo_stacks or not self.undo_stacks[workspace_id]:
            return {"success": False, "error": "No actions to undo"}
        
        action_id = self.undo_stacks[workspace_id].pop()
        action = self.actions.get(action_id)
        
        if not action:
            return {"success": False, "error": "Action not found"}
        
        if not action.can_undo:
            return {"success": False, "error": "Action cannot be undone"}
        
        try:
            # Execute undo handler
            handler_name = action.undo_handler or action.action_type.value
            handler = self.undo_handlers.get(handler_name)
            
            if handler:
                undo_result = handler(action)
                
                if undo_result.get("success"):
                    action.status = ActionStatus.UNDONE
                    action.can_redo = True
                    
                    # Add to redo stack
                    self.redo_stacks[workspace_id].append(action_id)
                    
                    logger.info(f"Undone action {action_id}")
                    
                    return {
                        "success": True,
                        "action": action.to_dict(),
                        "undo_result": undo_result
                    }
                else:
                    # Put back on undo stack if failed
                    self.undo_stacks[workspace_id].append(action_id)
                    return undo_result
            else:
                # Put back on undo stack
                self.undo_stacks[workspace_id].append(action_id)
                return {"success": False, "error": f"No undo handler for {handler_name}"}
        
        except Exception as e:
            logger.error(f"Failed to undo action: {e}")
            # Put back on undo stack
            self.undo_stacks[workspace_id].append(action_id)
            return {"success": False, "error": str(e)}
    
    def redo_action(self, workspace_id: str) -> Dict[str, Any]:
        """Redo last undone action"""
        if workspace_id not in self.redo_stacks or not self.redo_stacks[workspace_id]:
            return {"success": False, "error": "No actions to redo"}
        
        action_id = self.redo_stacks[workspace_id].pop()
        action = self.actions.get(action_id)
        
        if not action:
            return {"success": False, "error": "Action not found"}
        
        if not action.can_redo:
            return {"success": False, "error": "Action cannot be redone"}
        
        try:
            # Execute redo handler
            handler_name = action.redo_handler or action.action_type.value
            handler = self.redo_handlers.get(handler_name)
            
            if handler:
                redo_result = handler(action)
                
                if redo_result.get("success"):
                    action.status = ActionStatus.REDONE
                    action.can_redo = False
                    
                    # Add back to undo stack
                    self.undo_stacks[workspace_id].append(action_id)
                    
                    logger.info(f"Redone action {action_id}")
                    
                    return {
                        "success": True,
                        "action": action.to_dict(),
                        "redo_result": redo_result
                    }
                else:
                    # Put back on redo stack if failed
                    self.redo_stacks[workspace_id].append(action_id)
                    return redo_result
            else:
                # Put back on redo stack
                self.redo_stacks[workspace_id].append(action_id)
                return {"success": False, "error": f"No redo handler for {handler_name}"}
        
        except Exception as e:
            logger.error(f"Failed to redo action: {e}")
            # Put back on redo stack
            self.redo_stacks[workspace_id].append(action_id)
            return {"success": False, "error": str(e)}
    
    def undo_multiple(self, workspace_id: str, count: int) -> Dict[str, Any]:
        """Undo multiple actions"""
        results = []
        errors = []
        
        for i in range(count):
            result = self.undo_action(workspace_id)
            if result["success"]:
                results.append(result)
            else:
                errors.append(result)
                break  # Stop on first error
        
        return {
            "success": len(errors) == 0,
            "undone_count": len(results),
            "results": results,
            "errors": errors
        }
    
    def redo_multiple(self, workspace_id: str, count: int) -> Dict[str, Any]:
        """Redo multiple actions"""
        results = []
        errors = []
        
        for i in range(count):
            result = self.redo_action(workspace_id)
            if result["success"]:
                results.append(result)
            else:
                errors.append(result)
                break  # Stop on first error
        
        return {
            "success": len(errors) == 0,
            "redone_count": len(results),
            "results": results,
            "errors": errors
        }
    
    def create_checkpoint(
        self,
        workspace_id: str,
        name: str,
        description: str,
        state_snapshot: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create system checkpoint"""
        try:
            checkpoint_id = str(uuid.uuid4())
            
            action_count = len(self.workspace_actions.get(workspace_id, []))
            
            checkpoint = Checkpoint(
                checkpoint_id=checkpoint_id,
                workspace_id=workspace_id,
                name=name,
                description=description,
                created_at=datetime.utcnow(),
                state_snapshot=state_snapshot,
                action_count=action_count
            )
            
            self.checkpoints[checkpoint_id] = checkpoint
            
            if workspace_id not in self.workspace_checkpoints:
                self.workspace_checkpoints[workspace_id] = []
            self.workspace_checkpoints[workspace_id].append(checkpoint_id)
            
            logger.info(f"Created checkpoint {name}")
            
            return {
                "success": True,
                "checkpoint": checkpoint.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return {"success": False, "error": str(e)}
    
    def rollback_to_checkpoint(
        self,
        checkpoint_id: str
    ) -> Dict[str, Any]:
        """Rollback to checkpoint"""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            return {"success": False, "error": "Checkpoint not found"}
        
        try:
            workspace_id = checkpoint.workspace_id
            
            # Get actions after checkpoint
            all_actions = list(self.workspace_actions.get(workspace_id, []))
            actions_to_undo = all_actions[checkpoint.action_count:]
            
            # Undo actions in reverse order
            undone_count = 0
            for action_id in reversed(actions_to_undo):
                action = self.actions.get(action_id)
                if action and action.can_undo:
                    result = self.undo_action(workspace_id)
                    if result["success"]:
                        undone_count += 1
            
            logger.info(f"Rolled back to checkpoint {checkpoint.name}")
            
            return {
                "success": True,
                "checkpoint": checkpoint.to_dict(),
                "actions_undone": undone_count
            }
        
        except Exception as e:
            logger.error(f"Failed to rollback: {e}")
            return {"success": False, "error": str(e)}
    
    def get_action_history(
        self,
        workspace_id: str,
        limit: int = 50,
        action_type: Optional[ActionType] = None
    ) -> List[Dict[str, Any]]:
        """Get action history"""
        action_ids = list(self.workspace_actions.get(workspace_id, []))
        
        actions = []
        for action_id in reversed(action_ids):
            action = self.actions.get(action_id)
            if action:
                if action_type is None or action.action_type == action_type:
                    actions.append(action.to_dict())
                    if len(actions) >= limit:
                        break
        
        return actions
    
    def get_undo_stack(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get undo stack"""
        action_ids = self.undo_stacks.get(workspace_id, [])
        return [
            self.actions[aid].to_dict()
            for aid in reversed(action_ids)
            if aid in self.actions
        ]
    
    def get_redo_stack(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get redo stack"""
        action_ids = self.redo_stacks.get(workspace_id, [])
        return [
            self.actions[aid].to_dict()
            for aid in reversed(action_ids)
            if aid in self.actions
        ]
    
    # Default undo/redo handlers
    
    def _undo_file_create(self, action: Action) -> Dict[str, Any]:
        """Undo file creation"""
        file_path = action.parameters.get("file_path")
        if file_path:
            # Delete the created file
            from pathlib import Path
            try:
                Path(file_path).unlink(missing_ok=True)
                return {"success": True, "message": f"Deleted file {file_path}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "No file path in parameters"}
    
    def _redo_file_create(self, action: Action) -> Dict[str, Any]:
        """Redo file creation"""
        file_path = action.parameters.get("file_path")
        content = action.parameters.get("content", "")
        if file_path:
            # Recreate the file
            from pathlib import Path
            try:
                Path(file_path).write_text(content)
                return {"success": True, "message": f"Recreated file {file_path}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "No file path in parameters"}
    
    def _undo_file_edit(self, action: Action) -> Dict[str, Any]:
        """Undo file edit"""
        if action.before_snapshot:
            file_path = action.parameters.get("file_path")
            original_content = action.before_snapshot.state_data.get("content")
            if file_path and original_content is not None:
                from pathlib import Path
                try:
                    Path(file_path).write_text(original_content)
                    return {"success": True, "message": f"Restored file {file_path}"}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        return {"success": False, "error": "No before snapshot"}
    
    def _redo_file_edit(self, action: Action) -> Dict[str, Any]:
        """Redo file edit"""
        if action.after_snapshot:
            file_path = action.parameters.get("file_path")
            new_content = action.after_snapshot.state_data.get("content")
            if file_path and new_content is not None:
                from pathlib import Path
                try:
                    Path(file_path).write_text(new_content)
                    return {"success": True, "message": f"Reapplied edit to {file_path}"}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        return {"success": False, "error": "No after snapshot"}
    
    def _undo_file_delete(self, action: Action) -> Dict[str, Any]:
        """Undo file deletion"""
        if action.before_snapshot:
            file_path = action.parameters.get("file_path")
            original_content = action.before_snapshot.state_data.get("content")
            if file_path and original_content is not None:
                from pathlib import Path
                try:
                    Path(file_path).write_text(original_content)
                    return {"success": True, "message": f"Restored file {file_path}"}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        return {"success": False, "error": "No before snapshot"}
    
    def _redo_file_delete(self, action: Action) -> Dict[str, Any]:
        """Redo file deletion"""
        file_path = action.parameters.get("file_path")
        if file_path:
            from pathlib import Path
            try:
                Path(file_path).unlink(missing_ok=True)
                return {"success": True, "message": f"Deleted file {file_path}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "No file path in parameters"}


# Global service instance
action_history_service = ActionHistoryService()