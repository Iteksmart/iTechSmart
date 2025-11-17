"""
Slack Integration API Endpoints
Provides REST API for Slack messaging and notifications
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Optional
from pydantic import BaseModel, Field

from ..services.slack_service import slack_service, NotificationPriority

router = APIRouter(prefix="/api/integrations/slack", tags=["slack"])


# Request Models
class ConnectSlackRequest(BaseModel):
    workspace_id: str
    slack_workspace_id: str
    slack_workspace_name: str
    bot_token: str
    webhook_url: str
    user_token: Optional[str] = None


class SendMessageRequest(BaseModel):
    channel: str
    text: str
    blocks: Optional[List[dict]] = None
    thread_ts: Optional[str] = None


class SendNotificationRequest(BaseModel):
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    channel: Optional[str] = None


class CreateNotificationRuleRequest(BaseModel):
    name: str
    event_type: str
    slack_channel_id: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    filters: Optional[dict] = None


class TriggerNotificationRequest(BaseModel):
    event_type: str
    event_data: dict


# Response Models
class ConnectionResponse(BaseModel):
    success: bool
    connection: Optional[dict] = None
    error: Optional[str] = None


class MessageResponse(BaseModel):
    success: bool
    message: Optional[dict] = None
    error: Optional[str] = None


class RuleResponse(BaseModel):
    success: bool
    rule: Optional[dict] = None
    error: Optional[str] = None


# Helper function to get current user
def get_current_user_id(user_id: str = Query(...)) -> str:
    """Get current authenticated user ID"""
    return user_id


# Connection Endpoints


@router.post("/connect", response_model=ConnectionResponse)
async def connect_slack(request: ConnectSlackRequest, user_id: str = Query(...)):
    """
    Connect Slack workspace

    Requires Slack OAuth tokens from authentication flow
    Enables messaging, notifications, and command integration
    """
    result = slack_service.connect_slack(
        workspace_id=request.workspace_id,
        slack_workspace_id=request.slack_workspace_id,
        slack_workspace_name=request.slack_workspace_name,
        bot_token=request.bot_token,
        webhook_url=request.webhook_url,
        user_id=user_id,
        user_token=request.user_token,
    )

    return ConnectionResponse(**result)


@router.delete("/disconnect")
async def disconnect_slack(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    Disconnect Slack workspace

    Removes connection and stops notifications
    """
    result = slack_service.disconnect_slack(workspace_id)
    return result


