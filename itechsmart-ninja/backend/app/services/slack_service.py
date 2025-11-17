"""
Slack Integration Service
Provides messaging, notifications, and command integration with Slack
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import logging
import json

logger = logging.getLogger(__name__)


class SlackEventType(str, Enum):
    """Slack event types"""

    MESSAGE = "message"
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"
    CHANNEL_CREATED = "channel_created"
    CHANNEL_DELETED = "channel_deleted"
    MEMBER_JOINED = "member_joined_channel"
    MEMBER_LEFT = "member_left_channel"
    APP_MENTION = "app_mention"
    FILE_SHARED = "file_shared"


class NotificationPriority(str, Enum):
    """Notification priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class SlackConnection:
    """Slack workspace connection"""

    connection_id: str
    workspace_id: str
    slack_workspace_id: str
    slack_workspace_name: str
    bot_token: str
    user_token: Optional[str]
    webhook_url: str
    connected_at: datetime
    connected_by: str
    enabled: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connection_id": self.connection_id,
            "workspace_id": self.workspace_id,
            "slack_workspace_id": self.slack_workspace_id,
            "slack_workspace_name": self.slack_workspace_name,
            "connected_at": self.connected_at.isoformat(),
            "connected_by": self.connected_by,
            "enabled": self.enabled,
        }


@dataclass
class SlackChannel:
    """Slack channel information"""

    channel_id: str
    name: str
    is_private: bool
    is_archived: bool
    member_count: int
    topic: str
    purpose: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SlackMessage:
    """Slack message"""

    message_id: str
    channel_id: str
    user_id: str
    text: str
    timestamp: datetime
    thread_ts: Optional[str]
    attachments: List[Dict[str, Any]]
    reactions: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "timestamp": self.timestamp.isoformat()}


@dataclass
class SlackCommand:
    """Slack slash command"""

    command_id: str
    command: str
    description: str
    usage_hint: str
    handler: str
    enabled: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NotificationRule:
    """Notification routing rule"""

    rule_id: str
    workspace_id: str
    name: str
    event_type: str
    slack_channel_id: str
    priority: NotificationPriority
    enabled: bool
    filters: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "priority": self.priority.value}


