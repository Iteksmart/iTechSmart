"""
REST API Routes
FastAPI routes for iTechSmart HL7
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ..integrations.connection_manager import EMRConnectionManager, EMRType
from .auth import get_current_user, User
from .rate_limiter import rate_limit

# Create API router
api_router = APIRouter(prefix="/api/v1", tags=["api"])

# Global connection manager instance
connection_manager = EMRConnectionManager()


# ============================================================================
# Request/Response Models
# ============================================================================

class ConnectionConfig(BaseModel):
    connection_id: str
    emr_type: str
    config: Dict[str, Any]


class ConnectionResponse(BaseModel):
    id: str
    emr_type: str
    active: bool


class PatientSearchRequest(BaseModel):
    criteria: Dict[str, str]


class PatientResponse(BaseModel):
    id: str
    mrn: Optional[str]
    name: Optional[str]
    gender: Optional[str]
    birth_date: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[Dict]


class ObservationResponse(BaseModel):
    id: str
    code: Optional[Dict]
    value: Optional[Any]
    unit: Optional[str]
    date: Optional[str]
    status: Optional[str]
    category: Optional[str]


class MedicationResponse(BaseModel):
    id: str
    medication: Optional[str]
    dosage: Optional[str]
    status: Optional[str]
    intent: Optional[str]
    authored_on: Optional[str]


class AllergyResponse(BaseModel):
    id: str
    substance: Optional[Dict]
    clinical_status: Optional[str]
    verification_status: Optional[str]
    type: Optional[str]
    category: Optional[str]
    criticality: Optional[str]


class HL7MessageRequest(BaseModel):
    message: str


class AggregateDataRequest(BaseModel):
    patient_identifiers: Dict[str, str]


# ============================================================================
# Connection Management Endpoints
# ============================================================================

@api_router.post("/connections", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
@rate_limit(max_calls=10, time_window=60)
async def create_connection(
    connection: ConnectionConfig,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new EMR connection
    """
    try:
        emr_type = EMRType(connection.emr_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid EMR type: {connection.emr_type}"
        )
    
    success = await connection_manager.add_connection(
        connection.connection_id,
        emr_type,
        connection.config
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create connection"
        )
    
    return {
        "message": "Connection created successfully",
        "connection_id": connection.connection_id
    }


@api_router.get("/connections", response_model=List[ConnectionResponse])
@rate_limit(max_calls=30, time_window=60)
async def list_connections(current_user: User = Depends(get_current_user)):
    """
    List all EMR connections
    """
    connections = connection_manager.list_connections()
    return connections


@api_router.get("/connections/{connection_id}", response_model=ConnectionResponse)
@rate_limit(max_calls=30, time_window=60)
async def get_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get specific EMR connection details
    """
    connections = connection_manager.list_connections()
    connection = next((c for c in connections if c['id'] == connection_id), None)
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection not found: {connection_id}"
        )
    
    return connection


@api_router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
@rate_limit(max_calls=10, time_window=60)
async def delete_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an EMR connection
    """
    success = await connection_manager.remove_connection(connection_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection not found: {connection_id}"
        )


@api_router.post("/connections/{connection_id}/test", response_model=Dict[str, Any])
@rate_limit(max_calls=10, time_window=60)
async def test_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Test an EMR connection
    """
    success = await connection_manager.test_connection(connection_id)
    
    return {
        "connection_id": connection_id,
        "status": "connected" if success else "failed",
        "timestamp": datetime.now().isoformat()
    }


@api_router.get("/connections/stats", response_model=Dict[str, Any])
@rate_limit(max_calls=30, time_window=60)
async def get_connection_stats(current_user: User = Depends(get_current_user)):
    """
    Get connection statistics
    """
    return connection_manager.get_connection_stats()


# ============================================================================
# Patient Endpoints
# ============================================================================

@api_router.get("/connections/{connection_id}/patients/{patient_id}", response_model=PatientResponse)
@rate_limit(max_calls=100, time_window=60)
async def get_patient(
    connection_id: str,
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get patient demographics from specific EMR
    """
    patient = await connection_manager.get_patient(connection_id, patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {patient_id}"
        )
    
    return patient


@api_router.post("/connections/{connection_id}/patients/search", response_model=List[PatientResponse])
@rate_limit(max_calls=50, time_window=60)
async def search_patients(
    connection_id: str,
    search_request: PatientSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search for patients in specific EMR
    """
    patients = await connection_manager.search_patients(
        connection_id,
        search_request.criteria
    )
    
    return patients


@api_router.post("/patients/aggregate", response_model=Dict[str, Any])
@rate_limit(max_calls=20, time_window=60)
async def aggregate_patient_data(
    request: AggregateDataRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Aggregate patient data from multiple EMR systems
    """
    aggregated_data = await connection_manager.aggregate_patient_data(
        request.patient_identifiers
    )
    
    return aggregated_data


# ============================================================================
# Observation Endpoints
# ============================================================================

@api_router.get("/connections/{connection_id}/patients/{patient_id}/observations", response_model=List[ObservationResponse])
@rate_limit(max_calls=100, time_window=60)
async def get_observations(
    connection_id: str,
    patient_id: str,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get patient observations (vitals, labs, etc.)
    """
    observations = await connection_manager.get_observations(
        connection_id,
        patient_id,
        category
    )
    
    return observations


# ============================================================================
# Medication Endpoints
# ============================================================================

@api_router.get("/connections/{connection_id}/patients/{patient_id}/medications", response_model=List[MedicationResponse])
@rate_limit(max_calls=100, time_window=60)
async def get_medications(
    connection_id: str,
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get patient medications
    """
    medications = await connection_manager.get_medications(
        connection_id,
        patient_id
    )
    
    return medications


# ============================================================================
# Allergy Endpoints
# ============================================================================

@api_router.get("/connections/{connection_id}/patients/{patient_id}/allergies", response_model=List[AllergyResponse])
@rate_limit(max_calls=100, time_window=60)
async def get_allergies(
    connection_id: str,
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get patient allergies
    """
    allergies = await connection_manager.get_allergies(
        connection_id,
        patient_id
    )
    
    return allergies


# ============================================================================
# HL7 Messaging Endpoints
# ============================================================================

@api_router.post("/connections/{connection_id}/hl7/send", response_model=Dict[str, Any])
@rate_limit(max_calls=50, time_window=60)
async def send_hl7_message(
    connection_id: str,
    message_request: HL7MessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send HL7 message through specific connection
    """
    ack = await connection_manager.send_hl7_message(
        connection_id,
        message_request.message
    )
    
    if not ack:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send HL7 message"
        )
    
    return {
        "status": "sent",
        "ack": ack,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Health Check Endpoints
# ============================================================================

@api_router.get("/health", response_model=Dict[str, str])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@api_router.get("/health/detailed", response_model=Dict[str, Any])
@rate_limit(max_calls=30, time_window=60)
async def detailed_health_check(current_user: User = Depends(get_current_user)):
    """
    Detailed health check with connection status
    """
    stats = connection_manager.get_connection_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "connections": stats
    }