@router.get("/connection")
async def get_connection(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    Get Slack connection status

    Returns connection details and configuration
    """
    connection = slack_service.get_connection(workspace_id)

    if not connection:
        return {"success": False, "connected": False, "error": "Not connected to Slack"}

    return {"success": True, "connected": True, "connection": connection.to_dict()}


# Messaging Endpoints


@router.post("/send-message", response_model=MessageResponse)
async def send_message(
    workspace_id: str = Query(...),
    request: SendMessageRequest = None,
    user_id: str = Query(...),
):
    """
    Send message to Slack channel

    Supports text messages, blocks, and threaded replies
    """
    result = slack_service.send_message(
        workspace_id=workspace_id,
        channel=request.channel,
        text=request.text,
        blocks=request.blocks,
        thread_ts=request.thread_ts,
    )

    return MessageResponse(**result)


@router.post("/send-notification")
async def send_notification(
    workspace_id: str = Query(...),
    request: SendNotificationRequest = None,
    user_id: str = Query(...),
):
    """
    Send notification to Slack

    Sends formatted notification with priority level
    Priority levels: low, normal, high, urgent
    """
    result = slack_service.send_notification(
        workspace_id=workspace_id,
        title=request.title,
        message=request.message,
        priority=request.priority,
        channel=request.channel,
    )

    return result


@router.get("/channels")
async def list_channels(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    List Slack channels

    Returns all channels in connected Slack workspace
    """
    result = slack_service.list_channels(workspace_id)
    return result


@router.get("/messages/{channel_id}")
async def get_message_history(
    channel_id: str, limit: int = Query(50, ge=1, le=100), user_id: str = Query(...)
):
    """
    Get message history for channel

    Returns recent messages sent to channel
    """
    messages = slack_service.get_message_history(channel_id, limit)

    return {
        "success": True,
        "channel_id": channel_id,
        "messages": messages,
        "count": len(messages),
    }


# Command Endpoints


@router.post("/commands/handle")
async def handle_command(
    workspace_id: str = Query(...),
    command: str = Query(...),
    text: str = Query(""),
    user_id: str = Query(...),
    channel_id: str = Query(...),
):
    """
    Handle Slack slash command

    Processes slash command and returns response
    """
    result = slack_service.handle_command(
        workspace_id=workspace_id,
        command=command,
        text=text,
        user_id=user_id,
        channel_id=channel_id,
    )

    return result


@router.get("/commands")
async def list_commands():
    """
    List available slash commands

    Returns all registered slash commands
    """
    commands = slack_service.list_commands()

    return {"success": True, "commands": commands, "count": len(commands)}


# Notification Rules


@router.post("/notification-rules", response_model=RuleResponse)
async def create_notification_rule(
    workspace_id: str = Query(...),
    request: CreateNotificationRuleRequest = None,
    user_id: str = Query(...),
):
    """
    Create notification routing rule

    Automatically sends notifications to Slack when events occur
    """
    result = slack_service.create_notification_rule(
        workspace_id=workspace_id,
        name=request.name,
        event_type=request.event_type,
        slack_channel_id=request.slack_channel_id,
        priority=request.priority,
        filters=request.filters,
    )

    return RuleResponse(**result)


@router.get("/notification-rules")
async def list_notification_rules(
    workspace_id: str = Query(...), user_id: str = Query(...)
):
    """
    List notification rules

    Returns all notification routing rules for workspace
    """
    rules = slack_service.list_notification_rules(workspace_id)

    return {"success": True, "rules": rules, "count": len(rules)}


@router.post("/trigger-notification")
async def trigger_notification(
    workspace_id: str = Query(...),
    request: TriggerNotificationRequest = None,
    user_id: str = Query(...),
):
    """
    Trigger notification based on event

    Evaluates notification rules and sends matching notifications
    """
    result = slack_service.trigger_notification(
        workspace_id=workspace_id,
        event_type=request.event_type,
        event_data=request.event_data,
    )

    return result


# Webhook Endpoints


@router.post("/webhook/events")
async def slack_events_webhook(request: Request):
    """
    Slack events webhook endpoint

    Receives events from Slack (messages, reactions, etc.)
    """
    body = await request.json()

    # Handle URL verification challenge
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}

    # Handle events
    event = body.get("event", {})
    event_type = event.get("type")

    # Process event
    logger.info(f"Received Slack event: {event_type}")

    return {"ok": True}


@router.post("/webhook/commands")
async def slack_commands_webhook(
    command: str = Query(...),
    text: str = Query(""),
    user_id: str = Query(...),
    channel_id: str = Query(...),
    team_id: str = Query(...),
):
    """
    Slack slash commands webhook endpoint

    Receives slash command invocations from Slack
    """
    # Find workspace by team_id
    workspace_id = None
    for conn in slack_service.connections.values():
        if conn.slack_workspace_id == team_id:
            workspace_id = conn.workspace_id
            break

    if not workspace_id:
        return {"response_type": "ephemeral", "text": "❌ Workspace not connected"}

    # Handle command
    result = slack_service.handle_command(
        workspace_id=workspace_id,
        command=command,
        text=text,
        user_id=user_id,
        channel_id=channel_id,
    )

    if result["success"]:
        return {"response_type": "in_channel", "text": result["response"]}
    else:
        return {"response_type": "ephemeral", "text": f"❌ {result['error']}"}


@router.post("/webhook/interactive")
async def slack_interactive_webhook(request: Request):
    """
    Slack interactive components webhook endpoint

    Receives button clicks, menu selections, etc.
    """
    body = await request.json()

    # Handle interactive component
    payload = body.get("payload", {})
    action_type = payload.get("type")

    logger.info(f"Received Slack interaction: {action_type}")

    return {"ok": True}


# Statistics


@router.get("/stats")
async def get_slack_stats(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    Get Slack integration statistics

    Returns usage metrics and activity stats
    """
    connection = slack_service.get_connection(workspace_id)

    if not connection:
        raise HTTPException(status_code=404, detail="Not connected to Slack")

    # Count messages and rules
    total_messages = sum(
        len(messages) for messages in slack_service.message_history.values()
    )

    rules = slack_service.list_notification_rules(workspace_id)

    return {
        "success": True,
        "stats": {
            "connected": True,
            "slack_workspace": connection.slack_workspace_name,
            "connected_at": connection.connected_at.isoformat(),
            "total_messages_sent": total_messages,
            "notification_rules": len(rules),
            "available_commands": len(slack_service.list_commands()),
        },
    }
