"""
iTechSmart Mobile - Mobile API Gateway
Handles mobile app requests, authentication, and data synchronization
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
from uuid import uuid4
import hashlib


class DevicePlatform(str, Enum):
    """Mobile device platforms"""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class SyncStatus(str, Enum):
    """Data synchronization status"""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"


class NotificationType(str, Enum):
    """Push notification types"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ALERT = "alert"


class MobileDevice:
    """Represents a mobile device"""
    
    def __init__(
        self,
        device_id: str,
        user_id: str,
        platform: DevicePlatform,
        device_token: str,
        device_info: Dict[str, Any]
    ):
        self.device_id = device_id
        self.user_id = user_id
        self.platform = platform
        self.device_token = device_token
        self.device_info = device_info
        self.registered_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        self.is_active = True
        self.app_version = device_info.get("app_version", "1.0.0")
        self.os_version = device_info.get("os_version", "unknown")


class MobileSession:
    """Represents a mobile app session"""
    
    def __init__(self, session_id: str, device_id: str, user_id: str):
        self.session_id = session_id
        self.device_id = device_id
        self.user_id = user_id
        self.started_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.is_active = True
        self.events = []
        self.data_usage = 0  # bytes


class OfflineData:
    """Represents offline data to be synced"""
    
    def __init__(
        self,
        data_id: str,
        device_id: str,
        entity_type: str,
        operation: str,
        data: Dict[str, Any]
    ):
        self.data_id = data_id
        self.device_id = device_id
        self.entity_type = entity_type
        self.operation = operation  # create, update, delete
        self.data = data
        self.status = SyncStatus.PENDING
        self.created_at = datetime.utcnow()
        self.synced_at = None
        self.retry_count = 0
        self.error_message = None


class PushNotification:
    """Represents a push notification"""
    
    def __init__(
        self,
        notification_id: str,
        device_id: str,
        title: str,
        body: str,
        notification_type: NotificationType,
        data: Dict[str, Any] = None
    ):
        self.notification_id = notification_id
        self.device_id = device_id
        self.title = title
        self.body = body
        self.notification_type = notification_type
        self.data = data or {}
        self.created_at = datetime.utcnow()
        self.sent_at = None
        self.delivered_at = None
        self.opened_at = None
        self.status = "pending"


