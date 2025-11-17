"""
iTechSmart Sandbox - Template API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Template

router = APIRouter(prefix="/api/templates", tags=["Templates"])


class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image: str
    cpu: float = 1.0
    memory: str = "1Gi"
    gpu: Optional[str] = None
    packages: Optional[List[str]] = None
    env_vars: Optional[Dict[str, str]] = None
    is_public: bool = False


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image: str
    cpu: float
    memory: str
    is_public: bool

    class Config:
        from_attributes = True


@router.post("/", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Create sandbox template"""
    db_template = Template(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/", response_model=List[TemplateResponse])
def list_templates(
    is_public: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List templates"""
    q = db.query(Template)

    if is_public is not None:
        q = q.filter(Template.is_public == is_public)

    return q.limit(limit).all()


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get template details"""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template
