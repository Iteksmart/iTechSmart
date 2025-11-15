"""Document Templates API"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
async def get_templates(current_user: dict = Depends(get_current_user)):
    return {"message": "Templates API - Get templates"}

@router.post("/")
async def create_template(current_user: dict = Depends(get_current_user)):
    return {"message": "Templates API - Create template"}