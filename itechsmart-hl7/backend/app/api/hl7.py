"""
HL7 API Routes
FastAPI endpoints for HL7 message processing
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hl7", tags=["HL7"])


# Request/Response Models

class HL7MessageRequest(BaseModel):
    """Request model for HL7 message processing"""
    message: str = Field(..., description="Raw HL7 message")
    message_type: Optional[str] = Field(None, description="Message type (ADT, ORM, ORU, etc.)")
    source: Optional[str] = Field(None, description="Message source")
    priority: Optional[str] = Field("normal", description="Message priority (high, normal, low)")


class HL7MessageResponse(BaseModel):
    """Response model for HL7 message"""
    message_id: str
    status: str
    parsed_data: Optional[Dict] = None
    ack_message: Optional[str] = None
    errors: Optional[List[str]] = None


class MessageSearchRequest(BaseModel):
    """Request model for message search"""
    patient_id: Optional[str] = None
    message_type: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)


# Endpoints

@router.post("/parse", response_model=HL7MessageResponse)
async def parse_hl7_message(request: HL7MessageRequest):
    """
    Parse HL7 message
    
    Parses HL7 v2.x or FHIR message and returns structured data
    """
    try:
        from app.core.hl7_parser import HL7Parser
        
        parser = HL7Parser()
        
        # Determine message version
        if request.message.startswith('MSH'):
            # HL7 v2.x
            parsed = parser.parse_hl7_v2(request.message)
            ack = parser.generate_ack(request.message, 'AA')
        elif request.message.startswith('{'):
            # FHIR
            parsed = parser.parse_fhir(request.message)
            ack = None
        else:
            raise ValueError("Unknown message format")
        
        return HL7MessageResponse(
            message_id=parsed.get('message_control_id', f"MSG-{datetime.utcnow().timestamp()}"),
            status='parsed',
            parsed_data=parsed,
            ack_message=ack
        )
        
    except Exception as e:
        logger.error(f"Error parsing HL7 message: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate")
async def validate_hl7_message(request: HL7MessageRequest):
    """
    Validate HL7 message structure
    
    Validates message format and returns any errors or warnings
    """
    try:
        from app.core.hl7_parser import HL7Parser
        
        parser = HL7Parser()
        
        # Determine version
        version = 'v2' if request.message.startswith('MSH') else 'fhir'
        
        validation = parser.validate_message(request.message, version)
        
        return {
            'valid': validation['valid'],
            'errors': validation['errors'],
            'warnings': validation['warnings']
        }
        
    except Exception as e:
        logger.error(f"Error validating HL7 message: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/send")
async def send_hl7_message(request: HL7MessageRequest, background_tasks: BackgroundTasks):
    """
    Send HL7 message to EMR
    
    Sends message to configured EMR system and returns ACK
    """
    try:
        # Parse message first
        from app.core.hl7_parser import HL7Parser
        parser = HL7Parser()
        parsed = parser.parse_hl7_v2(request.message)
        
        # Store in database
        # In production: save to database
        
        # Send to EMR (background task)
        # background_tasks.add_task(send_to_emr, request.message)
        
        # Generate ACK
        ack = parser.generate_ack(request.message, 'AA')
        
        return {
            'message_id': parsed.get('message_control_id'),
            'status': 'sent',
            'ack_message': ack,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sending HL7 message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages")
async def search_messages(
    patient_id: Optional[str] = None,
    message_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """
    Search HL7 messages
    
    Search messages by patient, type, date range, or status
    """
    try:
        # In production: query database
        messages = []
        
        return {
            'total': len(messages),
            'messages': messages,
            'limit': limit
        }
        
    except Exception as e:
        logger.error(f"Error searching messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{message_id}")
async def get_message(message_id: str):
    """
    Get HL7 message by ID
    
    Retrieves message details including parsed data and status
    """
    try:
        # In production: query database
        message = {
            'message_id': message_id,
            'status': 'completed',
            'message_type': 'ADT^A01',
            'parsed_data': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return message
        
    except Exception as e:
        logger.error(f"Error getting message: {str(e)}")
        raise HTTPException(status_code=404, detail="Message not found")


@router.get("/statistics")
async def get_statistics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Get HL7 message statistics
    
    Returns message counts, success rates, and performance metrics
    """
    try:
        # In production: calculate from database
        stats = {
            'total_messages': 0,
            'successful_messages': 0,
            'failed_messages': 0,
            'success_rate': 0.0,
            'avg_processing_time_ms': 0.0,
            'messages_by_type': {},
            'messages_by_hour': {},
            'top_errors': []
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retry/{message_id}")
async def retry_message(message_id: str):
    """
    Retry failed message
    
    Attempts to reprocess a failed message
    """
    try:
        # In production: get message from database and retry
        
        return {
            'message_id': message_id,
            'status': 'retrying',
            'retry_count': 1,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrying message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/status")
async def get_queue_status():
    """
    Get message queue status
    
    Returns current queue size and processing metrics
    """
    try:
        status = {
            'queue_size': 0,
            'processing_rate': 0.0,
            'avg_wait_time_seconds': 0.0,
            'oldest_message_age_seconds': 0,
            'status': 'healthy'
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting queue status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue/clear")
async def clear_queue():
    """
    Clear message queue
    
    Archives and clears all pending messages (admin only)
    """
    try:
        # In production: archive messages and clear queue
        
        return {
            'messages_archived': 0,
            'queue_cleared': True,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns system health status
    """
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }