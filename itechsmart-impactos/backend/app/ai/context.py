"""
Context Management for AI Conversations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json


class ConversationContext:
    """Manage conversation context for AI interactions"""
    
    def __init__(self, max_messages: int = 20, max_age_minutes: int = 60):
        """
        Initialize conversation context
        
        Args:
            max_messages: Maximum number of messages to keep
            max_age_minutes: Maximum age of messages in minutes
        """
        self.max_messages = max_messages
        self.max_age_minutes = max_age_minutes
        self.messages: deque = deque(maxlen=max_messages)
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a message to the context
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.last_updated = datetime.utcnow()
    
    def get_messages(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get messages for AI model
        
        Args:
            include_system: Whether to include system messages
            
        Returns:
            List of messages
        """
        messages = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.max_age_minutes)
        
        for msg in self.messages:
            # Check message age
            msg_time = datetime.fromisoformat(msg["timestamp"])
            if msg_time < cutoff_time:
                continue
            
            # Filter system messages if needed
            if not include_system and msg["role"] == "system":
                continue
            
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages
    
    def clear(self):
        """Clear all messages"""
        self.messages.clear()
        self.last_updated = datetime.utcnow()
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata"""
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "messages": list(self.messages),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "message_count": len(self.messages)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        """Create from dictionary"""
        context = cls()
        context.messages = deque(data.get("messages", []), maxlen=context.max_messages)
        context.metadata = data.get("metadata", {})
        context.created_at = datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat()))
        context.last_updated = datetime.fromisoformat(data.get("last_updated", datetime.utcnow().isoformat()))
        return context


class ContextManager:
    """Manage multiple conversation contexts"""
    
    def __init__(self):
        """Initialize context manager"""
        self.contexts: Dict[str, ConversationContext] = {}
    
    def create_context(self, context_id: str, **kwargs) -> ConversationContext:
        """
        Create a new context
        
        Args:
            context_id: Unique context identifier
            **kwargs: Additional arguments for ConversationContext
            
        Returns:
            Created context
        """
        context = ConversationContext(**kwargs)
        self.contexts[context_id] = context
        return context
    
    def get_context(self, context_id: str) -> Optional[ConversationContext]:
        """
        Get a context by ID
        
        Args:
            context_id: Context identifier
            
        Returns:
            Context or None if not found
        """
        return self.contexts.get(context_id)
    
    def get_or_create_context(self, context_id: str, **kwargs) -> ConversationContext:
        """
        Get existing context or create new one
        
        Args:
            context_id: Context identifier
            **kwargs: Additional arguments for ConversationContext
            
        Returns:
            Context
        """
        if context_id not in self.contexts:
            return self.create_context(context_id, **kwargs)
        return self.contexts[context_id]
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a context
        
        Args:
            context_id: Context identifier
            
        Returns:
            True if deleted, False if not found
        """
        if context_id in self.contexts:
            del self.contexts[context_id]
            return True
        return False
    
    def clear_all(self):
        """Clear all contexts"""
        self.contexts.clear()
    
    def cleanup_old_contexts(self, max_age_hours: int = 24):
        """
        Clean up old contexts
        
        Args:
            max_age_hours: Maximum age in hours
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        contexts_to_delete = []
        
        for context_id, context in self.contexts.items():
            if context.last_updated < cutoff_time:
                contexts_to_delete.append(context_id)
        
        for context_id in contexts_to_delete:
            del self.contexts[context_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        return {
            "total_contexts": len(self.contexts),
            "contexts": {
                context_id: {
                    "message_count": len(context.messages),
                    "created_at": context.created_at.isoformat(),
                    "last_updated": context.last_updated.isoformat()
                }
                for context_id, context in self.contexts.items()
            }
        }


# Global context manager instance
context_manager = ContextManager()