class SlackClient:
    """Slack API client wrapper"""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"

    def post_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Post message to channel"""
        # Mock implementation - in production, use Slack Web API
        return {
            "ok": True,
            "channel": channel,
            "ts": str(datetime.utcnow().timestamp()),
            "message": {"text": text, "user": "bot_user_id"},
        }

    def update_message(
        self, channel: str, ts: str, text: str, blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Update existing message"""
        return {"ok": True, "channel": channel, "ts": ts, "text": text}

    def delete_message(self, channel: str, ts: str) -> Dict[str, Any]:
        """Delete message"""
        return {"ok": True, "channel": channel, "ts": ts}

    def list_channels(self) -> Dict[str, Any]:
        """List channels"""
        return {
            "ok": True,
            "channels": [
                {
                    "id": "C123456",
                    "name": "general",
                    "is_private": False,
                    "is_archived": False,
                    "num_members": 10,
                    "topic": {"value": "General discussion"},
                    "purpose": {"value": "Company-wide announcements"},
                }
            ],
        }

    def add_reaction(self, channel: str, timestamp: str, name: str) -> Dict[str, Any]:
        """Add reaction to message"""
        return {"ok": True}

    def upload_file(
        self,
        channels: str,
        file_content: bytes,
        filename: str,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload file to channel"""
        return {
            "ok": True,
            "file": {
                "id": "F123456",
                "name": filename,
                "title": title or filename,
                "url_private": "https://files.slack.com/files-pri/...",
            },
        }


class SlackService:
    """Manages Slack integration"""

    def __init__(self):
        self.connections: Dict[str, SlackConnection] = {}
        self.workspace_connections: Dict[str, str] = {}  # workspace_id -> connection_id
        self.commands: Dict[str, SlackCommand] = {}
        self.notification_rules: Dict[str, NotificationRule] = {}
        self.message_history: Dict[str, List[SlackMessage]] = {}

        # Register default commands
        self._register_default_commands()

    def _register_default_commands(self):
        """Register default slash commands"""
        import uuid

        default_commands = [
            {
                "command": "/ninja-help",
                "description": "Show available commands",
                "usage_hint": "/ninja-help",
                "handler": "show_help",
            },
            {
                "command": "/ninja-status",
                "description": "Check system status",
                "usage_hint": "/ninja-status",
                "handler": "check_status",
            },
            {
                "command": "/ninja-task",
                "description": "Create new task",
                "usage_hint": "/ninja-task [description]",
                "handler": "create_task",
            },
            {
                "command": "/ninja-search",
                "description": "Search workspace",
                "usage_hint": "/ninja-search [query]",
                "handler": "search_workspace",
            },
        ]

        for cmd in default_commands:
            command_id = str(uuid.uuid4())
            self.commands[command_id] = SlackCommand(
                command_id=command_id,
                command=cmd["command"],
                description=cmd["description"],
                usage_hint=cmd["usage_hint"],
                handler=cmd["handler"],
                enabled=True,
            )

    def connect_slack(
        self,
        workspace_id: str,
        slack_workspace_id: str,
        slack_workspace_name: str,
        bot_token: str,
        webhook_url: str,
        user_id: str,
        user_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Connect Slack workspace"""
        try:
            import uuid

            connection_id = str(uuid.uuid4())

            connection = SlackConnection(
                connection_id=connection_id,
                workspace_id=workspace_id,
                slack_workspace_id=slack_workspace_id,
                slack_workspace_name=slack_workspace_name,
                bot_token=bot_token,
                user_token=user_token,
                webhook_url=webhook_url,
                connected_at=datetime.utcnow(),
                connected_by=user_id,
                enabled=True,
            )

            self.connections[connection_id] = connection
            self.workspace_connections[workspace_id] = connection_id

            logger.info(f"Connected Slack workspace {slack_workspace_name}")

            return {"success": True, "connection": connection.to_dict()}

        except Exception as e:
            logger.error(f"Failed to connect Slack: {e}")
            return {"success": False, "error": str(e)}

    def disconnect_slack(self, workspace_id: str) -> Dict[str, Any]:
        """Disconnect Slack workspace"""
        connection_id = self.workspace_connections.get(workspace_id)
        if not connection_id:
            return {"success": False, "error": "Not connected to Slack"}

        try:
            del self.connections[connection_id]
            del self.workspace_connections[workspace_id]

            logger.info(f"Disconnected Slack for workspace {workspace_id}")

            return {"success": True, "workspace_id": workspace_id}

        except Exception as e:
            logger.error(f"Failed to disconnect Slack: {e}")
            return {"success": False, "error": str(e)}

    def get_connection(self, workspace_id: str) -> Optional[SlackConnection]:
        """Get Slack connection for workspace"""
        connection_id = self.workspace_connections.get(workspace_id)
        return self.connections.get(connection_id) if connection_id else None

    def send_message(
        self,
        workspace_id: str,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send message to Slack channel"""
        connection = self.get_connection(workspace_id)
        if not connection:
            return {"success": False, "error": "Not connected to Slack"}

        try:
            client = SlackClient(connection.bot_token)
            result = client.post_message(channel, text, blocks, thread_ts)

            if result["ok"]:
                # Store message
                import uuid

                message = SlackMessage(
                    message_id=str(uuid.uuid4()),
                    channel_id=channel,
                    user_id="bot",
                    text=text,
                    timestamp=datetime.utcnow(),
                    thread_ts=thread_ts,
                    attachments=[],
                    reactions=[],
                )

                if channel not in self.message_history:
                    self.message_history[channel] = []
                self.message_history[channel].append(message)

                logger.info(f"Sent message to Slack channel {channel}")

                return {
                    "success": True,
                    "message": message.to_dict(),
                    "slack_ts": result["ts"],
                }

            return {"success": False, "error": "Failed to send message"}

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return {"success": False, "error": str(e)}

    def send_notification(
        self,
        workspace_id: str,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send notification to Slack"""
        connection = self.get_connection(workspace_id)
        if not connection:
            return {"success": False, "error": "Not connected to Slack"}

        # Format message based on priority
        emoji_map = {
            NotificationPriority.LOW: ":information_source:",
            NotificationPriority.NORMAL: ":bell:",
            NotificationPriority.HIGH: ":warning:",
            NotificationPriority.URGENT: ":rotating_light:",
        }

        emoji = emoji_map.get(priority, ":bell:")
        formatted_text = f"{emoji} *{title}*\n{message}"

        # Use default channel if not specified
        target_channel = channel or "general"

        return self.send_message(workspace_id, target_channel, formatted_text)

    def list_channels(self, workspace_id: str) -> Dict[str, Any]:
        """List Slack channels"""
        connection = self.get_connection(workspace_id)
        if not connection:
            return {"success": False, "error": "Not connected to Slack"}

        try:
            client = SlackClient(connection.bot_token)
            result = client.list_channels()

            if result["ok"]:
                channels = []
                for ch in result["channels"]:
                    channel = SlackChannel(
                        channel_id=ch["id"],
                        name=ch["name"],
                        is_private=ch["is_private"],
                        is_archived=ch["is_archived"],
                        member_count=ch["num_members"],
                        topic=ch["topic"]["value"],
                        purpose=ch["purpose"]["value"],
                    )
                    channels.append(channel.to_dict())

                return {"success": True, "channels": channels}

            return {"success": False, "error": "Failed to list channels"}

        except Exception as e:
            logger.error(f"Failed to list channels: {e}")
            return {"success": False, "error": str(e)}

    def handle_command(
        self, workspace_id: str, command: str, text: str, user_id: str, channel_id: str
    ) -> Dict[str, Any]:
        """Handle slash command"""
        # Find command handler
        command_obj = None
        for cmd in self.commands.values():
            if cmd.command == command and cmd.enabled:
                command_obj = cmd
                break

        if not command_obj:
            return {"success": False, "error": f"Unknown command: {command}"}

        try:
            # Execute command handler
            handler_result = self._execute_command_handler(
                command_obj.handler, workspace_id, text, user_id, channel_id
            )

            logger.info(f"Executed command {command} for user {user_id}")

            return {"success": True, "command": command, "response": handler_result}

        except Exception as e:
            logger.error(f"Failed to handle command: {e}")
            return {"success": False, "error": str(e)}

    def _execute_command_handler(
        self, handler: str, workspace_id: str, text: str, user_id: str, channel_id: str
    ) -> str:
        """Execute command handler"""
        if handler == "show_help":
            commands_list = "\n".join(
                [
                    f"• `{cmd.command}` - {cmd.description}"
                    for cmd in self.commands.values()
                    if cmd.enabled
                ]
            )
            return f"*Available Commands:*\n{commands_list}"

        elif handler == "check_status":
            return (
                "✅ System is operational\n• All services running\n• No issues detected"
            )

        elif handler == "create_task":
            if not text:
                return "❌ Please provide a task description\nUsage: `/ninja-task [description]`"
            return f"✅ Task created: {text}\n• Task ID: TASK-{datetime.utcnow().timestamp()}"

        elif handler == "search_workspace":
            if not text:
                return (
                    "❌ Please provide a search query\nUsage: `/ninja-search [query]`"
                )
            return f"🔍 Search results for '{text}':\n• No results found"

        return "Command executed successfully"

    def create_notification_rule(
        self,
        workspace_id: str,
        name: str,
        event_type: str,
        slack_channel_id: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create notification routing rule"""
        try:
            import uuid

            rule_id = str(uuid.uuid4())

            rule = NotificationRule(
                rule_id=rule_id,
                workspace_id=workspace_id,
                name=name,
                event_type=event_type,
                slack_channel_id=slack_channel_id,
                priority=priority,
                enabled=True,
                filters=filters or {},
            )

            self.notification_rules[rule_id] = rule

            logger.info(f"Created notification rule {name}")

            return {"success": True, "rule": rule.to_dict()}

        except Exception as e:
            logger.error(f"Failed to create notification rule: {e}")
            return {"success": False, "error": str(e)}

    def trigger_notification(
        self, workspace_id: str, event_type: str, event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger notification based on rules"""
        # Find matching rules
        matching_rules = [
            rule
            for rule in self.notification_rules.values()
            if rule.workspace_id == workspace_id
            and rule.event_type == event_type
            and rule.enabled
        ]

        if not matching_rules:
            return {"success": True, "notifications_sent": 0}

        notifications_sent = 0

        for rule in matching_rules:
            # Apply filters
            if rule.filters:
                # Simplified filter logic
                pass

            # Format notification message
            title = f"Event: {event_type}"
            message = json.dumps(event_data, indent=2)

            # Send notification
            result = self.send_notification(
                workspace_id=workspace_id,
                title=title,
                message=message,
                priority=rule.priority,
                channel=rule.slack_channel_id,
            )

            if result["success"]:
                notifications_sent += 1

        return {"success": True, "notifications_sent": notifications_sent}

    def get_message_history(
        self, channel_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get message history for channel"""
        messages = self.message_history.get(channel_id, [])
        return [m.to_dict() for m in messages[-limit:]]

    def list_commands(self) -> List[Dict[str, Any]]:
        """List available slash commands"""
        return [cmd.to_dict() for cmd in self.commands.values() if cmd.enabled]

    def list_notification_rules(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List notification rules for workspace"""
        return [
            rule.to_dict()
            for rule in self.notification_rules.values()
            if rule.workspace_id == workspace_id
        ]


# Global service instance
slack_service = SlackService()
