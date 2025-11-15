"""
Collaboration Engine for iTechSmart Think-Tank
Handles real-time chat, file sharing, and team collaboration
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.models import Message, MessageType, User, Project


class CollaborationEngine:
    """
    Collaboration engine for team communication and file sharing
    """
    
    def __init__(self):
        self.engine_id = "collaboration-engine"
        self.version = "1.0.0"
        self.active_connections = {}  # WebSocket connections
    
    async def send_message(
        self,
        db: Session,
        project_id: int,
        sender_id: int,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        attachments: Optional[List[str]] = None,
        mentions: Optional[List[int]] = None,
        parent_message_id: Optional[int] = None
    ) -> Message:
        """Send a message in project chat"""
        
        message = Message(
            project_id=project_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            attachments=attachments or [],
            mentions=mentions or [],
            parent_message_id=parent_message_id
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Broadcast to WebSocket connections
        await self.broadcast_message(project_id, message)
        
        # Send notifications to mentioned users
        if mentions:
            await self.notify_mentioned_users(db, mentions, message)
        
        return message
    
    async def get_messages(
        self,
        db: Session,
        project_id: int,
        limit: int = 50,
        before_id: Optional[int] = None
    ) -> List[Message]:
        """Get messages for a project"""
        
        query = db.query(Message).filter(
            Message.project_id == project_id,
            Message.is_deleted == False
        )
        
        if before_id:
            query = query.filter(Message.id < before_id)
        
        messages = query.order_by(desc(Message.created_at)).limit(limit).all()
        return list(reversed(messages))
    
    async def edit_message(
        self,
        db: Session,
        message_id: int,
        new_content: str
    ) -> Message:
        """Edit a message"""
        
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        message.content = new_content
        message.is_edited = True
        message.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        
        return message
    
    async def delete_message(
        self,
        db: Session,
        message_id: int
    ) -> bool:
        """Delete a message (soft delete)"""
        
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        message.is_deleted = True
        message.updated_at = datetime.utcnow()
        
        db.commit()
        
        return True
    
    async def add_reaction(
        self,
        db: Session,
        message_id: int,
        user_id: int,
        emoji: str
    ) -> Message:
        """Add a reaction to a message"""
        
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        reactions = message.reactions or {}
        
        if emoji not in reactions:
            reactions[emoji] = []
        
        if user_id not in reactions[emoji]:
            reactions[emoji].append(user_id)
        
        message.reactions = reactions
        db.commit()
        db.refresh(message)
        
        return message
    
    async def remove_reaction(
        self,
        db: Session,
        message_id: int,
        user_id: int,
        emoji: str
    ) -> Message:
        """Remove a reaction from a message"""
        
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        reactions = message.reactions or {}
        
        if emoji in reactions and user_id in reactions[emoji]:
            reactions[emoji].remove(user_id)
            
            # Remove emoji key if no more reactions
            if not reactions[emoji]:
                del reactions[emoji]
        
        message.reactions = reactions
        db.commit()
        db.refresh(message)
        
        return message
    
    async def broadcast_message(
        self,
        project_id: int,
        message: Message
    ):
        """Broadcast message to all connected clients"""
        
        if project_id in self.active_connections:
            message_data = {
                "type": "new_message",
                "message": {
                    "id": message.id,
                    "sender_id": message.sender_id,
                    "content": message.content,
                    "message_type": message.message_type.value,
                    "created_at": message.created_at.isoformat()
                }
            }
            
            # Send to all connected WebSocket clients
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_json(message_data)
                except:
                    pass
    
    async def notify_mentioned_users(
        self,
        db: Session,
        user_ids: List[int],
        message: Message
    ):
        """Send notifications to mentioned users"""
        
        # Get sender info
        sender = db.query(User).filter(User.id == message.sender_id).first()
        
        # Get project info
        project = db.query(Project).filter(Project.id == message.project_id).first()
        
        # Create notifications (would integrate with notification system)
        for user_id in user_ids:
            notification = {
                "user_id": user_id,
                "type": "mention",
                "title": f"{sender.full_name} mentioned you",
                "message": f"In {project.name}: {message.content[:100]}",
                "link": f"/projects/{project.id}/chat",
                "timestamp": datetime.utcnow().isoformat()
            }
            # TODO: Send notification via iTechSmart Notify
    
    async def get_unread_count(
        self,
        db: Session,
        project_id: int,
        user_id: int,
        last_read_message_id: Optional[int] = None
    ) -> int:
        """Get count of unread messages"""
        
        query = db.query(Message).filter(
            Message.project_id == project_id,
            Message.sender_id != user_id,
            Message.is_deleted == False
        )
        
        if last_read_message_id:
            query = query.filter(Message.id > last_read_message_id)
        
        return query.count()
    
    async def search_messages(
        self,
        db: Session,
        project_id: int,
        search_query: str,
        limit: int = 20
    ) -> List[Message]:
        """Search messages in a project"""
        
        messages = db.query(Message).filter(
            Message.project_id == project_id,
            Message.content.ilike(f"%{search_query}%"),
            Message.is_deleted == False
        ).order_by(desc(Message.created_at)).limit(limit).all()
        
        return messages
    
    async def get_chat_statistics(
        self,
        db: Session,
        project_id: int
    ) -> Dict[str, Any]:
        """Get chat statistics for a project"""
        
        messages = db.query(Message).filter(
            Message.project_id == project_id,
            Message.is_deleted == False
        ).all()
        
        # Count by sender
        sender_counts = {}
        for message in messages:
            sender_id = message.sender_id
            sender_counts[sender_id] = sender_counts.get(sender_id, 0) + 1
        
        # Count by type
        type_counts = {}
        for message in messages:
            msg_type = message.message_type.value
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        # Get most active users
        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_messages": len(messages),
            "unique_senders": len(sender_counts),
            "message_types": type_counts,
            "top_senders": [
                {"user_id": user_id, "message_count": count}
                for user_id, count in top_senders
            ],
            "average_messages_per_day": len(messages) / 30 if messages else 0
        }