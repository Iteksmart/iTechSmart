"""
iTechSmart Mobile - API Endpoints
"""

from fastapi import APIRouter, HTTPException, Header
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ..core.mobile_gateway import mobile_gateway, DevicePlatform, NotificationType


router = APIRouter(prefix="/api/v1/mobile", tags=["mobile"])


# Request/Response Models
class RegisterDeviceRequest(BaseModel):
    user_id: str
    platform: str
    device_token: str
    device_info: Dict[str, Any]


class UpdateDeviceRequest(BaseModel):
    device_token: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None


class CreateSessionRequest(BaseModel):
    device_id: str
    user_id: str


class TrackEventRequest(BaseModel):
    event_type: str
    event_data: Dict[str, Any]


class QueueDataRequest(BaseModel):
    entity_type: str
    operation: str
    data: Dict[str, Any]


class SendNotificationRequest(BaseModel):
    title: str
    body: str
    notification_type: str = "info"
    data: Optional[Dict[str, Any]] = None


class SendUserNotificationRequest(BaseModel):
    user_id: str
    title: str
    body: str
    notification_type: str = "info"
    data: Optional[Dict[str, Any]] = None


# Device Management Endpoints
@router.post("/devices/register")
async def register_device(request: RegisterDeviceRequest):
    """Register a mobile device"""
    try:
        device_id = mobile_gateway.register_device(
            user_id=request.user_id,
            platform=DevicePlatform(request.platform),
            device_token=request.device_token,
            device_info=request.device_info
        )
        
        return {
            "device_id": device_id,
            "message": "Device registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/devices/{device_id}")
