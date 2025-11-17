"""
Chat and Collaboration Service
Provides real-time messaging, threads, and team collaboration features
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages"""

    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    CODE = "code"
    SYSTEM = "system"
    THREAD_REPLY = "thread_reply"


class ChannelType(str, Enum):
    """Types of channels"""

    PUBLIC = "public"
    PRIVATE = "private"
    DIRECT = "direct"
    THREAD = "thread"


class ReactionType(str, Enum):
    """Message reaction types"""

    LIKE = "like"
    LOVE = "love"
    LAUGH = "laugh"
    SURPRISED = "surprised"
    SAD = "sad"
    ANGRY = "angry"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    CELEBRATE = "celebrate"
    ROCKET = "rocket"


@dataclass
class Reaction:
    """Message reaction"""

    reaction_type: ReactionType
    user_id: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reaction_type": self.reaction_type.value,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Attachment:
    """Message attachment"""

    attachment_id: str
    file_name: str
    file_type: str
    file_size: int
    file_url: str
    thumbnail_url: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Message:
    """Chat message"""

    message_id: str
    channel_id: str
    user_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    edited_at: Optional[datetime]
    deleted_at: Optional[datetime]
    parent_message_id: Optional[str]
    thread_count: int
    reactions: List[Reaction]
    attachments: List[Attachment]
    mentions: List[str]
    is_pinned: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "channel_id": self.channel_id,
            "user_id": self.user_id,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "edited_at": self.edited_at.isoformat() if self.edited_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "parent_message_id": self.parent_message_id,
            "thread_count": self.thread_count,
            "reactions": [r.to_dict() for r in self.reactions],
            "attachments": [a.to_dict() for a in self.attachments],
            "mentions": self.mentions,
            "is_pinned": self.is_pinned,
        }


@dataclass
class Channel:
    """Chat channel"""

    channel_id: str
    workspace_id: str
    name: str
    description: Optional[str]
    channel_type: ChannelType
    created_by: str
    created_at: datetime
    updated_at: datetime
    members: Set[str]
    admins: Set[str]
    is_archived: bool
    settings: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "description": self.description,
            "channel_type": self.channel_type.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "members": list(self.members),
            "admins": list(self.admins),
            "member_count": len(self.members),
            "is_archived": self.is_archived,
            "settings": self.settings,
        }


@dataclass
class TypingIndicator:
    """Typing indicator"""

    user_id: str
    channel_id: str
    started_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "started_at": self.started_at.isoformat(),
        }


@dataclass
class ReadReceipt:
    """Message read receipt"""

    user_id: str
    message_id: str
    read_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "message_id": self.message_id,
            "read_at": self.read_at.isoformat(),
        }


