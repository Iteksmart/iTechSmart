"""Email Integration API"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()


@router.get("/")
async def get_emails(current_user: dict = Depends(get_current_user)):
    return {"message": "Email API - Get emails"}


@router.post("/send")
async def send_email(current_user: dict = Depends(get_current_user)):
    return {"message": "Email API - Send email"}