async def get_device(device_id: str):
    """Get device information"""
    device = mobile_gateway.get_device(device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {
        "device_id": device.device_id,
        "user_id": device.user_id,
        "platform": device.platform.value,
        "app_version": device.app_version,
        "os_version": device.os_version,
        "is_active": device.is_active,
        "registered_at": device.registered_at.isoformat(),
        "last_active": device.last_active.isoformat()
    }


@router.put("/devices/{device_id}")
async def update_device(device_id: str, request: UpdateDeviceRequest):
    """Update device information"""
    success = mobile_gateway.update_device(
        device_id=device_id,
        device_token=request.device_token,
        device_info=request.device_info
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"message": "Device updated successfully"}


@router.delete("/devices/{device_id}")
async def deactivate_device(device_id: str):
    """Deactivate a device"""
    success = mobile_gateway.deactivate_device(device_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"message": "Device deactivated successfully"}


@router.get("/users/{user_id}/devices")
async def get_user_devices(user_id: str):
    """Get all devices for a user"""
    devices = mobile_gateway.get_user_devices(user_id)
    
    return {
        "devices": [
            {
                "device_id": d.device_id,
                "platform": d.platform.value,
                "app_version": d.app_version,
                "is_active": d.is_active,
                "last_active": d.last_active.isoformat()
            }
            for d in devices
        ]
    }


# Session Management Endpoints
@router.post("/sessions")
async def create_session(request: CreateSessionRequest):
    """Create a new mobile session"""
    try:
        session_id = mobile_gateway.create_session(
            device_id=request.device_id,
            user_id=request.user_id
        )
        
        return {
            "session_id": session_id,
            "message": "Session created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    session = mobile_gateway.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "device_id": session.device_id,
        "user_id": session.user_id,
        "is_active": session.is_active,
        "started_at": session.started_at.isoformat(),
        "last_activity": session.last_activity.isoformat(),
        "events_count": len(session.events),
        "data_usage": session.data_usage
    }


@router.post("/sessions/{session_id}/heartbeat")
async def session_heartbeat(session_id: str):
    """Update session activity"""
    success = mobile_gateway.update_session_activity(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session updated"}


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: str):
    """End a mobile session"""
    success = mobile_gateway.end_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session ended successfully"}


@router.post("/sessions/{session_id}/events")
async def track_event(session_id: str, request: TrackEventRequest):
    """Track an event in the session"""
    success = mobile_gateway.track_event(
        session_id=session_id,
        event_type=request.event_type,
        event_data=request.event_data
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Event tracked successfully"}


# Offline Data Sync Endpoints
@router.post("/devices/{device_id}/sync/queue")
async def queue_offline_data(device_id: str, request: QueueDataRequest):
    """Queue data for synchronization"""
    try:
        data_id = mobile_gateway.queue_offline_data(
            device_id=device_id,
            entity_type=request.entity_type,
            operation=request.operation,
            data=request.data
        )
        
        return {
            "data_id": data_id,
            "message": "Data queued for sync"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/devices/{device_id}/sync/execute")
async def sync_offline_data(device_id: str):
    """Synchronize offline data for a device"""
    try:
        result = mobile_gateway.sync_offline_data(device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/devices/{device_id}/sync/pending")
async def get_pending_sync_data(device_id: str):
    """Get pending sync data for a device"""
    pending = mobile_gateway.get_pending_sync_data(device_id)
    return {"pending_data": pending}


# Push Notifications Endpoints
@router.post("/devices/{device_id}/notifications")
async def send_notification(device_id: str, request: SendNotificationRequest):
    """Send push notification to a device"""
    try:
        notification_id = mobile_gateway.send_notification(
            device_id=device_id,
            title=request.title,
            body=request.body,
            notification_type=NotificationType(request.notification_type),
            data=request.data
        )
        
        return {
            "notification_id": notification_id,
            "message": "Notification sent successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/notifications/broadcast")
async def send_user_notification(request: SendUserNotificationRequest):
    """Send notification to all user's devices"""
    try:
        notification_ids = mobile_gateway.send_notification_to_user(
            user_id=request.user_id,
            title=request.title,
            body=request.body,
            notification_type=NotificationType(request.notification_type),
            data=request.data
        )
        
        return {
            "notification_ids": notification_ids,
            "devices_count": len(notification_ids),
            "message": "Notifications sent successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/notifications/{notification_id}/delivered")
async def mark_notification_delivered(notification_id: str):
    """Mark notification as delivered"""
    success = mobile_gateway.mark_notification_delivered(notification_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as delivered"}


@router.post("/notifications/{notification_id}/opened")
async def mark_notification_opened(notification_id: str):
    """Mark notification as opened"""
    success = mobile_gateway.mark_notification_opened(notification_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as opened"}


@router.get("/devices/{device_id}/notifications")
async def get_device_notifications(device_id: str, limit: int = 50):
    """Get notifications for a device"""
    notifications = mobile_gateway.get_device_notifications(device_id, limit)
    return {"notifications": notifications}


# Analytics Endpoints
@router.get("/devices/{device_id}/analytics")
async def get_device_analytics(device_id: str):
    """Get analytics for a device"""
    analytics = mobile_gateway.get_device_analytics(device_id)
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return analytics


@router.get("/analytics/platform")
async def get_platform_statistics():
    """Get statistics by platform"""
    stats = mobile_gateway.get_platform_statistics()
    return stats


# API Caching Endpoints
@router.get("/cache/{cache_key}")
async def get_cached_data(cache_key: str):
    """Get cached API response"""
    data = mobile_gateway.get_cached_response(cache_key)
    
    if data is None:
        raise HTTPException(status_code=404, detail="Cache miss")
    
    return {"data": data, "cached": True}


@router.delete("/cache")
async def clear_cache(pattern: Optional[str] = None):
    """Clear cache entries"""
    mobile_gateway.clear_cache(pattern)
    return {"message": "Cache cleared successfully"}


# Health Check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = mobile_gateway.get_platform_statistics()
    
    return {
        "status": "healthy",
        "service": "iTechSmart Mobile",
        "timestamp": datetime.utcnow().isoformat(),
        "statistics": stats
    }