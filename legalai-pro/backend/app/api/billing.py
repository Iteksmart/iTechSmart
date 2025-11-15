"""Billing & Invoicing API"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/invoices")
async def get_invoices(current_user: dict = Depends(get_current_user)):
    return {"message": "Billing API - Get invoices"}

@router.post("/invoices")
async def create_invoice(current_user: dict = Depends(get_current_user)):
    return {"message": "Billing API - Create invoice"}