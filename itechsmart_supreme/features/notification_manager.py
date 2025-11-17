"""
Notification Manager - Multi-channel notifications
Supports Slack, Email, SMS, PagerDuty, Microsoft Teams, Telegram
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from enum import Enum
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..core.models import Alert, RemediationAction


class NotificationChannel(Enum):
    """Supported notification channels"""

    SLACK = "slack"
    EMAIL = "email"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"


class NotificationManager:
    """
    Multi-channel notification manager
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.channels = {}

        # Initialize channels
        self._initialize_channels()

    def _initialize_channels(self):
        """Initialize notification channels"""

        # Slack
        if self.config.get("slack_webhook_url"):
            self.channels[NotificationChannel.SLACK] = {
                "webhook_url": self.config["slack_webhook_url"],
                "enabled": True,
            }

        # Email
        if self.config.get("smtp_server"):
            self.channels[NotificationChannel.EMAIL] = {
                "smtp_server": self.config["smtp_server"],
                "smtp_port": self.config.get("smtp_port", 587),
                "smtp_username": self.config.get("smtp_username"),
                "smtp_password": self.config.get("smtp_password"),
                "from_email": self.config.get("from_email"),
                "enabled": True,
            }

        # PagerDuty
        if self.config.get("pagerduty_api_key"):
            self.channels[NotificationChannel.PAGERDUTY] = {
                "api_key": self.config["pagerduty_api_key"],
                "service_id": self.config.get("pagerduty_service_id"),
                "enabled": True,
            }

        # Microsoft Teams
        if self.config.get("teams_webhook_url"):
            self.channels[NotificationChannel.TEAMS] = {
                "webhook_url": self.config["teams_webhook_url"],
                "enabled": True,
            }

        # Telegram
        if self.config.get("telegram_bot_token"):
            self.channels[NotificationChannel.TELEGRAM] = {
                "bot_token": self.config["telegram_bot_token"],
                "chat_id": self.config.get("telegram_chat_id"),
                "enabled": True,
            }

    async def send_alert_notification(
        self, alert: Alert, channels: Optional[List[NotificationChannel]] = None
    ):
        """Send alert notification to specified channels"""

        if channels is None:
            channels = list(self.channels.keys())

        message = self._format_alert_message(alert)

        tasks = []
        for channel in channels:
            if channel in self.channels and self.channels[channel]["enabled"]:
                tasks.append(self._send_to_channel(channel, message, alert))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def send_action_notification(
        self,
        action: RemediationAction,
        status: str,
        channels: Optional[List[NotificationChannel]] = None,
    ):
        """Send action notification"""

        if channels is None:
            channels = list(self.channels.keys())

        message = self._format_action_message(action, status)

        tasks = []
        for channel in channels:
            if channel in self.channels and self.channels[channel]["enabled"]:
                tasks.append(self._send_to_channel(channel, message, None))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_to_channel(
        self,
        channel: NotificationChannel,
        message: Dict[str, Any],
        alert: Optional[Alert],
    ):
        """Send message to specific channel"""

        try:
            if channel == NotificationChannel.SLACK:
                await self._send_slack(message)

            elif channel == NotificationChannel.EMAIL:
                await self._send_email(message)

            elif channel == NotificationChannel.PAGERDUTY:
                await self._send_pagerduty(message, alert)

            elif channel == NotificationChannel.TEAMS:
                await self._send_teams(message)

            elif channel == NotificationChannel.TELEGRAM:
                await self._send_telegram(message)

            self.logger.info(f"Notification sent to {channel.value}")

        except Exception as e:
            self.logger.error(f"Failed to send notification to {channel.value}: {e}")

    async def _send_slack(self, message: Dict[str, Any]):
        """Send Slack notification"""

        channel_config = self.channels[NotificationChannel.SLACK]

        payload = {
            "text": message["title"],
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": message["title"]},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": message["body"]},
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:* {message.get('severity', 'N/A')}",
                        }
                    ],
                },
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                channel_config["webhook_url"], json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"Slack API error: {response.status}")

    async def _send_email(self, message: Dict[str, Any]):
        """Send email notification"""

        channel_config = self.channels[NotificationChannel.EMAIL]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = message["title"]
        msg["From"] = channel_config["from_email"]
        msg["To"] = ", ".join(self.config.get("email_recipients", []))

        html_body = f"""
        <html>
          <body>
            <h2>{message['title']}</h2>
            <p>{message['body']}</p>
            <p><strong>Severity:</strong> {message.get('severity', 'N/A')}</p>
            <p><strong>Time:</strong> {message.get('timestamp', 'N/A')}</p>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html"))

        # Send email
        with smtplib.SMTP(
            channel_config["smtp_server"], channel_config["smtp_port"]
        ) as server:
            server.starttls()
            if channel_config.get("smtp_username"):
                server.login(
                    channel_config["smtp_username"], channel_config["smtp_password"]
                )
            server.send_message(msg)

    async def _send_pagerduty(self, message: Dict[str, Any], alert: Optional[Alert]):
        """Send PagerDuty notification"""

        channel_config = self.channels[NotificationChannel.PAGERDUTY]

        payload = {
            "routing_key": channel_config["api_key"],
            "event_action": "trigger",
            "payload": {
                "summary": message["title"],
                "severity": message.get("severity", "error"),
                "source": message.get("host", "iTechSmart Supreme"),
                "custom_details": {"description": message["body"]},
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://events.pagerduty.com/v2/enqueue", json=payload
            ) as response:
                if response.status != 202:
                    raise Exception(f"PagerDuty API error: {response.status}")

    async def _send_teams(self, message: Dict[str, Any]):
        """Send Microsoft Teams notification"""

        channel_config = self.channels[NotificationChannel.TEAMS]

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": message["title"],
            "themeColor": self._get_color_for_severity(message.get("severity")),
            "title": message["title"],
            "sections": [
                {
                    "activityTitle": "iTechSmart Supreme Alert",
                    "activitySubtitle": message.get("timestamp", ""),
                    "text": message["body"],
                    "facts": [
                        {"name": "Severity", "value": message.get("severity", "N/A")},
                        {"name": "Host", "value": message.get("host", "N/A")},
                    ],
                }
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                channel_config["webhook_url"], json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"Teams API error: {response.status}")

    async def _send_telegram(self, message: Dict[str, Any]):
        """Send Telegram notification"""

        channel_config = self.channels[NotificationChannel.TELEGRAM]

        text = f"*{message['title']}*\n\n{message['body']}\n\n*Severity:* {message.get('severity', 'N/A')}"

        payload = {
            "chat_id": channel_config["chat_id"],
            "text": text,
            "parse_mode": "Markdown",
        }

        url = f"https://api.telegram.org/bot{channel_config['bot_token']}/sendMessage"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Telegram API error: {response.status}")

    def _format_alert_message(self, alert: Alert) -> Dict[str, Any]:
        """Format alert as notification message"""

        return {
            "title": f"🚨 Alert: {alert.message}",
            "body": f"Host: {alert.host}\nSource: {alert.source.value}\nTags: {', '.join(alert.tags)}",
            "severity": alert.severity.value,
            "host": alert.host,
            "timestamp": alert.timestamp.isoformat(),
        }

    def _format_action_message(
        self, action: RemediationAction, status: str
    ) -> Dict[str, Any]:
        """Format action as notification message"""

        emoji = "✅" if status == "success" else "❌"

        return {
            "title": f"{emoji} Action {status}: {action.description}",
            "body": f"Command: {action.command}\nRisk Level: {action.risk_level.value}",
            "severity": action.risk_level.value,
            "timestamp": action.created_at.isoformat(),
        }

    def _get_color_for_severity(self, severity: Optional[str]) -> str:
        """Get color code for severity"""

        colors = {
            "critical": "FF0000",
            "high": "FF6600",
            "medium": "FFCC00",
            "low": "00CC00",
        }

        return colors.get(severity, "0078D7")
