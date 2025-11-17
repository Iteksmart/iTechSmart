"""
Privacy API Endpoints for iTechSmart Ninja
Provides REST API for privacy settings and data protection
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from ..core.privacy import (
    PrivacyManager,
    PrivacySettings,
    PrivacyLevel,
    DataCategory,
    ConsentType,
    DataRetentionPeriod,
    DataAccessLog,
    DataExportRequest,
    DataDeletionRequest,
    get_privacy_manager,
)

router = APIRouter(prefix="/privacy", tags=["privacy"])


# Request/Response Models
class PrivacySettingsResponse(BaseModel):
    """Response with privacy settings"""

    user_id: str
    privacy_level: str
    consents: Dict[str, bool]
    data_retention: Dict[str, str]
    opt_outs: List[str]
    anonymize_data: bool
    allow_ai_training: bool
    allow_third_party_sharing: bool
    allow_analytics: bool
    allow_marketing: bool
    data_export_requested: bool
    data_deletion_requested: bool
    created_at: str
    updated_at: str


class UpdatePrivacySettingsRequest(BaseModel):
    """Request to update privacy settings"""

    privacy_level: Optional[str] = None
    consents: Optional[Dict[str, bool]] = None
    data_retention: Optional[Dict[str, str]] = None
    opt_outs: Optional[List[str]] = None
    anonymize_data: Optional[bool] = None
    allow_ai_training: Optional[bool] = None
    allow_third_party_sharing: Optional[bool] = None
    allow_analytics: Optional[bool] = None
    allow_marketing: Optional[bool] = None


class ConsentCheckResponse(BaseModel):
    """Response for consent check"""

    user_id: str
    consent_type: str
    granted: bool


class OptOutRequest(BaseModel):
    """Request to opt out of a feature"""

    feature: str = Field(..., description="Feature to opt out of")


class DataAccessLogResponse(BaseModel):
    """Response with data access log"""

    log_id: str
    user_id: str
    accessor_id: str
    data_category: str
    access_type: str
    purpose: str
    timestamp: str
    ip_address: Optional[str]
    user_agent: Optional[str]


class DataExportRequestModel(BaseModel):
    """Request for data export"""

    categories: List[str] = Field(..., description="Data categories to export")
    format: str = Field(default="json", description="Export format (json, csv, xml)")


class DataExportResponse(BaseModel):
    """Response for data export request"""

    request_id: str
    user_id: str
    categories: List[str]
    format: str
    status: str
    requested_at: str
    completed_at: Optional[str]
    download_url: Optional[str]
    expires_at: Optional[str]


class DataDeletionRequestModel(BaseModel):
    """Request for data deletion"""

    categories: List[str] = Field(..., description="Data categories to delete")
    reason: str = Field(..., description="Reason for deletion")
    verification_required: bool = Field(
        default=True, description="Require verification"
    )


class DataDeletionResponse(BaseModel):
    """Response for data deletion request"""

    request_id: str
    user_id: str
    categories: List[str]
    reason: str
    status: str
    requested_at: str
    completed_at: Optional[str]
    verification_required: bool
    verified: bool


# API Endpoints
@router.get("/settings/{user_id}", response_model=PrivacySettingsResponse)
async def get_privacy_settings(
    user_id: str, manager: PrivacyManager = Depends(get_privacy_manager)
):
    """
    Get privacy settings for a user

    **Parameters:**
    - **user_id**: User ID

    **Returns:**
    - Complete privacy settings including consents, retention policies, and opt-outs
    """
    try:
        settings = await manager.get_privacy_settings(user_id)
        return PrivacySettingsResponse(**settings.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get privacy settings: {str(e)}"
        )


@router.put("/settings/{user_id}", response_model=PrivacySettingsResponse)
async def update_privacy_settings(
    user_id: str,
    request: UpdatePrivacySettingsRequest,
    manager: PrivacyManager = Depends(get_privacy_manager),
):
    """
    Update privacy settings for a user

    **Parameters:**
    - **user_id**: User ID
    - **privacy_level**: Privacy protection level
    - **consents**: Consent preferences
    - **data_retention**: Data retention policies
    - **opt_outs**: Features to opt out of
    - **anonymize_data**: Enable data anonymization
    - **allow_ai_training**: Allow data for AI training
    - **allow_third_party_sharing**: Allow third-party data sharing
    - **allow_analytics**: Allow analytics tracking
    - **allow_marketing**: Allow marketing communications

    **Returns:**
    - Updated privacy settings
    """
    try:
        updates = request.dict(exclude_none=True)
        settings = await manager.update_privacy_settings(user_id, updates)
        return PrivacySettingsResponse(**settings.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update privacy settings: {str(e)}"
        )


@router.get("/consent/{user_id}/{consent_type}", response_model=ConsentCheckResponse)
async def check_consent(
    user_id: str,
    consent_type: str,
    manager: PrivacyManager = Depends(get_privacy_manager),
):
    """
    Check if user has given consent for a specific purpose

    **Parameters:**
    - **user_id**: User ID
    - **consent_type**: Type of consent (essential, functional, analytics, marketing, third_party, ai_training)

    **Returns:**
    - Consent status
    """
    try:
        consent_enum = ConsentType(consent_type)
        granted = await manager.check_consent(user_id, consent_enum)

        return ConsentCheckResponse(
            user_id=user_id, consent_type=consent_type, granted=granted
        )
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid consent type: {consent_type}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to check consent: {str(e)}"
        )


@router.post("/opt-out/{user_id}")
async def opt_out(
    user_id: str,
    request: OptOutRequest,
    manager: PrivacyManager = Depends(get_privacy_manager),
):
    """
    Opt out of a specific feature or service

    **Parameters:**
    - **user_id**: User ID
    - **feature**: Feature to opt out of

    **Returns:**
    - Success message
    """
    try:
        await manager.opt_out(user_id, request.feature)
        return {"message": f"User {user_id} opted out of {request.feature}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to opt out: {str(e)}")


@router.post("/opt-in/{user_id}")
async def opt_in(
    user_id: str,
    request: OptOutRequest,
    manager: PrivacyManager = Depends(get_privacy_manager),
):
    """
    Opt in to a specific feature or service

    **Parameters:**
    - **user_id**: User ID
    - **feature**: Feature to opt in to

    **Returns:**
    - Success message
    """
    try:
        await manager.opt_in(user_id, request.feature)
        return {"message": f"User {user_id} opted in to {request.feature}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to opt in: {str(e)}")


@router.get("/opt-out/{user_id}/{feature}")
async def check_opt_out(
    user_id: str, feature: str, manager: PrivacyManager = Depends(get_privacy_manager)
):
    """
    Check if user has opted out of a feature

    **Parameters:**
    - **user_id**: User ID
    - **feature**: Feature to check

    **Returns:**
    - Opt-out status
    """
    try:
        opted_out = await manager.is_opted_out(user_id, feature)
        return {"user_id": user_id, "feature": feature, "opted_out": opted_out}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to check opt-out status: {str(e)}"
        )


@router.get("/access-logs/{user_id}", response_model=List[DataAccessLogResponse])
async def get_access_logs(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    category: Optional[str] = Query(None, description="Data category filter"),
    manager: PrivacyManager = Depends(get_privacy_manager),
):
    """
    Get data access logs for a user

    **Parameters:**
    - **user_id**: User ID
    - **start_date**: Optional start date filter
    - **end_date**: Optional end date filter
    - **category**: Optional data category filter

    **Returns:**
    - List of data access logs
    """
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        cat = DataCategory(category) if category else None

        logs = await manager.get_access_logs(user_id, start, end, cat)

        return [DataAccessLogResponse(**log.to_dict()) for log in logs]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get access logs: {str(e)}"
        )


@router.post("/export/{user_id}", response_model=DataExportResponse)
async def request_data_export(
    user_id: str,
    request: DataExportRequestModel,
    manager: PrivacyManager = Depends(get_privacy_manager),
):
    """
    Request data export (GDPR right to data portability)

    **Parameters:**
    - **user_id**: User ID
    - **categories**: Data categories to export
    - **format**: Export format (json, csv, xml)

    **Returns:**
    - Data export request details
    """
    try:
        categories = [DataCategory(cat) for cat in request.categories]
        export_request = await manager.request_data_export(
            user_id, categories, request.format
        )

        return DataExportResponse(
            request_id=export_request.request_id,
            user_id=export_request.user_id,
            categories=[cat.value for cat in export_request.categories],
            format=export_request.format,
            status=export_request.status,
            requested_at=export_request.requested_at.isoformat(),
            completed_at=(
                export_request.completed_at.isoformat()
                if export_request.completed_at
                else None
            ),
            download_url=export_request.download_url,
            expires_at=(
                export_request.expires_at.isoformat()
                if export_request.expires_at
                else None
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to request data export: {str(e)}"
        )


@router.post("/delete/{user_id}", response_model=DataDeletionResponse)
async def request_data_deletion(
    user_id: str,
    request: DataDeletionRequestModel,
    manager: PrivacyManager = Depends(get_privacy_manager),
):
    """
    Request data deletion (GDPR right to erasure)

    **Parameters:**
    - **user_id**: User ID
    - **categories**: Data categories to delete
    - **reason**: Reason for deletion
    - **verification_required**: Require verification before deletion

    **Returns:**
    - Data deletion request details
    """
    try:
        categories = [DataCategory(cat) for cat in request.categories]
        deletion_request = await manager.request_data_deletion(
            user_id, categories, request.reason, request.verification_required
        )

        return DataDeletionResponse(
            request_id=deletion_request.request_id,
            user_id=deletion_request.user_id,
            categories=[cat.value for cat in deletion_request.categories],
            reason=deletion_request.reason,
            status=deletion_request.status,
            requested_at=deletion_request.requested_at.isoformat(),
            completed_at=(
                deletion_request.completed_at.isoformat()
                if deletion_request.completed_at
                else None
            ),
            verification_required=deletion_request.verification_required,
            verified=deletion_request.verified,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to request data deletion: {str(e)}"
        )


@router.post("/anonymize/{user_id}")
async def anonymize_data(
    user_id: str,
    categories: List[str] = Query(..., description="Data categories to anonymize"),
    manager: PrivacyManager = Depends(get_privacy_manager),
):
    """
    Anonymize user data

    **Parameters:**
    - **user_id**: User ID
    - **categories**: Data categories to anonymize

    **Returns:**
    - Success message
    """
    try:
        cats = [DataCategory(cat) for cat in categories]
        await manager.anonymize_user_data(user_id, cats)
        return {"message": f"Data anonymized for user {user_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to anonymize data: {str(e)}"
        )


# Health check endpoint
@router.get("/health")
async def health_check(manager: PrivacyManager = Depends(get_privacy_manager)):
    """
    Check privacy service health

    **Returns:**
    - Service status and statistics
    """
    try:
        return {
            "status": "healthy",
            "total_users": len(manager.settings),
            "total_access_logs": len(manager.access_logs),
            "export_requests": len(manager.export_requests),
            "deletion_requests": len(manager.deletion_requests),
            "supported_privacy_levels": [level.value for level in PrivacyLevel],
            "supported_data_categories": [cat.value for cat in DataCategory],
            "supported_consent_types": [consent.value for consent in ConsentType],
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
