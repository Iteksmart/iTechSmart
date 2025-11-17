"""Settings & Configuration API"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()


@router.get("/")
async def get_settings(current_user: dict = Depends(get_current_user)):
    return {"message": "Settings API - Get settings"}


@router.put("/")
async def update_settings(current_user: dict = Depends(get_current_user)):
    return {"message": "Settings API - Update settings"}
