"""
Calendar & Scheduling API Endpoints for iTechSmart Ninja
Provides REST API for calendar and event management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from ..core.calendar_scheduler import (
    CalendarScheduler,
    Calendar,
    CalendarEvent,
    Attendee,
    Reminder,
    Recurrence,
    EventType,
    EventStatus,
    RecurrenceType,
    ReminderType,
    get_calendar_scheduler,
)

router = APIRouter(prefix="/calendar", tags=["calendar"])


# Request/Response Models
class CreateCalendarRequest(BaseModel):
    """Request to create a calendar"""

    name: str = Field(..., description="Calendar name")
    description: str = Field(..., description="Calendar description")
    owner_id: str = Field(..., description="Owner user ID")
    color: str = Field(default="#3B82F6", description="Calendar color (hex)")
    timezone: str = Field(default="UTC", description="Calendar timezone")
    is_default: bool = Field(default=False, description="Is default calendar")


class AttendeeRequest(BaseModel):
    """Request for event attendee"""

    user_id: str
    email: str
    name: str
    status: str = "pending"


class ReminderRequest(BaseModel):
    """Request for event reminder"""

    type: str
    minutes_before: int


class RecurrenceRequest(BaseModel):
    """Request for event recurrence"""

    type: str
    interval: int = 1
    end_date: Optional[str] = None
    count: Optional[int] = None
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None


class CreateEventRequest(BaseModel):
    """Request to create an event"""

    calendar_id: str = Field(..., description="Calendar ID")
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Event description")
    start_time: str = Field(..., description="Start time (ISO format)")
    end_time: str = Field(..., description="End time (ISO format)")
    created_by: str = Field(..., description="Creator user ID")
    event_type: str = Field(default="meeting", description="Event type")
    all_day: bool = Field(default=False, description="All-day event")
    location: Optional[str] = Field(default=None, description="Event location")
    attendees: Optional[List[AttendeeRequest]] = Field(
        default=None, description="Attendees"
    )
    reminders: Optional[List[ReminderRequest]] = Field(
        default=None, description="Reminders"
    )
    recurrence: Optional[RecurrenceRequest] = Field(
        default=None, description="Recurrence pattern"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )


class UpdateEventRequest(BaseModel):
    """Request to update an event"""

    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None


class CalendarResponse(BaseModel):
    """Response with calendar information"""

    calendar_id: str
    name: str
    description: str
    owner_id: str
    color: str
    timezone: str
    is_default: bool
    shared_with: List[str]
    created_at: str
    updated_at: str


class EventResponse(BaseModel):
    """Response with event information"""

    event_id: str
    calendar_id: str
    title: str
    description: str
    event_type: str
    status: str
    start_time: str
    end_time: str
    all_day: bool
    location: Optional[str]
    attendees: List[Dict[str, Any]]
    reminders: List[Dict[str, Any]]
    recurrence: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_by: str
    created_at: str
    updated_at: str


class CalendarListResponse(BaseModel):
    """Response with list of calendars"""

    calendars: List[CalendarResponse]
    total: int


class EventListResponse(BaseModel):
    """Response with list of events"""

    events: List[EventResponse]
    total: int


class AvailabilityResponse(BaseModel):
    """Response for availability check"""

    available: bool
    message: str


class AvailableSlotsResponse(BaseModel):
    """Response with available time slots"""

    date: str
    slots: List[Dict[str, str]]
    total: int


# API Endpoints
@router.post("/calendars", response_model=CalendarResponse)
async def create_calendar(
    request: CreateCalendarRequest,
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """
    Create a new calendar

    **Parameters:**
    - **name**: Calendar name
    - **description**: Calendar description
    - **owner_id**: Owner user ID
    - **color**: Calendar color (hex code)
    - **timezone**: Calendar timezone
    - **is_default**: Set as default calendar

    **Returns:**
    - Calendar information
    """
    try:
        calendar = await scheduler.create_calendar(
            name=request.name,
            description=request.description,
            owner_id=request.owner_id,
            color=request.color,
            timezone=request.timezone,
            is_default=request.is_default,
        )

        return CalendarResponse(**calendar.to_dict())

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create calendar: {str(e)}"
        )


@router.post("/events", response_model=EventResponse)
async def create_event(
    request: CreateEventRequest,
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """
    Create a new event

    **Event Types:** meeting, task, reminder, deadline, appointment, call, custom

    **Returns:**
    - Event information
    """
    try:
        # Parse dates
        start_time = datetime.fromisoformat(request.start_time.replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(request.end_time.replace("Z", "+00:00"))

        # Convert attendees
        attendees = None
        if request.attendees:
            attendees = [
                Attendee(user_id=a.user_id, email=a.email, name=a.name, status=a.status)
                for a in request.attendees
            ]

        # Convert reminders
        reminders = None
        if request.reminders:
            import uuid

            reminders = [
                Reminder(
                    reminder_id=str(uuid.uuid4()),
                    type=ReminderType(r.type),
                    minutes_before=r.minutes_before,
                )
                for r in request.reminders
            ]

        # Convert recurrence
        recurrence = None
        if request.recurrence:
            end_date = None
            if request.recurrence.end_date:
                end_date = datetime.fromisoformat(
                    request.recurrence.end_date.replace("Z", "+00:00")
                )

            recurrence = Recurrence(
                type=RecurrenceType(request.recurrence.type),
                interval=request.recurrence.interval,
                end_date=end_date,
                count=request.recurrence.count,
                days_of_week=request.recurrence.days_of_week,
                day_of_month=request.recurrence.day_of_month,
            )

        event = await scheduler.create_event(
            calendar_id=request.calendar_id,
            title=request.title,
            description=request.description,
            start_time=start_time,
            end_time=end_time,
            created_by=request.created_by,
            event_type=EventType(request.event_type),
            all_day=request.all_day,
            location=request.location,
            attendees=attendees,
            reminders=reminders,
            recurrence=recurrence,
            metadata=request.metadata,
        )

        return EventResponse(**event.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    request: UpdateEventRequest,
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """Update an event"""
    try:
        updates = request.dict(exclude_none=True)

        # Parse dates if provided
        if "start_time" in updates:
            updates["start_time"] = datetime.fromisoformat(
                updates["start_time"].replace("Z", "+00:00")
            )
        if "end_time" in updates:
            updates["end_time"] = datetime.fromisoformat(
                updates["end_time"].replace("Z", "+00:00")
            )

        event = await scheduler.update_event(event_id, updates)
        return EventResponse(**event.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")


@router.post("/events/{event_id}/cancel", response_model=EventResponse)
async def cancel_event(
    event_id: str, scheduler: CalendarScheduler = Depends(get_calendar_scheduler)
):
    """Cancel an event"""
    try:
        event = await scheduler.cancel_event(event_id)
        return EventResponse(**event.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel event: {str(e)}")


@router.get("/calendars/{calendar_id}", response_model=CalendarResponse)
async def get_calendar(
    calendar_id: str, scheduler: CalendarScheduler = Depends(get_calendar_scheduler)
):
    """Get calendar information"""
    calendar = await scheduler.get_calendar(calendar_id)
    if not calendar:
        raise HTTPException(status_code=404, detail=f"Calendar {calendar_id} not found")
    return CalendarResponse(**calendar.to_dict())


@router.get("/calendars", response_model=CalendarListResponse)
async def list_calendars(
    owner_id: Optional[str] = None,
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """List all calendars"""
    try:
        calendars = await scheduler.list_calendars(owner_id=owner_id)
        return CalendarListResponse(
            calendars=[CalendarResponse(**c.to_dict()) for c in calendars],
            total=len(calendars),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list calendars: {str(e)}"
        )


@router.get("/events", response_model=EventListResponse)
async def list_events(
    calendar_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """List events with optional filtering"""
    try:
        start = (
            datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            if start_date
            else None
        )
        end = (
            datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            if end_date
            else None
        )
        e_type = EventType(event_type) if event_type else None
        e_status = EventStatus(status) if status else None

        events = await scheduler.get_events(
            calendar_id=calendar_id,
            start_date=start,
            end_date=end,
            event_type=e_type,
            status=e_status,
        )

        return EventListResponse(
            events=[EventResponse(**e.to_dict()) for e in events], total=len(events)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list events: {str(e)}")


@router.get("/calendars/{calendar_id}/upcoming", response_model=EventListResponse)
async def get_upcoming_events(
    calendar_id: str,
    days: int = Query(default=7, ge=1, le=365),
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """Get upcoming events for next N days"""
    try:
        events = await scheduler.get_upcoming_events(calendar_id, days)
        return EventListResponse(
            events=[EventResponse(**e.to_dict()) for e in events], total=len(events)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get upcoming events: {str(e)}"
        )


@router.get(
    "/calendars/{calendar_id}/availability", response_model=AvailabilityResponse
)
async def check_availability(
    calendar_id: str,
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)"),
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """Check if time slot is available"""
    try:
        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

        available = await scheduler.check_availability(calendar_id, start, end)

        return AvailabilityResponse(
            available=available,
            message=(
                "Time slot is available" if available else "Time slot is not available"
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to check availability: {str(e)}"
        )


@router.get(
    "/calendars/{calendar_id}/available-slots", response_model=AvailableSlotsResponse
)
async def find_available_slots(
    calendar_id: str,
    date: str = Query(..., description="Date (ISO format)"),
    duration_minutes: int = Query(..., ge=15, le=480),
    working_hours_start: int = Query(default=9, ge=0, le=23),
    working_hours_end: int = Query(default=17, ge=1, le=24),
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """Find available time slots on a given date"""
    try:
        target_date = datetime.fromisoformat(date.replace("Z", "+00:00"))

        slots = await scheduler.find_available_slots(
            calendar_id=calendar_id,
            date=target_date,
            duration_minutes=duration_minutes,
            working_hours_start=working_hours_start,
            working_hours_end=working_hours_end,
        )

        formatted_slots = [
            {"start": slot["start"].isoformat(), "end": slot["end"].isoformat()}
            for slot in slots
        ]

        return AvailableSlotsResponse(
            date=date, slots=formatted_slots, total=len(formatted_slots)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to find available slots: {str(e)}"
        )


@router.post("/calendars/{calendar_id}/share")
async def share_calendar(
    calendar_id: str,
    user_id: str = Query(..., description="User ID to share with"),
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """Share calendar with a user"""
    try:
        await scheduler.share_calendar(calendar_id, user_id)
        return {"message": f"Calendar {calendar_id} shared with user {user_id}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to share calendar: {str(e)}"
        )


@router.post("/calendars/{calendar_id}/unshare")
async def unshare_calendar(
    calendar_id: str,
    user_id: str = Query(..., description="User ID to unshare from"),
    scheduler: CalendarScheduler = Depends(get_calendar_scheduler),
):
    """Unshare calendar from a user"""
    try:
        await scheduler.unshare_calendar(calendar_id, user_id)
        return {"message": f"Calendar {calendar_id} unshared from user {user_id}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to unshare calendar: {str(e)}"
        )


@router.delete("/calendars/{calendar_id}")
async def delete_calendar(
    calendar_id: str, scheduler: CalendarScheduler = Depends(get_calendar_scheduler)
):
    """Delete a calendar"""
    try:
        success = await scheduler.delete_calendar(calendar_id)
        if success:
            return {"message": f"Calendar {calendar_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=404, detail=f"Calendar {calendar_id} not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete calendar: {str(e)}"
        )


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str, scheduler: CalendarScheduler = Depends(get_calendar_scheduler)
):
    """Delete an event"""
    try:
        success = await scheduler.delete_event(event_id)
        if success:
            return {"message": f"Event {event_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")


@router.get("/health")
async def health_check(scheduler: CalendarScheduler = Depends(get_calendar_scheduler)):
    """Check calendar service health"""
    try:
        calendars = await scheduler.list_calendars()
        events = await scheduler.get_events()

        return {
            "status": "healthy",
            "total_calendars": len(calendars),
            "total_events": len(events),
            "supported_event_types": [t.value for t in EventType],
            "supported_recurrence_types": [r.value for r in RecurrenceType],
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
