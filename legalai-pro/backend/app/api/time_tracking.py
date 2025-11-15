"""Time Tracking API"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/entries")
async def get_time_entries(current_user: dict = Depends(get_current_user)):
    return {"message": "Time Tracking API - Get entries"}

@router.post("/entries")
async def create_time_entry(current_user: dict = Depends(get_current_user)):
    return {"message": "Time Tracking API - Create entry"}