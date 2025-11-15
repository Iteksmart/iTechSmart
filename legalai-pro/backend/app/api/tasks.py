"""Task Management API"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
async def get_tasks(current_user: dict = Depends(get_current_user)):
    return {"message": "Tasks API - Get tasks"}

@router.post("/")
async def create_task(current_user: dict = Depends(get_current_user)):
    return {"message": "Tasks API - Create task"}