"""
Tickets Router
Ticket management endpoints
"""

from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()


@router.get("/")
async def list_tickets() -> List[Dict]:
    """List all tickets"""
    return [
        {
            "id": 1,
            "title": "Sample Ticket",
            "status": "open",
            "priority": "high",
            "created_at": "2024-01-15T10:00:00Z"
        }
    ]


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: int) -> Dict:
    """Get ticket by ID"""
    return {
        "id": ticket_id,
        "title": "Sample Ticket",
        "description": "This is a sample ticket",
        "status": "open",
        "priority": "high",
        "created_at": "2024-01-15T10:00:00Z"
    }