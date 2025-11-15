"""
iTechSmart Enterprise - Authentication API Endpoints
REST API for unified authentication across iTechSmart Suite
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr

from app.core.unified_auth import UnifiedAuthSystem, UserRole, PermissionScope
from app.core.database import get_db

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class APIKeyRequest(BaseModel):
    name: str
    scopes: List[str]
    expires_in_days: Optional[int] = None

class ServiceTokenRequest(BaseModel):
    service_id: int
    scopes: List[str]


# Initialize auth system (in production, use dependency injection)
def get_auth_system(db: Session = Depends(get_db)) -> UnifiedAuthSystem:
    """Get unified auth system instance"""
    # In production, get secret from environment
    secret_key = "your-secret-key-here-change-in-production"
    return UnifiedAuthSystem(db, secret_key)


@router.post("/login")
async def login(
    request: LoginRequest,
    auth: UnifiedAuthSystem = Depends(get_auth_system)
) -> Dict[str, Any]:
    """
    Authenticate user and receive access tokens
    
    Args:
        username: User's username or email
        password: User's password
    
    Returns:
        - access_token: JWT access token
        - refresh_token: JWT refresh token
        - user: User information
        - expires_in: Token expiration time in seconds
    """
    result = await auth.authenticate_user(request.username, request.password)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result


@router.post("/refresh")
async def refresh_token(
    request: TokenRefreshRequest,
    auth: UnifiedAuthSystem = Depends(get_auth_system)
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token
    
    Args:
        refresh_token: JWT refresh token
    
    Returns:
        - access_token: New JWT access token
        - expires_in: Token expiration time in seconds
    """
    result = await auth.refresh_access_token(request.refresh_token)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result


@router.get("/validate")
async def validate_token(
    authorization: str = Header(...),
    auth: UnifiedAuthSystem = Depends(get_auth_system)
) -> Dict[str, Any]:
    """
    Validate access token
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        - valid: Boolean indicating if token is valid
        - user: User information (if valid)
    """
    # Extract token from Authorization header
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    result = await auth.validate_token(token)
    
    if not result["valid"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result


@router.post("/api-keys")
async def create_api_key(
    request: APIKeyRequest,
    authorization: str = Header(...),
    auth: UnifiedAuthSystem = Depends(get_auth_system)
) -> Dict[str, Any]:
    """
    Create API key for programmatic access
    
    Headers:
        Authorization: Bearer <token>
    
    Args:
        name: API key name/description
        scopes: List of permission scopes
        expires_in_days: Optional expiration in days
    
    Returns:
        - api_key: Generated API key
        - name: API key name
        - scopes: Permission scopes
        - created_at: Creation timestamp
        - expires_at: Expiration timestamp (if applicable)
    """
    # Validate user token
    token = authorization.replace("Bearer ", "")
    validation = await auth.validate_token(token)
    
    if not validation["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = validation["user"]["id"]
    
    # Convert scope strings to PermissionScope enums
    try:
        scopes = [PermissionScope(s) for s in request.scopes]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid scope: {str(e)}")
    
    # Create API key
    result = await auth.create_api_key(
        user_id,
        request.name,
        scopes,
        request.expires_in_days
    )
    
    return result


@router.post("/service-tokens")
async def generate_service_token(
    request: ServiceTokenRequest,
    authorization: str = Header(...),
    auth: UnifiedAuthSystem = Depends(get_auth_system)
) -> Dict[str, str]:
    """
    Generate service-to-service authentication token
    
    Headers:
        Authorization: Bearer <token>
    
    Args:
        service_id: Service ID
        scopes: List of permission scopes
    
    Returns:
        - service_token: Generated service token
    """
    # Validate user token
    token = authorization.replace("Bearer ", "")
    validation = await auth.validate_token(token)
    
    if not validation["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if user has admin permissions
    if PermissionScope.ADMIN not in validation["user"]["permissions"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Convert scope strings to PermissionScope enums
    try:
        scopes = [PermissionScope(s) for s in request.scopes]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid scope: {str(e)}")
    
    # Generate service token
    service_token = await auth.generate_service_token(request.service_id, scopes)
    
    return {
        "service_token": service_token
    }


@router.post("/authorize")
async def authorize_action(
    service_id: int,
    action: str,
    authorization: str = Header(...),
    auth: UnifiedAuthSystem = Depends(get_auth_system)
) -> Dict[str, bool]:
    """
    Check if user is authorized to perform action on service
    
    Headers:
        Authorization: Bearer <token>
    
    Args:
        service_id: Service ID
        action: Required permission scope
    
    Returns:
        - authorized: Boolean indicating if action is authorized
    """
    # Validate user token
    token = authorization.replace("Bearer ", "")
    validation = await auth.validate_token(token)
    
    if not validation["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = validation["user"]["id"]
    
    # Convert action string to PermissionScope enum
    try:
        action_scope = PermissionScope(action)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
    
    # Check authorization
    authorized = await auth.authorize_action(user_id, service_id, action_scope)
    
    return {
        "authorized": authorized
    }


@router.get("/me")
async def get_current_user(
    authorization: str = Header(...),
    auth: UnifiedAuthSystem = Depends(get_auth_system)
) -> Dict[str, Any]:
    """
    Get current authenticated user information
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        User information including:
        - id: User ID
        - username: Username
        - email: Email address
        - role: User role
        - permissions: List of permissions
    """
    # Validate user token
    token = authorization.replace("Bearer ", "")
    validation = await auth.validate_token(token)
    
    if not validation["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return validation["user"]


@router.post("/logout")
async def logout(
    authorization: str = Header(...),
    auth: UnifiedAuthSystem = Depends(get_auth_system)
) -> Dict[str, str]:
    """
    Logout user (invalidate token)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        Success message
    """
    # In production, add token to blacklist
    # For now, just return success
    
    return {
        "status": "success",
        "message": "Logged out successfully"
    }


@router.get("/roles")
async def get_available_roles() -> Dict[str, List[str]]:
    """
    Get list of available user roles
    
    Returns:
        List of role names and their permissions
    """
    return {
        "roles": [role.value for role in UserRole],
        "permissions": [scope.value for scope in PermissionScope]
    }