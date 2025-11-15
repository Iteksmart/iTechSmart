"""Calendar & Scheduling API"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/events")
async def get_events(current_user: dict = Depends(get_current_user)):
    return {"message": "Calendar API - Get events"}

@router.post("/events")
async def create_event(current_user: dict = Depends(get_current_user)):
    return {"message": "Calendar API - Create event"}