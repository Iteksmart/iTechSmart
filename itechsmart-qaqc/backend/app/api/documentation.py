"""
API endpoints for documentation management
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.models import Documentation, Product, DocumentationType, DocumentationStatus
from app.core.documentation_manager import DocumentationManager
from pydantic import BaseModel

router = APIRouter(prefix="/documentation", tags=["documentation"])


# Pydantic models
class DocumentationCreate(BaseModel):
    product_id: int
    doc_type: DocumentationType
    title: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    tags: Optional[dict] = None
    metadata: Optional[dict] = None


class DocumentationUpdate(BaseModel):
    title: Optional[str] = None
    file_path: Optional[str] = None
    url: Optional[str] = None
    status: Optional[DocumentationStatus] = None
    completeness_score: Optional[float] = None
    tags: Optional[dict] = None
    metadata: Optional[dict] = None


class DocumentationResponse(BaseModel):
    id: int
    product_id: int
    doc_type: DocumentationType
    title: str
    file_path: Optional[str]
    url: Optional[str]
    status: DocumentationStatus
    completeness_score: float
    word_count: Optional[int]
    section_count: Optional[int]
    code_example_count: Optional[int]
    last_updated: Optional[datetime]
    last_reviewed: Optional[datetime]
    days_since_update: Optional[int]
    is_outdated: bool
    is_auto_generated: bool
    template_used: Optional[str]
    generation_date: Optional[datetime]
    tags: Optional[dict]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerateDocRequest(BaseModel):
    product_id: int
    doc_types: List[DocumentationType]
    force_regenerate: bool = False


@router.get("/", response_model=List[DocumentationResponse])
async def list_documentation(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    doc_type: Optional[DocumentationType] = None,
    status: Optional[DocumentationStatus] = None,
    is_outdated: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all documentation with optional filtering"""
    query = db.query(Documentation)
    
    if product_id is not None:
        query = query.filter(Documentation.product_id == product_id)
    
    if doc_type is not None:
        query = query.filter(Documentation.doc_type == doc_type)
    
    if status is not None:
        query = query.filter(Documentation.status == status)
    
    if is_outdated is not None:
        query = query.filter(Documentation.is_outdated == is_outdated)
    
    docs = query.offset(skip).limit(limit).all()
    return docs


