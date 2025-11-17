"""
Calendar & Scheduling System for iTechSmart Ninja
Provides calendar management, event scheduling, and reminders
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types"""

    MEETING = "meeting"
    TASK = "task"
    REMINDER = "reminder"
    DEADLINE = "deadline"
    APPOINTMENT = "appointment"
    CALL = "call"
    CUSTOM = "custom"


class EventStatus(str, Enum):
    """Event status"""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class RecurrenceType(str, Enum):
    """Recurrence patterns"""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReminderType(str, Enum):
    """Reminder types"""

    EMAIL = "email"
    NOTIFICATION = "notification"
    SMS = "sms"
    WEBHOOK = "webhook"


@dataclass
class Recurrence:
    """Recurrence pattern for events"""

    type: RecurrenceType
    interval: int = 1  # Every N days/weeks/months/years
    end_date: Optional[datetime] = None
    count: Optional[int] = None  # Number of occurrences
    days_of_week: Optional[List[int]] = None  # 0=Monday, 6=Sunday
    day_of_month: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "interval": self.interval,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "count": self.count,
            "days_of_week": self.days_of_week,
            "day_of_month": self.day_of_month,
        }


@dataclass
class Reminder:
    """Reminder configuration"""

    reminder_id: str
    type: ReminderType
    minutes_before: int
    sent: bool = False
    sent_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reminder_id": self.reminder_id,
            "type": self.type.value,
            "minutes_before": self.minutes_before,
            "sent": self.sent,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }


@dataclass
class Attendee:
    """Event attendee"""

    user_id: str
    email: str
    name: str
    status: str = "pending"  # pending, accepted, declined, tentative

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "status": self.status,
        }


