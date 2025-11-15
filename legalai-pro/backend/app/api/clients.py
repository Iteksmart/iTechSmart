"""
Client Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Client

router = APIRouter()

# Pydantic models
class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "USA"
    ssn: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    notes: Optional[str] = None

class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    ssn: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    company_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    mobile: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: str
    ssn: Optional[str]
    date_of_birth: Optional[datetime]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new client"""
    
    new_client = Client(**client_data.dict())
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    return new_client

@router.get("/", response_model=List[ClientResponse])
async def get_clients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all clients with optional filtering"""
    
    query = db.query(Client)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Client.first_name.ilike(search_filter)) |
            (Client.last_name.ilike(search_filter)) |
            (Client.email.ilike(search_filter)) |
            (Client.company_name.ilike(search_filter))
        )
    
    if is_active is not None:
        query = query.filter(Client.is_active == is_active)
    
    clients = query.offset(skip).limit(limit).all()
    return clients

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific client by ID"""
    
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a client"""
    
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Update only provided fields
    update_data = client_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a client (soft delete)"""
    
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Soft delete
    client.is_active = False
    db.commit()
    
    return None

@router.get("/{client_id}/auto-fill-data")
async def get_client_auto_fill_data(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get client data formatted for auto-filling documents
    This returns all client information in a structured format
    that can be used to populate document templates
    """
    
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Format data for auto-fill
    auto_fill_data = {
        "client_full_name": f"{client.first_name} {client.last_name}",
        "client_first_name": client.first_name,
        "client_last_name": client.last_name,
        "client_company": client.company_name or "",
        "client_email": client.email or "",
        "client_phone": client.phone or "",
        "client_mobile": client.mobile or "",
        "client_address": client.address or "",
        "client_city": client.city or "",
        "client_state": client.state or "",
        "client_zip": client.zip_code or "",
        "client_country": client.country,
        "client_full_address": f"{client.address or ''}, {client.city or ''}, {client.state or ''} {client.zip_code or ''}".strip(", "),
        "client_ssn": client.ssn or "",
        "client_dob": client.date_of_birth.strftime("%m/%d/%Y") if client.date_of_birth else "",
        "client_notes": client.notes or ""
    }
    
    return auto_fill_data