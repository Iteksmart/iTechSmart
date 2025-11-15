"""
API endpoints for product management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.models import Product, ProductStatus
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])


# Pydantic models for request/response
class ProductCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    version: Optional[str] = None
    port: Optional[int] = None
    base_url: Optional[str] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None


class ProductUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    port: Optional[int] = None
    base_url: Optional[str] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    status: Optional[ProductStatus] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    version: Optional[str]
    port: Optional[int]
    base_url: Optional[str]
    repository_url: Optional[str]
    documentation_url: Optional[str]
    status: ProductStatus
    is_active: bool
    qa_score: float
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    last_health_check: Optional[datetime]
    last_qa_scan: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    status: Optional[ProductStatus] = None,
    db: Session = Depends(get_db)
):
    """List all products with optional filtering"""
    query = db.query(Product)
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    if status is not None:
        query = query.filter(Product.status == status)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/name/{product_name}", response_model=ProductResponse)
async def get_product_by_name(product_name: str, db: Session = Depends(get_db)):
    """Get a specific product by name"""
    product = db.query(Product).filter(Product.name == product_name).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check if product already exists
    existing = db.query(Product).filter(Product.name == product.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    update_data = product.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db_product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return None


@router.get("/{product_id}/stats")
async def get_product_stats(product_id: int, db: Session = Depends(get_db)):
    """Get detailed statistics for a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product_id": product.id,
        "name": product.name,
        "qa_score": product.qa_score,
        "total_checks": product.total_checks,
        "passed_checks": product.passed_checks,
        "failed_checks": product.failed_checks,
        "warning_checks": product.warning_checks,
        "pass_rate": (product.passed_checks / product.total_checks * 100) if product.total_checks > 0 else 0,
        "status": product.status,
        "last_health_check": product.last_health_check,
        "last_qa_scan": product.last_qa_scan
    }


@router.post("/{product_id}/activate")
async def activate_product(product_id: int, db: Session = Depends(get_db)):
    """Activate a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = True
    product.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Product activated successfully", "product_id": product_id}


@router.post("/{product_id}/deactivate")
async def deactivate_product(product_id: int, db: Session = Depends(get_db)):
    """Deactivate a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    product.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Product deactivated successfully", "product_id": product_id}