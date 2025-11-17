"""
Chat and Collaboration API Endpoints
Provides REST API for real-time messaging and team collaboration
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import List, Optional
from pydantic import BaseModel, Field
import json

from ..services.chat_service import chat_service, MessageType, ChannelType, ReactionType

router = APIRouter(prefix="/api/chat", tags=["chat"])


# Request Models
class CreateChannelRequest(BaseModel):
    workspace_id: str
    name: str = Field(..., min_length=1, max_length=100)
    channel_type: ChannelType = ChannelType.PUBLIC
    description: Optional[str] = Field(None, max_length=500)
    members: Optional[List[str]] = None


class UpdateChannelRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    settings: Optional[dict] = None


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: MessageType = MessageType.TEXT
    parent_message_id: Optional[str] = None
    attachments: Optional[List[dict]] = None
    mentions: Optional[List[str]] = None


class EditMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class AddReactionRequest(BaseModel):
    reaction_type: ReactionType


# Response Models
class ChannelResponse(BaseModel):
    success: bool
    channel: Optional[dict] = None
    error: Optional[str] = None


class MessageResponse(BaseModel):
    success: bool
    message: Optional[dict] = None
    error: Optional[str] = None


# Helper function to get current user
def get_current_user_id(user_id: str = Query(...)) -> str:
    """Get current authenticated user ID"""
    return user_id


# Channel Endpoints


@router.post("/channels/create", response_model=ChannelResponse)
async def create_channel(request: CreateChannelRequest, user_id: str = Query(...)):
    """
    Create a new chat channel

    Channel types:
    - public: Anyone in workspace can join
    - private: Invite-only
    - direct: One-on-one conversation
    """
    result = chat_service.create_channel(
        workspace_id=request.workspace_id,
        name=request.name,
        created_by=user_id,
        channel_type=request.channel_type,
        description=request.description,
        members=request.members,
    )

    return ChannelResponse(**result)


@router.get("/channels/{channel_id}", response_model=ChannelResponse)
async def get_channel(channel_id: str, user_id: str = Query(...)):
    """
    Get channel details

    Returns channel information including members and settings
    """
    channel = chat_service.get_channel(channel_id)

    if not channel:
        return ChannelResponse(success=False, error="Channel not found")

    # Check if user is member
    if user_id not in channel.members:
        return ChannelResponse(success=False, error="Access denied")

    return ChannelResponse(success=True, channel=channel.to_dict())


@router.put("/channels/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: str, request: UpdateChannelRequest, user_id: str = Query(...)
):
    """
    Update channel details

    Requires admin permissions
    """
    updates = request.dict(exclude_unset=True)

    result = chat_service.update_channel(
        channel_id=channel_id, user_id=user_id, **updates
    )

    return ChannelResponse(**result)


@router.delete("/channels/{channel_id}", response_model=ChannelResponse)
async def delete_channel(channel_id: str, user_id: str = Query(...)):
    """
    Delete channel

    Only channel creator can delete
    """
    result = chat_service.delete_channel(channel_id=channel_id, user_id=user_id)

    return ChannelResponse(**result)


@router.post("/channels/{channel_id}/members/add")
async def add_member(channel_id: str, member_id: str, user_id: str = Query(...)):
    """
    Add member to channel

    For private channels, requires admin permissions
    """
    result = chat_service.add_member(
        channel_id=channel_id, user_id=user_id, new_member_id=member_id
    )

    return result


@router.delete("/channels/{channel_id}/members/{member_id}")
async def remove_member(channel_id: str, member_id: str, user_id: str = Query(...)):
    """
    Remove member from channel

    Admins can remove any member, users can remove themselves
    """
    result = chat_service.remove_member(
        channel_id=channel_id, user_id=user_id, member_id=member_id
    )

    return result


@router.get("/channels/{channel_id}/members")
async def list_members(channel_id: str, user_id: str = Query(...)):
    """
    List all channel members
    """
    channel = chat_service.get_channel(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if user_id not in channel.members:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "success": True,
        "members": list(channel.members),
        "admins": list(channel.admins),
        "total": len(channel.members),
    }


# Message Endpoints


@router.post("/channels/{channel_id}/messages", response_model=MessageResponse)
async def send_message(
    channel_id: str, request: SendMessageRequest, user_id: str = Query(...)
):
    """
    Send message to channel

    Supports text, files, images, code blocks, and thread replies
    """
    result = chat_service.send_message(
        channel_id=channel_id,
        user_id=user_id,
        content=request.content,
        message_type=request.message_type,
        parent_message_id=request.parent_message_id,
        attachments=request.attachments,
        mentions=request.mentions,
    )

    return MessageResponse(**result)


@router.get("/channels/{channel_id}/messages")
async def get_messages(
    channel_id: str,
    limit: int = Query(50, ge=1, le=100),
    before: Optional[str] = None,
    user_id: str = Query(...),
):
    """
    Get messages from channel

    Returns messages in reverse chronological order
    Supports pagination with 'before' parameter
    """
    channel = chat_service.get_channel(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if user_id not in channel.members:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = chat_service.get_messages(
        channel_id=channel_id, limit=limit, before=before
    )

    return {"success": True, "messages": messages, "count": len(messages)}


@router.put("/messages/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: str, request: EditMessageRequest, user_id: str = Query(...)
):
    """
    Edit message

    Only message author can edit
    """
    result = chat_service.edit_message(
        message_id=message_id, user_id=user_id, new_content=request.content
    )

    return MessageResponse(**result)


@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, user_id: str = Query(...)):
    """
    Delete message

    Message author or channel admin can delete
    """
    result = chat_service.delete_message(message_id=message_id, user_id=user_id)

    return result


@router.get("/messages/{message_id}/thread")
async def get_thread(
    message_id: str, limit: int = Query(50, ge=1, le=100), user_id: str = Query(...)
):
    """
    Get thread replies

    Returns all replies to a message
    """
    replies = chat_service.get_thread_messages(
        parent_message_id=message_id, limit=limit
    )

    return {
        "success": True,
        "parent_message_id": message_id,
        "replies": replies,
        "count": len(replies),
    }


# Reaction Endpoints


@router.post("/messages/{message_id}/reactions")
async def add_reaction(
    message_id: str, request: AddReactionRequest, user_id: str = Query(...)
):
    """
    Add reaction to message

    Available reactions: like, love, laugh, surprised, sad, angry,
    thumbs_up, thumbs_down, celebrate, rocket
    """
    result = chat_service.add_reaction(
        message_id=message_id, user_id=user_id, reaction_type=request.reaction_type
    )

    return result


@router.delete("/messages/{message_id}/reactions/{reaction_type}")
async def remove_reaction(
    message_id: str, reaction_type: ReactionType, user_id: str = Query(...)
):
    """
    Remove reaction from message
    """
    result = chat_service.remove_reaction(
        message_id=message_id, user_id=user_id, reaction_type=reaction_type
    )

    return result


# Pin/Unpin Endpoints


@router.post("/messages/{message_id}/pin")
async def pin_message(message_id: str, user_id: str = Query(...)):
    """
    Pin message to channel

    Requires admin permissions
    """
    result = chat_service.pin_message(message_id=message_id, user_id=user_id)

    return result


@router.get("/channels/{channel_id}/pinned")
async def get_pinned_messages(channel_id: str, user_id: str = Query(...)):
    """
    Get pinned messages in channel
    """
    channel = chat_service.get_channel(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if user_id not in channel.members:
        raise HTTPException(status_code=403, detail="Access denied")

    pinned_ids = chat_service.pinned_messages.get(channel_id, [])
    pinned_messages = []

    for message_id in pinned_ids:
        message = chat_service.messages.get(message_id)
        if message and not message.deleted_at:
            pinned_messages.append(message.to_dict())

    return {"success": True, "messages": pinned_messages, "count": len(pinned_messages)}


# Read Receipt Endpoints


@router.post("/messages/{message_id}/read")
async def mark_as_read(message_id: str, user_id: str = Query(...)):
    """
    Mark message as read

    Creates read receipt for message
    """
    result = chat_service.mark_as_read(message_id=message_id, user_id=user_id)

    return result


@router.get("/messages/{message_id}/receipts")
async def get_read_receipts(message_id: str, user_id: str = Query(...)):
    """
    Get read receipts for message

    Shows who has read the message
    """
    receipts = chat_service.read_receipts.get(message_id, [])

    return {
        "success": True,
        "receipts": [r.to_dict() for r in receipts],
        "count": len(receipts),
    }


# Typing Indicator Endpoints


@router.post("/channels/{channel_id}/typing")
async def set_typing(channel_id: str, user_id: str = Query(...)):
    """
    Set typing indicator

    Shows that user is currently typing
    Indicator expires after 5 seconds
    """
    result = chat_service.set_typing_indicator(channel_id=channel_id, user_id=user_id)

    return result


@router.get("/channels/{channel_id}/typing")
async def get_typing_users(channel_id: str, user_id: str = Query(...)):
    """
    Get users currently typing

    Returns list of user IDs who are typing
    """
    typing_users = chat_service.get_typing_users(channel_id)

    return {"success": True, "typing_users": typing_users, "count": len(typing_users)}


# Search Endpoint


@router.get("/channels/{channel_id}/search")
async def search_messages(
    channel_id: str,
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    user_id: str = Query(...),
):
    """
    Search messages in channel

    Performs full-text search on message content
    """
    channel = chat_service.get_channel(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if user_id not in channel.members:
        raise HTTPException(status_code=403, detail="Access denied")

    results = chat_service.search_messages(
        channel_id=channel_id, query=query, limit=limit
    )

    return {"success": True, "query": query, "results": results, "count": len(results)}


# WebSocket for real-time updates
@router.websocket("/ws/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket, channel_id: str, user_id: str = Query(...)
):
    """
    WebSocket connection for real-time chat

    Receives real-time message updates, typing indicators, and reactions
    """
    await websocket.accept()

    try:
        # Verify user is member
        channel = chat_service.get_channel(channel_id)
        if not channel or user_id not in channel.members:
            await websocket.close(code=1008, reason="Access denied")
            return

        # Send initial connection confirmation
        await websocket.send_json(
            {"type": "connected", "channel_id": channel_id, "user_id": user_id}
        )

        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types
            if message_data.get("type") == "message":
                result = chat_service.send_message(
                    channel_id=channel_id,
                    user_id=user_id,
                    content=message_data.get("content", ""),
                    message_type=MessageType(message_data.get("message_type", "text")),
                )

                if result["success"]:
                    # Broadcast to all connected clients (simplified)
                    await websocket.send_json(
                        {"type": "new_message", "message": result["message"]}
                    )

            elif message_data.get("type") == "typing":
                chat_service.set_typing_indicator(channel_id, user_id)
                await websocket.send_json(
                    {
                        "type": "typing_update",
                        "typing_users": chat_service.get_typing_users(channel_id),
                    }
                )

    except WebSocketDisconnect:
        # Handle disconnect
        pass
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
