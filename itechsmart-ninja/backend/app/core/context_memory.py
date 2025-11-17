"""
Task Memory & Context System for iTechSmart Ninja
Provides persistent session memory with infinite context support
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of context"""

    CONVERSATION = "conversation"
    TASK = "task"
    CODE = "code"
    RESEARCH = "research"
    FILE = "file"
    SYSTEM = "system"


class MemoryPriority(Enum):
    """Memory priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ContextEntry:
    """Single context entry"""

    entry_id: str
    context_type: ContextType
    content: Any
    timestamp: datetime
    priority: MemoryPriority = MemoryPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entry_id": self.entry_id,
            "context_type": self.context_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "metadata": self.metadata,
            "tags": self.tags,
        }


class ContextMemory:
    """
    Persistent context memory with infinite context support

    Features:
    - Persistent storage across sessions
    - Semantic search
    - Context compression
    - Priority-based retention
    - Tag-based organization
    - Time-based retrieval
    - Context summarization
    """

    def __init__(self, session_id: str, max_entries: int = 10000):
        self.session_id = session_id
        self.max_entries = max_entries
        self.entries: Dict[str, ContextEntry] = {}
        self.index: Dict[str, List[str]] = {}  # Tag -> Entry IDs
        self.conversation_history: List[str] = []
        self.task_history: List[str] = []
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()

    def add(
        self,
        content: Any,
        context_type: ContextType = ContextType.CONVERSATION,
        priority: MemoryPriority = MemoryPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Add entry to context memory

        Args:
            content: Content to store
            context_type: Type of context
            priority: Memory priority
            metadata: Additional metadata
            tags: Tags for organization

        Returns:
            Entry ID
        """
        # Generate entry ID
        entry_id = self._generate_id(content)

        # Create entry
        entry = ContextEntry(
            entry_id=entry_id,
            context_type=context_type,
            content=content,
            timestamp=datetime.utcnow(),
            priority=priority,
            metadata=metadata or {},
            tags=tags or [],
        )

        # Store entry
        self.entries[entry_id] = entry

        # Update indices
        for tag in entry.tags:
            if tag not in self.index:
                self.index[tag] = []
            self.index[tag].append(entry_id)

        # Update history
        if context_type == ContextType.CONVERSATION:
            self.conversation_history.append(entry_id)
        elif context_type == ContextType.TASK:
            self.task_history.append(entry_id)

        # Manage memory size
        if len(self.entries) > self.max_entries:
            self._compress_memory()

        self.last_accessed = datetime.utcnow()
        logger.debug(f"Added context entry: {entry_id}")

        return entry_id

    def get(self, entry_id: str) -> Optional[ContextEntry]:
        """Get entry by ID"""
        self.last_accessed = datetime.utcnow()
        return self.entries.get(entry_id)

    def get_by_tags(self, tags: List[str]) -> List[ContextEntry]:
        """Get entries by tags"""
        entry_ids = set()
        for tag in tags:
            if tag in self.index:
                entry_ids.update(self.index[tag])

        self.last_accessed = datetime.utcnow()
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]

    def get_by_type(self, context_type: ContextType) -> List[ContextEntry]:
        """Get entries by type"""
        self.last_accessed = datetime.utcnow()
        return [e for e in self.entries.values() if e.context_type == context_type]

    def get_recent(
        self, limit: int = 10, context_type: Optional[ContextType] = None
    ) -> List[ContextEntry]:
        """Get recent entries"""
        entries = list(self.entries.values())

        if context_type:
            entries = [e for e in entries if e.context_type == context_type]

        entries.sort(key=lambda e: e.timestamp, reverse=True)
        self.last_accessed = datetime.utcnow()

        return entries[:limit]

    def get_conversation_history(
        self, limit: Optional[int] = None
    ) -> List[ContextEntry]:
        """Get conversation history"""
        history_ids = (
            self.conversation_history[-limit:] if limit else self.conversation_history
        )
        self.last_accessed = datetime.utcnow()
        return [self.entries[eid] for eid in history_ids if eid in self.entries]

    def get_task_history(self, limit: Optional[int] = None) -> List[ContextEntry]:
        """Get task history"""
        history_ids = self.task_history[-limit:] if limit else self.task_history
        self.last_accessed = datetime.utcnow()
        return [self.entries[eid] for eid in history_ids if eid in self.entries]

    def search(
        self, query: str, context_type: Optional[ContextType] = None, limit: int = 10
    ) -> List[ContextEntry]:
        """
        Search context memory

        Args:
            query: Search query
            context_type: Filter by context type
            limit: Maximum results

        Returns:
            List of matching entries
        """
        query_lower = query.lower()
        results = []

        for entry in self.entries.values():
            if context_type and entry.context_type != context_type:
                continue

            # Simple text search (can be enhanced with embeddings)
            content_str = str(entry.content).lower()
            if query_lower in content_str:
                results.append(entry)

        # Sort by relevance (timestamp for now)
        results.sort(key=lambda e: e.timestamp, reverse=True)
        self.last_accessed = datetime.utcnow()

        return results[:limit]

    def get_context_window(
        self, max_tokens: int = 8000, context_type: Optional[ContextType] = None
    ) -> List[ContextEntry]:
        """
        Get context window within token limit

        Args:
            max_tokens: Maximum tokens
            context_type: Filter by context type

        Returns:
            List of entries within token limit
        """
        entries = self.get_recent(limit=100, context_type=context_type)

        # Estimate tokens (rough: 1 token ≈ 4 characters)
        window = []
        total_tokens = 0

        for entry in entries:
            content_str = str(entry.content)
            estimated_tokens = len(content_str) // 4

            if total_tokens + estimated_tokens <= max_tokens:
                window.append(entry)
                total_tokens += estimated_tokens
            else:
                break

        self.last_accessed = datetime.utcnow()
        return window

    def summarize_context(
        self,
        context_type: Optional[ContextType] = None,
        time_range: Optional[timedelta] = None,
    ) -> Dict[str, Any]:
        """
        Summarize context memory

        Args:
            context_type: Filter by context type
            time_range: Time range for summary

        Returns:
            Context summary
        """
        entries = list(self.entries.values())

        if context_type:
            entries = [e for e in entries if e.context_type == context_type]

        if time_range:
            cutoff = datetime.utcnow() - time_range
            entries = [e for e in entries if e.timestamp >= cutoff]

        # Calculate statistics
        total_entries = len(entries)
        by_type = {}
        by_priority = {}

        for entry in entries:
            # Count by type
            type_key = entry.context_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # Count by priority
            priority_key = entry.priority.value
            by_priority[priority_key] = by_priority.get(priority_key, 0) + 1

        return {
            "session_id": self.session_id,
            "total_entries": total_entries,
            "by_type": by_type,
            "by_priority": by_priority,
            "oldest_entry": (
                min(entries, key=lambda e: e.timestamp).timestamp.isoformat()
                if entries
                else None
            ),
            "newest_entry": (
                max(entries, key=lambda e: e.timestamp).timestamp.isoformat()
                if entries
                else None
            ),
            "total_tags": len(self.index),
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
        }

    def clear(self, context_type: Optional[ContextType] = None):
        """Clear context memory"""
        if context_type:
            # Clear specific type
            to_remove = [
                eid for eid, e in self.entries.items() if e.context_type == context_type
            ]
            for eid in to_remove:
                del self.entries[eid]

            # Update histories
            if context_type == ContextType.CONVERSATION:
                self.conversation_history.clear()
            elif context_type == ContextType.TASK:
                self.task_history.clear()
        else:
            # Clear all
            self.entries.clear()
            self.index.clear()
            self.conversation_history.clear()
            self.task_history.clear()

        logger.info(f"Cleared context memory for session {self.session_id}")

    def export(self) -> Dict[str, Any]:
        """Export context memory"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "entries": [e.to_dict() for e in self.entries.values()],
            "conversation_history": self.conversation_history,
            "task_history": self.task_history,
        }

    def import_data(self, data: Dict[str, Any]):
        """Import context memory"""
        self.session_id = data["session_id"]
        self.created_at = datetime.fromisoformat(data["created_at"])
        self.last_accessed = datetime.fromisoformat(data["last_accessed"])

        # Import entries
        for entry_data in data["entries"]:
            entry = ContextEntry(
                entry_id=entry_data["entry_id"],
                context_type=ContextType(entry_data["context_type"]),
                content=entry_data["content"],
                timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                priority=MemoryPriority(entry_data["priority"]),
                metadata=entry_data["metadata"],
                tags=entry_data["tags"],
            )
            self.entries[entry.entry_id] = entry

            # Rebuild index
            for tag in entry.tags:
                if tag not in self.index:
                    self.index[tag] = []
                self.index[tag].append(entry.entry_id)

        self.conversation_history = data["conversation_history"]
        self.task_history = data["task_history"]

        logger.info(f"Imported context memory for session {self.session_id}")

    def _generate_id(self, content: Any) -> str:
        """Generate unique ID for content"""
        content_str = json.dumps(content, sort_keys=True, default=str)
        timestamp = datetime.utcnow().isoformat()
        combined = f"{content_str}{timestamp}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _compress_memory(self):
        """Compress memory by removing low-priority old entries"""
        if len(self.entries) <= self.max_entries:
            return

        # Sort entries by priority and age
        entries_list = list(self.entries.values())
        entries_list.sort(key=lambda e: (e.priority.value, e.timestamp))

        # Remove oldest low-priority entries
        to_remove = entries_list[: len(entries_list) - self.max_entries]

        for entry in to_remove:
            del self.entries[entry.entry_id]

            # Update index
            for tag in entry.tags:
                if tag in self.index and entry.entry_id in self.index[tag]:
                    self.index[tag].remove(entry.entry_id)

        logger.info(f"Compressed memory: removed {len(to_remove)} entries")


class ContextMemoryManager:
    """Manages multiple context memory sessions"""

    def __init__(self):
        self.sessions: Dict[str, ContextMemory] = {}

    def get_session(self, session_id: str) -> ContextMemory:
        """Get or create session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ContextMemory(session_id)
        return self.sessions[session_id]

    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")

    def get_all_sessions(self) -> List[str]:
        """Get all session IDs"""
        return list(self.sessions.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        return {
            "total_sessions": len(self.sessions),
            "sessions": {
                sid: memory.summarize_context() for sid, memory in self.sessions.items()
            },
        }


# Global context memory manager
context_manager = ContextMemoryManager()