@router.get("/{doc_id}", response_model=DocumentationResponse)
async def get_documentation(doc_id: int, db: Session = Depends(get_db)):
    """Get a specific documentation by ID"""
    doc = db.query(Documentation).filter(Documentation.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documentation not found")
    return doc


@router.post("/", response_model=DocumentationResponse, status_code=status.HTTP_201_CREATED)
async def create_documentation(doc: DocumentationCreate, db: Session = Depends(get_db)):
    """Create a new documentation record"""
    # Verify product exists
    product = db.query(Product).filter(Product.id == doc.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_doc = Documentation(**doc.dict())
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


@router.put("/{doc_id}", response_model=DocumentationResponse)
async def update_documentation(
    doc_id: int,
    doc: DocumentationUpdate,
    db: Session = Depends(get_db)
):
    """Update a documentation record"""
    db_doc = db.query(Documentation).filter(Documentation.id == doc_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Documentation not found")
    
    # Update fields
    update_data = doc.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_doc, field, value)
    
    db_doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_doc)
    return db_doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_documentation(doc_id: int, db: Session = Depends(get_db)):
    """Delete a documentation record"""
    db_doc = db.query(Documentation).filter(Documentation.id == doc_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Documentation not found")
    
    db.delete(db_doc)
    db.commit()
    return None


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_documentation(
    request: GenerateDocRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate documentation for a product"""
    # Verify product exists
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Start generation in background
    background_tasks.add_task(
        generate_docs_task,
        request.product_id,
        product.name,
        request.doc_types,
        request.force_regenerate
    )
    
    return {
        "message": "Documentation generation started",
        "product_id": request.product_id,
        "doc_types": [dt.value for dt in request.doc_types]
    }


async def generate_docs_task(
    product_id: int,
    product_name: str,
    doc_types: List[DocumentationType],
    force_regenerate: bool
):
    """Background task to generate documentation"""
    from app.core.database import get_db_context
    
    with get_db_context() as db:
        doc_manager = DocumentationManager()
        
        for doc_type in doc_types:
            try:
                # Check if documentation already exists
                existing = db.query(Documentation).filter(
                    Documentation.product_id == product_id,
                    Documentation.doc_type == doc_type
                ).first()
                
                if existing and not force_regenerate:
                    continue
                
                # Generate documentation
                result = await doc_manager.generate_documentation(product_name, doc_type.value)
                
                if existing:
                    # Update existing
                    existing.status = DocumentationStatus.UP_TO_DATE
                    existing.completeness_score = result.get("completeness_score", 0.0)
                    existing.word_count = result.get("word_count")
                    existing.section_count = result.get("section_count")
                    existing.code_example_count = result.get("code_example_count")
                    existing.last_updated = datetime.utcnow()
                    existing.is_auto_generated = True
                    existing.generation_date = datetime.utcnow()
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new
                    new_doc = Documentation(
                        product_id=product_id,
                        doc_type=doc_type,
                        title=result.get("title", f"{doc_type.value} Documentation"),
                        file_path=result.get("file_path"),
                        status=DocumentationStatus.UP_TO_DATE,
                        completeness_score=result.get("completeness_score", 0.0),
                        word_count=result.get("word_count"),
                        section_count=result.get("section_count"),
                        code_example_count=result.get("code_example_count"),
                        last_updated=datetime.utcnow(),
                        is_auto_generated=True,
                        generation_date=datetime.utcnow()
                    )
                    db.add(new_doc)
                
                db.commit()
                
            except Exception as e:
                print(f"Error generating {doc_type.value} for {product_name}: {e}")
                continue


@router.post("/{doc_id}/check-freshness")
async def check_documentation_freshness(doc_id: int, db: Session = Depends(get_db)):
    """Check if documentation is up to date"""
    doc = db.query(Documentation).filter(Documentation.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documentation not found")
    
    doc_manager = DocumentationManager()
    is_fresh = await doc_manager.check_documentation_freshness(doc.product_id, doc.doc_type.value)
    
    if not is_fresh:
        doc.is_outdated = True
        doc.status = DocumentationStatus.OUTDATED
        db.commit()
    
    return {
        "doc_id": doc_id,
        "is_fresh": is_fresh,
        "days_since_update": doc.days_since_update,
        "status": doc.status
    }


@router.post("/check-all-freshness")
async def check_all_documentation_freshness(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Check freshness of all documentation"""
    background_tasks.add_task(check_all_freshness_task)
    
    return {"message": "Freshness check started for all documentation"}


async def check_all_freshness_task():
    """Background task to check all documentation freshness"""
    from app.core.database import get_db_context
    
    with get_db_context() as db:
        doc_manager = DocumentationManager()
        docs = db.query(Documentation).all()
        
        for doc in docs:
            try:
                is_fresh = await doc_manager.check_documentation_freshness(
                    doc.product_id,
                    doc.doc_type.value
                )
                
                if not is_fresh:
                    doc.is_outdated = True
                    doc.status = DocumentationStatus.OUTDATED
                else:
                    doc.is_outdated = False
                    if doc.status == DocumentationStatus.OUTDATED:
                        doc.status = DocumentationStatus.UP_TO_DATE
                
                db.commit()
                
            except Exception as e:
                print(f"Error checking freshness for doc {doc.id}: {e}")
                continue


@router.get("/stats/summary")
async def get_documentation_stats(db: Session = Depends(get_db)):
    """Get overall documentation statistics"""
    total_docs = db.query(Documentation).count()
    up_to_date = db.query(Documentation).filter(
        Documentation.status == DocumentationStatus.UP_TO_DATE
    ).count()
    outdated = db.query(Documentation).filter(
        Documentation.status == DocumentationStatus.OUTDATED
    ).count()
    missing = db.query(Documentation).filter(
        Documentation.status == DocumentationStatus.MISSING
    ).count()
    incomplete = db.query(Documentation).filter(
        Documentation.status == DocumentationStatus.INCOMPLETE
    ).count()
    
    # Calculate average completeness
    docs = db.query(Documentation).all()
    avg_completeness = sum(d.completeness_score for d in docs) / len(docs) if docs else 0
    
    # Count auto-generated
    auto_generated = db.query(Documentation).filter(
        Documentation.is_auto_generated == True
    ).count()
    
    return {
        "total_documentation": total_docs,
        "up_to_date": up_to_date,
        "outdated": outdated,
        "missing": missing,
        "incomplete": incomplete,
        "average_completeness": round(avg_completeness, 2),
        "auto_generated_count": auto_generated,
        "coverage_percentage": round((up_to_date / total_docs * 100) if total_docs > 0 else 0, 2)
    }


@router.get("/types/list")
async def list_documentation_types():
    """List all available documentation types"""
    return {
        "types": [
            {"value": dt.value, "name": dt.value.replace("_", " ").title()}
            for dt in DocumentationType
        ]
    }