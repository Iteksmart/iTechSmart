"""
Users Router
User management endpoints
"""

from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()


@router.get("/")
async def list_users() -> List[Dict]:
    """List all users"""
    return [
        {
            "id": 1,
            "email": "admin@itechsmart.dev",
            "name": "Admin User",
            "role": "admin",
            "active": True
        }
    ]


@router.get("/{user_id}")
async def get_user(user_id: int) -> Dict:
    """Get user by ID"""
    return {
        "id": user_id,
        "email": "admin@itechsmart.dev",
        "name": "Admin User",
        "role": "admin",
        "active": True
    }