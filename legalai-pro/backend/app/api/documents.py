"""
Document Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Document

router = APIRouter()

class DocumentResponse(BaseModel):
    id: int
    case_id: int
    title: str
    description: Optional[str]
    file_path: str
    file_type: Optional[str]
    file_size: Optional[int]
    category: Optional[str]
    tags: Optional[list]
    version: int
    is_template: bool
    ai_summary: Optional[str]
    ai_extracted_data: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/upload")
async def upload_document(
    case_id: int,
    title: str,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document"""
    
    # Save file (implement actual file storage)
    file_path = f"documents/{case_id}/{file.filename}"
    
    new_document = Document(
        case_id=case_id,
        title=title,
        description=description,
        file_path=file_path,
        file_type=file.content_type,
        file_size=0,  # Calculate actual size
        category=category,
        created_by=int(current_user["user_id"])
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    return new_document

@router.get("/case/{case_id}", response_model=List[DocumentResponse])
async def get_case_documents(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all documents for a case"""
    
    documents = db.query(Document).filter(Document.case_id == case_id).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific document"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a document"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}