"""Reports & Analytics API"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
async def get_reports(current_user: dict = Depends(get_current_user)):
    return {"message": "Reports API - Get reports"}

@router.get("/analytics")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    return {"message": "Reports API - Get analytics"}