class ChatService:
    """Manages chat and collaboration features"""

    def __init__(self):
        self.channels: Dict[str, Channel] = {}
        self.messages: Dict[str, Message] = {}
        self.channel_messages: Dict[str, List[str]] = defaultdict(
            list
        )  # channel_id -> message_ids
        self.user_channels: Dict[str, Set[str]] = defaultdict(
            set
        )  # user_id -> channel_ids
        self.typing_indicators: Dict[str, List[TypingIndicator]] = defaultdict(list)
        self.read_receipts: Dict[str, List[ReadReceipt]] = defaultdict(
            list
        )  # message_id -> receipts
        self.pinned_messages: Dict[str, List[str]] = defaultdict(
            list
        )  # channel_id -> message_ids

    def create_channel(
        self,
        workspace_id: str,
        name: str,
        created_by: str,
        channel_type: ChannelType = ChannelType.PUBLIC,
        description: Optional[str] = None,
        members: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create new channel"""
        try:
            channel_id = str(uuid.uuid4())
            now = datetime.utcnow()

            initial_members = set(members or [])
            initial_members.add(created_by)

            channel = Channel(
                channel_id=channel_id,
                workspace_id=workspace_id,
                name=name,
                description=description,
                channel_type=channel_type,
                created_by=created_by,
                created_at=now,
                updated_at=now,
                members=initial_members,
                admins={created_by},
                is_archived=False,
                settings={
                    "allow_threads": True,
                    "allow_reactions": True,
                    "allow_file_uploads": True,
                    "message_retention_days": 90,
                },
            )

            self.channels[channel_id] = channel

            # Add to user channels
            for member_id in initial_members:
                self.user_channels[member_id].add(channel_id)

            logger.info(f"Created channel {channel_id} in workspace {workspace_id}")

            return {"success": True, "channel": channel.to_dict()}

        except Exception as e:
            logger.error(f"Failed to create channel: {e}")
            return {"success": False, "error": str(e)}

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get channel by ID"""
        return self.channels.get(channel_id)

    def update_channel(
        self, channel_id: str, user_id: str, **updates
    ) -> Dict[str, Any]:
        """Update channel details"""
        channel = self.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": "Channel not found"}

        # Check if user is admin
        if user_id not in channel.admins:
            return {"success": False, "error": "Insufficient permissions"}

        try:
            allowed_fields = ["name", "description", "settings"]
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(channel, field, value)

            channel.updated_at = datetime.utcnow()

            return {"success": True, "channel": channel.to_dict()}

        except Exception as e:
            logger.error(f"Failed to update channel: {e}")
            return {"success": False, "error": str(e)}

    def delete_channel(self, channel_id: str, user_id: str) -> Dict[str, Any]:
        """Delete channel"""
        channel = self.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": "Channel not found"}

        # Only creator can delete
        if channel.created_by != user_id:
            return {"success": False, "error": "Only creator can delete channel"}

        try:
            # Remove from user channels
            for member_id in channel.members:
                self.user_channels[member_id].discard(channel_id)

            # Delete messages
            message_ids = self.channel_messages.get(channel_id, [])
            for message_id in message_ids:
                if message_id in self.messages:
                    del self.messages[message_id]

            del self.channels[channel_id]
            del self.channel_messages[channel_id]

            logger.info(f"Deleted channel {channel_id}")

            return {"success": True, "channel_id": channel_id}

        except Exception as e:
            logger.error(f"Failed to delete channel: {e}")
            return {"success": False, "error": str(e)}

    def add_member(
        self, channel_id: str, user_id: str, new_member_id: str
    ) -> Dict[str, Any]:
        """Add member to channel"""
        channel = self.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": "Channel not found"}

        # Check permissions
        if (
            channel.channel_type == ChannelType.PRIVATE
            and user_id not in channel.admins
        ):
            return {"success": False, "error": "Insufficient permissions"}

        if new_member_id in channel.members:
            return {"success": False, "error": "User is already a member"}

        try:
            channel.members.add(new_member_id)
            self.user_channels[new_member_id].add(channel_id)
            channel.updated_at = datetime.utcnow()

            # Send system message
            self.send_message(
                channel_id=channel_id,
                user_id="system",
                content=f"User {new_member_id} joined the channel",
                message_type=MessageType.SYSTEM,
            )

            logger.info(f"Added member {new_member_id} to channel {channel_id}")

            return {"success": True, "member_id": new_member_id}

        except Exception as e:
            logger.error(f"Failed to add member: {e}")
            return {"success": False, "error": str(e)}

    def remove_member(
        self, channel_id: str, user_id: str, member_id: str
    ) -> Dict[str, Any]:
        """Remove member from channel"""
        channel = self.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": "Channel not found"}

        # Check permissions
        if user_id not in channel.admins and user_id != member_id:
            return {"success": False, "error": "Insufficient permissions"}

        if member_id not in channel.members:
            return {"success": False, "error": "User is not a member"}

        try:
            channel.members.discard(member_id)
            channel.admins.discard(member_id)
            self.user_channels[member_id].discard(channel_id)
            channel.updated_at = datetime.utcnow()

            # Send system message
            self.send_message(
                channel_id=channel_id,
                user_id="system",
                content=f"User {member_id} left the channel",
                message_type=MessageType.SYSTEM,
            )

            logger.info(f"Removed member {member_id} from channel {channel_id}")

            return {"success": True, "member_id": member_id}

        except Exception as e:
            logger.error(f"Failed to remove member: {e}")
            return {"success": False, "error": str(e)}

    def send_message(
        self,
        channel_id: str,
        user_id: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        parent_message_id: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        mentions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Send message to channel"""
        channel = self.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": "Channel not found"}

        # Check if user is member (except system messages)
        if user_id != "system" and user_id not in channel.members:
            return {"success": False, "error": "User is not a member"}

        try:
            message_id = str(uuid.uuid4())
            now = datetime.utcnow()

            # Process attachments
            attachment_objects = []
            if attachments:
                for att in attachments:
                    attachment_objects.append(Attachment(**att))

            message = Message(
                message_id=message_id,
                channel_id=channel_id,
                user_id=user_id,
                content=content,
                message_type=message_type,
                timestamp=now,
                edited_at=None,
                deleted_at=None,
                parent_message_id=parent_message_id,
                thread_count=0,
                reactions=[],
                attachments=attachment_objects,
                mentions=mentions or [],
                is_pinned=False,
            )

            self.messages[message_id] = message
            self.channel_messages[channel_id].append(message_id)

            # Update thread count if reply
            if parent_message_id:
                parent = self.messages.get(parent_message_id)
                if parent:
                    parent.thread_count += 1

            logger.info(f"Sent message {message_id} to channel {channel_id}")

            return {"success": True, "message": message.to_dict()}

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return {"success": False, "error": str(e)}

    def edit_message(
        self, message_id: str, user_id: str, new_content: str
    ) -> Dict[str, Any]:
        """Edit message"""
        message = self.messages.get(message_id)
        if not message:
            return {"success": False, "error": "Message not found"}

        if message.user_id != user_id:
            return {"success": False, "error": "Cannot edit other user's message"}

        if message.deleted_at:
            return {"success": False, "error": "Cannot edit deleted message"}

        try:
            message.content = new_content
            message.edited_at = datetime.utcnow()

            logger.info(f"Edited message {message_id}")

            return {"success": True, "message": message.to_dict()}

        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
            return {"success": False, "error": str(e)}

    def delete_message(self, message_id: str, user_id: str) -> Dict[str, Any]:
        """Delete message"""
        message = self.messages.get(message_id)
        if not message:
            return {"success": False, "error": "Message not found"}

        channel = self.get_channel(message.channel_id)
        if not channel:
            return {"success": False, "error": "Channel not found"}

        # Check permissions
        if message.user_id != user_id and user_id not in channel.admins:
            return {"success": False, "error": "Insufficient permissions"}

        try:
            message.deleted_at = datetime.utcnow()
            message.content = "[deleted]"

            logger.info(f"Deleted message {message_id}")

            return {"success": True, "message_id": message_id}

        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return {"success": False, "error": str(e)}

    def add_reaction(
        self, message_id: str, user_id: str, reaction_type: ReactionType
    ) -> Dict[str, Any]:
        """Add reaction to message"""
        message = self.messages.get(message_id)
        if not message:
            return {"success": False, "error": "Message not found"}

        try:
            # Check if user already reacted with this type
            for reaction in message.reactions:
                if (
                    reaction.user_id == user_id
                    and reaction.reaction_type == reaction_type
                ):
                    return {"success": False, "error": "Already reacted"}

            reaction = Reaction(
                reaction_type=reaction_type,
                user_id=user_id,
                timestamp=datetime.utcnow(),
            )

            message.reactions.append(reaction)

            logger.info(f"Added reaction to message {message_id}")

            return {"success": True, "reaction": reaction.to_dict()}

        except Exception as e:
            logger.error(f"Failed to add reaction: {e}")
            return {"success": False, "error": str(e)}

    def remove_reaction(
        self, message_id: str, user_id: str, reaction_type: ReactionType
    ) -> Dict[str, Any]:
        """Remove reaction from message"""
        message = self.messages.get(message_id)
        if not message:
            return {"success": False, "error": "Message not found"}

        try:
            message.reactions = [
                r
                for r in message.reactions
                if not (r.user_id == user_id and r.reaction_type == reaction_type)
            ]

            logger.info(f"Removed reaction from message {message_id}")

            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to remove reaction: {e}")
            return {"success": False, "error": str(e)}

    def pin_message(self, message_id: str, user_id: str) -> Dict[str, Any]:
        """Pin message to channel"""
        message = self.messages.get(message_id)
        if not message:
            return {"success": False, "error": "Message not found"}

        channel = self.get_channel(message.channel_id)
        if not channel:
            return {"success": False, "error": "Channel not found"}

        if user_id not in channel.admins:
            return {"success": False, "error": "Insufficient permissions"}

        try:
            message.is_pinned = True
            self.pinned_messages[message.channel_id].append(message_id)

            logger.info(f"Pinned message {message_id}")

            return {"success": True, "message_id": message_id}

        except Exception as e:
            logger.error(f"Failed to pin message: {e}")
            return {"success": False, "error": str(e)}

    def get_messages(
        self, channel_id: str, limit: int = 50, before: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get messages from channel"""
        message_ids = self.channel_messages.get(channel_id, [])

        messages = []
        for message_id in reversed(message_ids):
            message = self.messages.get(message_id)
            if message and not message.deleted_at:
                if before and message.message_id == before:
                    break
                messages.append(message.to_dict())
                if len(messages) >= limit:
                    break

        return messages

    def get_thread_messages(
        self, parent_message_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get thread replies"""
        replies = []

        for message in self.messages.values():
            if (
                message.parent_message_id == parent_message_id
                and not message.deleted_at
            ):
                replies.append(message.to_dict())

        # Sort by timestamp
        replies.sort(key=lambda x: x["timestamp"])

        return replies[:limit]

    def mark_as_read(self, message_id: str, user_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        message = self.messages.get(message_id)
        if not message:
            return {"success": False, "error": "Message not found"}

        try:
            receipt = ReadReceipt(
                user_id=user_id, message_id=message_id, read_at=datetime.utcnow()
            )

            self.read_receipts[message_id].append(receipt)

            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to mark as read: {e}")
            return {"success": False, "error": str(e)}

    def set_typing_indicator(self, channel_id: str, user_id: str) -> Dict[str, Any]:
        """Set typing indicator"""
        try:
            indicator = TypingIndicator(
                user_id=user_id, channel_id=channel_id, started_at=datetime.utcnow()
            )

            # Remove old indicators for this user in this channel
            self.typing_indicators[channel_id] = [
                i for i in self.typing_indicators[channel_id] if i.user_id != user_id
            ]

            self.typing_indicators[channel_id].append(indicator)

            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to set typing indicator: {e}")
            return {"success": False, "error": str(e)}

    def get_typing_users(self, channel_id: str) -> List[str]:
        """Get users currently typing"""
        now = datetime.utcnow()
        typing_users = []

        # Remove stale indicators (older than 5 seconds)
        self.typing_indicators[channel_id] = [
            i
            for i in self.typing_indicators[channel_id]
            if (now - i.started_at).total_seconds() < 5
        ]

        for indicator in self.typing_indicators[channel_id]:
            typing_users.append(indicator.user_id)

        return typing_users

    def search_messages(
        self, channel_id: str, query: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search messages in channel"""
        message_ids = self.channel_messages.get(channel_id, [])
        results = []

        query_lower = query.lower()

        for message_id in reversed(message_ids):
            message = self.messages.get(message_id)
            if message and not message.deleted_at:
                if query_lower in message.content.lower():
                    results.append(message.to_dict())
                    if len(results) >= limit:
                        break

        return results


# Global service instance
chat_service = ChatService()