@dataclass
class CalendarEvent:
    """Calendar event"""

    event_id: str
    calendar_id: str
    title: str
    description: str
    event_type: EventType
    status: EventStatus
    start_time: datetime
    end_time: datetime
    all_day: bool
    location: Optional[str]
    attendees: List[Attendee]
    reminders: List[Reminder]
    recurrence: Optional[Recurrence]
    metadata: Dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "calendar_id": self.calendar_id,
            "title": self.title,
            "description": self.description,
            "event_type": self.event_type.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "all_day": self.all_day,
            "location": self.location,
            "attendees": [a.to_dict() for a in self.attendees],
            "reminders": [r.to_dict() for r in self.reminders],
            "recurrence": self.recurrence.to_dict() if self.recurrence else None,
            "metadata": self.metadata,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Calendar:
    """Calendar"""

    calendar_id: str
    name: str
    description: str
    owner_id: str
    color: str
    timezone: str
    is_default: bool
    shared_with: Set[str]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "calendar_id": self.calendar_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "color": self.color,
            "timezone": self.timezone,
            "is_default": self.is_default,
            "shared_with": list(self.shared_with),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class CalendarScheduler:
    """Manages calendars, events, and scheduling"""

    def __init__(self):
        """Initialize calendar scheduler"""
        self.calendars: Dict[str, Calendar] = {}
        self.events: Dict[str, CalendarEvent] = {}
        logger.info("CalendarScheduler initialized successfully")

    async def create_calendar(
        self,
        name: str,
        description: str,
        owner_id: str,
        color: str = "#3B82F6",
        timezone: str = "UTC",
        is_default: bool = False,
    ) -> Calendar:
        """
        Create a new calendar

        Args:
            name: Calendar name
            description: Calendar description
            owner_id: Owner user ID
            color: Calendar color (hex)
            timezone: Calendar timezone
            is_default: Is default calendar

        Returns:
            Calendar object
        """
        calendar_id = str(uuid.uuid4())

        calendar = Calendar(
            calendar_id=calendar_id,
            name=name,
            description=description,
            owner_id=owner_id,
            color=color,
            timezone=timezone,
            is_default=is_default,
            shared_with=set(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.calendars[calendar_id] = calendar
        logger.info(f"Calendar {calendar_id} created: {name}")

        return calendar

    async def create_event(
        self,
        calendar_id: str,
        title: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        created_by: str,
        event_type: EventType = EventType.MEETING,
        all_day: bool = False,
        location: Optional[str] = None,
        attendees: Optional[List[Attendee]] = None,
        reminders: Optional[List[Reminder]] = None,
        recurrence: Optional[Recurrence] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CalendarEvent:
        """
        Create a new event

        Args:
            calendar_id: Calendar ID
            title: Event title
            description: Event description
            start_time: Event start time
            end_time: Event end time
            created_by: Creator user ID
            event_type: Event type
            all_day: All-day event
            location: Event location
            attendees: List of attendees
            reminders: List of reminders
            recurrence: Recurrence pattern
            metadata: Additional metadata

        Returns:
            CalendarEvent object
        """
        calendar = self.calendars.get(calendar_id)
        if not calendar:
            raise ValueError(f"Calendar {calendar_id} not found")

        event_id = str(uuid.uuid4())

        event = CalendarEvent(
            event_id=event_id,
            calendar_id=calendar_id,
            title=title,
            description=description,
            event_type=event_type,
            status=EventStatus.SCHEDULED,
            start_time=start_time,
            end_time=end_time,
            all_day=all_day,
            location=location,
            attendees=attendees or [],
            reminders=reminders or [],
            recurrence=recurrence,
            metadata=metadata or {},
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.events[event_id] = event
        logger.info(f"Event {event_id} created: {title}")

        return event

    async def update_event(
        self, event_id: str, updates: Dict[str, Any]
    ) -> CalendarEvent:
        """Update an event"""
        event = self.events.get(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")

        # Update fields
        if "title" in updates:
            event.title = updates["title"]
        if "description" in updates:
            event.description = updates["description"]
        if "start_time" in updates:
            event.start_time = updates["start_time"]
        if "end_time" in updates:
            event.end_time = updates["end_time"]
        if "location" in updates:
            event.location = updates["location"]
        if "status" in updates:
            event.status = EventStatus(updates["status"])

        event.updated_at = datetime.now()

        logger.info(f"Event {event_id} updated")
        return event

    async def cancel_event(self, event_id: str) -> CalendarEvent:
        """Cancel an event"""
        event = self.events.get(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")

        event.status = EventStatus.CANCELLED
        event.updated_at = datetime.now()

        logger.info(f"Event {event_id} cancelled")
        return event

    async def get_events(
        self,
        calendar_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[EventType] = None,
        status: Optional[EventStatus] = None,
    ) -> List[CalendarEvent]:
        """
        Get events with optional filtering

        Args:
            calendar_id: Filter by calendar
            start_date: Filter by start date
            end_date: Filter by end date
            event_type: Filter by event type
            status: Filter by status

        Returns:
            List of events
        """
        events = list(self.events.values())

        if calendar_id:
            events = [e for e in events if e.calendar_id == calendar_id]

        if start_date:
            events = [e for e in events if e.start_time >= start_date]

        if end_date:
            events = [e for e in events if e.end_time <= end_date]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if status:
            events = [e for e in events if e.status == status]

        return events

    async def get_upcoming_events(
        self, calendar_id: str, days: int = 7
    ) -> List[CalendarEvent]:
        """Get upcoming events for next N days"""
        now = datetime.now()
        end_date = now + timedelta(days=days)

        return await self.get_events(
            calendar_id=calendar_id,
            start_date=now,
            end_date=end_date,
            status=EventStatus.SCHEDULED,
        )

    async def check_availability(
        self, calendar_id: str, start_time: datetime, end_time: datetime
    ) -> bool:
        """Check if time slot is available"""
        events = await self.get_events(
            calendar_id=calendar_id,
            start_date=start_time,
            end_date=end_time,
            status=EventStatus.SCHEDULED,
        )

        # Check for overlapping events
        for event in events:
            if start_time < event.end_time and end_time > event.start_time:
                return False

        return True

    async def find_available_slots(
        self,
        calendar_id: str,
        date: datetime,
        duration_minutes: int,
        working_hours_start: int = 9,
        working_hours_end: int = 17,
    ) -> List[Dict[str, datetime]]:
        """
        Find available time slots on a given date

        Args:
            calendar_id: Calendar ID
            date: Date to check
            duration_minutes: Required duration
            working_hours_start: Start of working hours (hour)
            working_hours_end: End of working hours (hour)

        Returns:
            List of available slots
        """
        # Get events for the day
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        events = await self.get_events(
            calendar_id=calendar_id,
            start_date=day_start,
            end_date=day_end,
            status=EventStatus.SCHEDULED,
        )

        # Sort events by start time
        events.sort(key=lambda e: e.start_time)

        # Find gaps
        available_slots = []
        current_time = day_start.replace(hour=working_hours_start)
        end_of_day = day_start.replace(hour=working_hours_end)

        for event in events:
            # Check gap before event
            if event.start_time > current_time:
                gap_minutes = (event.start_time - current_time).total_seconds() / 60
                if gap_minutes >= duration_minutes:
                    available_slots.append(
                        {"start": current_time, "end": event.start_time}
                    )

            current_time = max(current_time, event.end_time)

        # Check gap after last event
        if current_time < end_of_day:
            gap_minutes = (end_of_day - current_time).total_seconds() / 60
            if gap_minutes >= duration_minutes:
                available_slots.append({"start": current_time, "end": end_of_day})

        return available_slots

    async def share_calendar(self, calendar_id: str, user_id: str) -> Calendar:
        """Share calendar with a user"""
        calendar = self.calendars.get(calendar_id)
        if not calendar:
            raise ValueError(f"Calendar {calendar_id} not found")

        calendar.shared_with.add(user_id)
        calendar.updated_at = datetime.now()

        logger.info(f"Calendar {calendar_id} shared with user {user_id}")
        return calendar

    async def unshare_calendar(self, calendar_id: str, user_id: str) -> Calendar:
        """Unshare calendar from a user"""
        calendar = self.calendars.get(calendar_id)
        if not calendar:
            raise ValueError(f"Calendar {calendar_id} not found")

        calendar.shared_with.discard(user_id)
        calendar.updated_at = datetime.now()

        logger.info(f"Calendar {calendar_id} unshared from user {user_id}")
        return calendar

    async def get_calendar(self, calendar_id: str) -> Optional[Calendar]:
        """Get calendar by ID"""
        return self.calendars.get(calendar_id)

    async def list_calendars(self, owner_id: Optional[str] = None) -> List[Calendar]:
        """List calendars with optional filtering"""
        calendars = list(self.calendars.values())

        if owner_id:
            calendars = [
                c
                for c in calendars
                if c.owner_id == owner_id or owner_id in c.shared_with
            ]

        return calendars

    async def delete_calendar(self, calendar_id: str) -> bool:
        """Delete a calendar"""
        if calendar_id in self.calendars:
            # Delete all events in calendar
            events_to_delete = [
                e_id for e_id, e in self.events.items() if e.calendar_id == calendar_id
            ]
            for event_id in events_to_delete:
                del self.events[event_id]

            del self.calendars[calendar_id]
            logger.info(f"Calendar {calendar_id} deleted")
            return True
        return False

    async def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        if event_id in self.events:
            del self.events[event_id]
            logger.info(f"Event {event_id} deleted")
            return True
        return False


# Global calendar scheduler instance
_calendar_scheduler: Optional[CalendarScheduler] = None


def get_calendar_scheduler() -> CalendarScheduler:
    """Get or create global calendar scheduler instance"""
    global _calendar_scheduler
    if _calendar_scheduler is None:
        _calendar_scheduler = CalendarScheduler()
    return _calendar_scheduler
