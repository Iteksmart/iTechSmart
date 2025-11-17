"""
iTechSmart Notify - Omnichannel Notification Platform
Email, SMS, Push, Slack, Teams, WhatsApp notifications
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4


class Channel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"
    WHATSAPP = "whatsapp"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    OPENED = "opened"
    CLICKED = "clicked"


class Template:
    def __init__(self, template_id: str, name: str, channel: Channel, content: str):
        self.template_id = template_id
        self.name = name
        self.channel = channel
        self.content = content
        self.variables = []
        self.created_at = datetime.utcnow()
        self.usage_count = 0


class Notification:
    def __init__(
        self, notification_id: str, channel: Channel, recipient: str, content: str
    ):
        self.notification_id = notification_id
        self.channel = channel
        self.recipient = recipient
        self.content = content
        self.status = NotificationStatus.PENDING
        self.sent_at = None
        self.delivered_at = None
        self.opened_at = None
        self.created_at = datetime.utcnow()


class Campaign:
    def __init__(self, campaign_id: str, name: str, template_id: str):
        self.campaign_id = campaign_id
        self.name = name
        self.template_id = template_id
        self.recipients = []
        self.scheduled_at = None
        self.sent_count = 0
        self.delivered_count = 0
        self.opened_count = 0
        self.clicked_count = 0


class NotifyEngine:
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self.notifications: Dict[str, Notification] = {}
        self.campaigns: Dict[str, Campaign] = {}
        self.rate_limits: Dict[Channel, int] = {
            Channel.EMAIL: 1000,
            Channel.SMS: 100,
            Channel.PUSH: 10000,
            Channel.SLACK: 500,
            Channel.TEAMS: 500,
            Channel.WHATSAPP: 100,
        }

    def create_template(
        self, name: str, channel: Channel, content: str, variables: List[str]
    ) -> str:
        """Create notification template"""
        template_id = str(uuid4())
        template = Template(template_id, name, channel, content)
        template.variables = variables
        self.templates[template_id] = template
        return template_id

    def send_notification(
        self,
        channel: Channel,
        recipient: str,
        content: str,
        template_id: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
    ) -> str:
        """Send a notification"""
        notification_id = str(uuid4())

        # Use template if provided
        if template_id:
            template = self.templates.get(template_id)
            if template:
                content = template.content
                if variables:
                    for key, value in variables.items():
                        content = content.replace(f"{{{key}}}", value)
                template.usage_count += 1

        notification = Notification(notification_id, channel, recipient, content)
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()

        # Simulate delivery
        notification.status = NotificationStatus.DELIVERED
        notification.delivered_at = datetime.utcnow()

        self.notifications[notification_id] = notification
        return notification_id

    def send_bulk(
        self,
        channel: Channel,
        recipients: List[str],
        content: str,
        template_id: Optional[str] = None,
    ) -> List[str]:
        """Send bulk notifications"""
        notification_ids = []

        for recipient in recipients:
            notification_id = self.send_notification(
                channel=channel,
                recipient=recipient,
                content=content,
                template_id=template_id,
            )
            notification_ids.append(notification_id)

        return notification_ids

    def create_campaign(
        self, name: str, template_id: str, recipients: List[str]
    ) -> str:
        """Create notification campaign"""
        campaign_id = str(uuid4())
        campaign = Campaign(campaign_id, name, template_id)
        campaign.recipients = recipients
        self.campaigns[campaign_id] = campaign
        return campaign_id

    def schedule_campaign(self, campaign_id: str, scheduled_at: datetime) -> bool:
        """Schedule campaign"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return False

        campaign.scheduled_at = scheduled_at
        return True

    def track_open(self, notification_id: str) -> bool:
        """Track notification open"""
        notification = self.notifications.get(notification_id)
        if not notification:
            return False

        notification.status = NotificationStatus.OPENED
        notification.opened_at = datetime.utcnow()
        return True

    def track_click(self, notification_id: str) -> bool:
        """Track notification click"""
        notification = self.notifications.get(notification_id)
        if not notification:
            return False

        notification.status = NotificationStatus.CLICKED
        return True

    def get_analytics(self, channel: Optional[Channel] = None) -> Dict[str, Any]:
        """Get notification analytics"""
        notifications = list(self.notifications.values())

        if channel:
            notifications = [n for n in notifications if n.channel == channel]

        total = len(notifications)
        sent = len(
            [
                n
                for n in notifications
                if n.status
                in [
                    NotificationStatus.SENT,
                    NotificationStatus.DELIVERED,
                    NotificationStatus.OPENED,
                ]
            ]
        )
        delivered = len(
            [
                n
                for n in notifications
                if n.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED]
            ]
        )
        opened = len(
            [n for n in notifications if n.status == NotificationStatus.OPENED]
        )

        return {
            "total_notifications": total,
            "sent": sent,
            "delivered": delivered,
            "opened": opened,
            "delivery_rate": (delivered / total * 100) if total > 0 else 0,
            "open_rate": (opened / delivered * 100) if delivered > 0 else 0,
        }

    def get_statistics(self) -> Dict[str, Any]:
        by_channel = {}
        for channel in Channel:
            channel_notifications = [
                n for n in self.notifications.values() if n.channel == channel
            ]
            by_channel[channel.value] = len(channel_notifications)

        return {
            "total_templates": len(self.templates),
            "total_notifications": len(self.notifications),
            "total_campaigns": len(self.campaigns),
            "by_channel": by_channel,
        }


notify_engine = NotifyEngine()