class MobileGateway:
    """Mobile API Gateway for handling mobile app requests"""
    
    def __init__(self):
        self.devices: Dict[str, MobileDevice] = {}
        self.sessions: Dict[str, MobileSession] = {}
        self.offline_data: Dict[str, OfflineData] = {}
        self.notifications: Dict[str, PushNotification] = {}
        self.api_cache: Dict[str, Any] = {}
    
    # Device Management
    def register_device(
        self,
        user_id: str,
        platform: DevicePlatform,
        device_token: str,
        device_info: Dict[str, Any]
    ) -> str:
        """Register a mobile device"""
        device_id = str(uuid4())
        
        device = MobileDevice(
            device_id=device_id,
            user_id=user_id,
            platform=platform,
            device_token=device_token,
            device_info=device_info
        )
        
        self.devices[device_id] = device
        return device_id
    
    def get_device(self, device_id: str) -> Optional[MobileDevice]:
        """Get device information"""
        return self.devices.get(device_id)
    
    def update_device(
        self,
        device_id: str,
        device_token: str = None,
        device_info: Dict[str, Any] = None
    ) -> bool:
        """Update device information"""
        device = self.devices.get(device_id)
        if not device:
            return False
        
        if device_token:
            device.device_token = device_token
        if device_info:
            device.device_info.update(device_info)
        
        device.last_active = datetime.utcnow()
        return True
    
    def deactivate_device(self, device_id: str) -> bool:
        """Deactivate a device"""
        device = self.devices.get(device_id)
        if not device:
            return False
        
        device.is_active = False
        return True
    
    def get_user_devices(self, user_id: str) -> List[MobileDevice]:
        """Get all devices for a user"""
        return [d for d in self.devices.values() if d.user_id == user_id and d.is_active]
    
    # Session Management
    def create_session(self, device_id: str, user_id: str) -> str:
        """Create a new mobile session"""
        session_id = str(uuid4())
        
        session = MobileSession(
            session_id=session_id,
            device_id=device_id,
            user_id=user_id
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[MobileSession]:
        """Get session information"""
        return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.last_activity = datetime.utcnow()
        return True
    
    def end_session(self, session_id: str) -> bool:
        """End a mobile session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.is_active = False
        return True
    
    def track_event(
        self,
        session_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """Track an event in the session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        session.events.append(event)
        return True
    
    # Offline Data Sync
    def queue_offline_data(
        self,
        device_id: str,
        entity_type: str,
        operation: str,
        data: Dict[str, Any]
    ) -> str:
        """Queue data for synchronization"""
        data_id = str(uuid4())
        
        offline_data = OfflineData(
            data_id=data_id,
            device_id=device_id,
            entity_type=entity_type,
            operation=operation,
            data=data
        )
        
        self.offline_data[data_id] = offline_data
        return data_id
    
    def sync_offline_data(self, device_id: str) -> Dict[str, Any]:
        """Synchronize offline data for a device"""
        device_data = [
            d for d in self.offline_data.values()
            if d.device_id == device_id and d.status == SyncStatus.PENDING
        ]
        
        synced = []
        failed = []
        
        for data in device_data:
            try:
                data.status = SyncStatus.SYNCING
                
                # Simulate sync operation
                # In production, this would call the appropriate service
                success = True
                
                if success:
                    data.status = SyncStatus.SYNCED
                    data.synced_at = datetime.utcnow()
                    synced.append(data.data_id)
                else:
                    data.status = SyncStatus.FAILED
                    data.retry_count += 1
                    failed.append(data.data_id)
                    
            except Exception as e:
                data.status = SyncStatus.FAILED
                data.error_message = str(e)
                data.retry_count += 1
                failed.append(data.data_id)
        
        return {
            "synced": synced,
            "failed": failed,
            "total": len(device_data)
        }
    
    def get_pending_sync_data(self, device_id: str) -> List[Dict[str, Any]]:
        """Get pending sync data for a device"""
        pending = [
            {
                "data_id": d.data_id,
                "entity_type": d.entity_type,
                "operation": d.operation,
                "created_at": d.created_at.isoformat()
            }
            for d in self.offline_data.values()
            if d.device_id == device_id and d.status == SyncStatus.PENDING
        ]
        
        return pending
    
    # Push Notifications
    def send_notification(
        self,
        device_id: str,
        title: str,
        body: str,
        notification_type: NotificationType = NotificationType.INFO,
        data: Dict[str, Any] = None
    ) -> str:
        """Send push notification to a device"""
        notification_id = str(uuid4())
        
        notification = PushNotification(
            notification_id=notification_id,
            device_id=device_id,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data
        )
        
        self.notifications[notification_id] = notification
        
        # Simulate sending notification
        notification.sent_at = datetime.utcnow()
        notification.status = "sent"
        
        return notification_id
    
    def send_notification_to_user(
        self,
        user_id: str,
        title: str,
        body: str,
        notification_type: NotificationType = NotificationType.INFO,
        data: Dict[str, Any] = None
    ) -> List[str]:
        """Send notification to all user's devices"""
        devices = self.get_user_devices(user_id)
        notification_ids = []
        
        for device in devices:
            notification_id = self.send_notification(
                device_id=device.device_id,
                title=title,
                body=body,
                notification_type=notification_type,
                data=data
            )
            notification_ids.append(notification_id)
        
        return notification_ids
    
    def mark_notification_delivered(self, notification_id: str) -> bool:
        """Mark notification as delivered"""
        notification = self.notifications.get(notification_id)
        if not notification:
            return False
        
        notification.delivered_at = datetime.utcnow()
        notification.status = "delivered"
        return True
    
    def mark_notification_opened(self, notification_id: str) -> bool:
        """Mark notification as opened"""
        notification = self.notifications.get(notification_id)
        if not notification:
            return False
        
        notification.opened_at = datetime.utcnow()
        notification.status = "opened"
        return True
    
    def get_device_notifications(
        self,
        device_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get notifications for a device"""
        notifications = [
            {
                "notification_id": n.notification_id,
                "title": n.title,
                "body": n.body,
                "type": n.notification_type.value,
                "data": n.data,
                "created_at": n.created_at.isoformat(),
                "status": n.status
            }
            for n in self.notifications.values()
            if n.device_id == device_id
        ]
        
        # Sort by created_at descending
        notifications.sort(key=lambda x: x["created_at"], reverse=True)
        
        return notifications[:limit]
    
    # API Response Caching
    def cache_response(
        self,
        cache_key: str,
        data: Any,
        ttl_seconds: int = 300
    ):
        """Cache API response"""
        self.api_cache[cache_key] = {
            "data": data,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds)
        }
    
    def get_cached_response(self, cache_key: str) -> Optional[Any]:
        """Get cached API response"""
        cached = self.api_cache.get(cache_key)
        
        if not cached:
            return None
        
        if datetime.utcnow() > cached["expires_at"]:
            del self.api_cache[cache_key]
            return None
        
        return cached["data"]
    
    def clear_cache(self, pattern: str = None):
        """Clear cache entries"""
        if pattern:
            keys_to_delete = [k for k in self.api_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.api_cache[key]
        else:
            self.api_cache.clear()
    
    # Analytics
    def get_device_analytics(self, device_id: str) -> Dict[str, Any]:
        """Get analytics for a device"""
        device = self.devices.get(device_id)
        if not device:
            return {}
        
        sessions = [s for s in self.sessions.values() if s.device_id == device_id]
        active_sessions = [s for s in sessions if s.is_active]
        
        total_events = sum(len(s.events) for s in sessions)
        total_data_usage = sum(s.data_usage for s in sessions)
        
        return {
            "device_id": device_id,
            "platform": device.platform.value,
            "app_version": device.app_version,
            "total_sessions": len(sessions),
            "active_sessions": len(active_sessions),
            "total_events": total_events,
            "total_data_usage": total_data_usage,
            "last_active": device.last_active.isoformat(),
            "registered_at": device.registered_at.isoformat()
        }
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get statistics by platform"""
        stats = {
            "total_devices": len(self.devices),
            "active_devices": len([d for d in self.devices.values() if d.is_active]),
            "by_platform": {},
            "total_sessions": len(self.sessions),
            "active_sessions": len([s for s in self.sessions.values() if s.is_active]),
            "total_notifications": len(self.notifications),
            "pending_sync": len([d for d in self.offline_data.values() if d.status == SyncStatus.PENDING])
        }
        
        for platform in DevicePlatform:
            platform_devices = [d for d in self.devices.values() if d.platform == platform]
            stats["by_platform"][platform.value] = {
                "total": len(platform_devices),
                "active": len([d for d in platform_devices if d.is_active])
            }
        
        return stats


# Global mobile gateway instance
mobile_gateway = MobileGateway()