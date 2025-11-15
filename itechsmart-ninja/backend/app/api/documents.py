"""
Document Processing API Routes
Provides endpoints for document upload, text extraction, OCR, and conversion
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import List, Optional
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, Document, DocumentTable
from app.integrations.document_processor import DocumentProcessor

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Initialize document processor
doc_processor = DocumentProcessor()

# Upload directory
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload document for processing
    
    Supported formats: PDF, Word, Excel, PowerPoint, Text, Images
    """
    try:
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create database entry
        document = Document(
            user_id=current_user.id,
            filename=file.filename,
            file_type=file_ext,
            file_path=file_path,
            file_size=file_size,
            is_processed=False
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return {
            "success": True,
            "document_id": document.id,
            "filename": file.filename,
            "file_type": file_ext,
            "file_size": file_size,
            "message": "Document uploaded successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    file_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents for current user"""
    try:
        query = db.query(Document).filter(Document.user_id == current_user.id)
        
        if file_type:
            query = query.filter(Document.file_type == file_type)
        
        documents = query.offset(skip).limit(limit).all()
        
        doc_list = []
        for doc in documents:
            doc_list.append({
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "page_count": doc.page_count,
                "is_processed": doc.is_processed,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "processed_at": doc.processed_at.isoformat() if doc.processed_at else None
            })
        
        return {
            "success": True,
            "documents": doc_list,
            "total": len(doc_list),
            "message": "Documents retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}")
async def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document details"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "document": {
                "id": document.id,
                "filename": document.filename,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "page_count": document.page_count,
                "extracted_text": document.extracted_text,
                "metadata": document.metadata,
                "is_processed": document.is_processed,
                "processing_error": document.processing_error,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "processed_at": document.processed_at.isoformat() if document.processed_at else None
            },
            "message": "Document retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from disk
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {
            "success": True,
            "message": "Document deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}/extract-text")
async def extract_text(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract text from document"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract text
        text = await doc_processor.extract_text(document.file_path, document.file_type)
        
        # Update document
        document.extracted_text = text
        document.is_processed = True
        document.processed_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "text": text,
            "length": len(text),
            "message": "Text extracted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        document.processing_error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}/extract-tables")
async def extract_tables(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract tables from document"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract tables
        tables = await doc_processor.extract_tables(document.file_path, document.file_type)
        
        # Save tables to database
        for table in tables:
            doc_table = DocumentTable(
                document_id=document.id,
                page_number=table.get('page', table.get('table_number', 1)),
                table_number=table.get('table_number', 1),
                table_data=table['data'],
                rows=table.get('rows', 0),
                columns=table.get('columns', 0)
            )
            db.add(doc_table)
        
        db.commit()
        
        return {
            "success": True,
            "tables": tables,
            "count": len(tables),
            "message": "Tables extracted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}/extract-images")
async def extract_images(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract images from document"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create output directory
        output_dir = os.path.join(UPLOAD_DIR, f"images_{doc_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract images
        image_paths = await doc_processor.extract_images(
            document.file_path, 
            document.file_type,
            output_dir
        )
        
        return {
            "success": True,
            "images": image_paths,
            "count": len(image_paths),
            "message": "Images extracted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}/extract-metadata")
async def extract_metadata(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract metadata from document"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract metadata
        metadata = await doc_processor.extract_metadata(document.file_path, document.file_type)
        
        # Update document
        document.metadata = metadata
        document.page_count = metadata.get('page_count', metadata.get('slide_count', 0))
        db.commit()
        
        return {
            "success": True,
            "metadata": metadata,
            "message": "Metadata extracted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}/ocr")
async def perform_ocr(
    doc_id: int,
    language: str = "eng",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform OCR on document"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Perform OCR
        text = await doc_processor.perform_ocr(document.file_path, language)
        
        # Update document
        document.extracted_text = text
        document.is_processed = True
        document.processed_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "text": text,
            "length": len(text),
            "message": "OCR completed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        document.processing_error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}/convert")
async def convert_document(
    doc_id: int,
    target_format: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert document to different format"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Convert document
        output_path = await doc_processor.convert_document(
            document.file_path,
            document.file_type,
            target_format
        )
        
        return {
            "success": True,
            "output_path": output_path,
            "target_format": target_format,
            "message": "Document converted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}/search")
async def search_document(
    doc_id: int,
    query: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search within document"""
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Search document
        results = await doc_processor.search_document(
            document.file_path,
            document.file_type,
            query
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "query": query,
            "message": "Search completed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_documents(
    doc_id1: int,
    doc_id2: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare two documents"""
    try:
        # Get both documents
        document1 = db.query(Document).filter(
            Document.id == doc_id1,
            Document.user_id == current_user.id
        ).first()
        
        document2 = db.query(Document).filter(
            Document.id == doc_id2,
            Document.user_id == current_user.id
        ).first()
        
        if not document1 or not document2:
            raise HTTPException(status_code=404, detail="One or both documents not found")
        
        # Compare documents
        comparison = await doc_processor.compare_documents(
            document1.file_path,
            document2.file_path,
            document1.file_type,
            document2.file_type
        )
        
        return {
            "success": True,
            "comparison": comparison,
            "document1": document1.filename,
            "document2": document2.filename,
            "message": "Documents compared successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-process")
async def batch_process_documents(
    doc_ids: List[int],
    operation: str = Query(..., regex="^(extract-text|extract-tables|extract-metadata|ocr)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Batch process multiple documents"""
    try:
        results = []
        
        for doc_id in doc_ids:
            document = db.query(Document).filter(
                Document.id == doc_id,
                Document.user_id == current_user.id
            ).first()
            
            if not document:
                results.append({
                    "doc_id": doc_id,
                    "success": False,
                    "error": "Document not found"
                })
                continue
            
            try:
                if operation == "extract-text":
                    text = await doc_processor.extract_text(document.file_path, document.file_type)
                    document.extracted_text = text
                    document.is_processed = True
                    document.processed_at = datetime.utcnow()
                    result = {"text_length": len(text)}
                    
                elif operation == "extract-tables":
                    tables = await doc_processor.extract_tables(document.file_path, document.file_type)
                    result = {"table_count": len(tables)}
                    
                elif operation == "extract-metadata":
                    metadata = await doc_processor.extract_metadata(document.file_path, document.file_type)
                    document.metadata = metadata
                    result = {"metadata": metadata}
                    
                elif operation == "ocr":
                    text = await doc_processor.perform_ocr(document.file_path)
                    document.extracted_text = text
                    document.is_processed = True
                    document.processed_at = datetime.utcnow()
                    result = {"text_length": len(text)}
                
                db.commit()
                
                results.append({
                    "doc_id": doc_id,
                    "filename": document.filename,
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                document.processing_error = str(e)
                db.commit()
                results.append({
                    "doc_id": doc_id,
                    "filename": document.filename,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "results": results,
            "total": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "message": f"Batch processing completed: {successful}/{len(results)} successful"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))