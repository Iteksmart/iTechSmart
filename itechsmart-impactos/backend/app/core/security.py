"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Data to encode in the token
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> None:
    """
    Verify the token type matches expected type
    
    Args:
        payload: Decoded token payload
        expected_type: Expected token type (access or refresh)
        
    Raises:
        HTTPException: If token type doesn't match
    """
    token_type = payload.get("type")
    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {expected_type}, got {token_type}",
            headers={"WWW-Authenticate": "Bearer"},
        )


class PasswordValidator:
    """Password strength validator"""
    
    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @classmethod
    def validate(cls, password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters long"
        
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if cls.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARS for c in password):
            return False, f"Password must contain at least one special character ({cls.SPECIAL_CHARS})"
        
        return True, None


class RolePermissions:
    """Role-based access control permissions"""
    
    # Define roles
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    PROGRAM_MANAGER = "program_manager"
    GRANT_WRITER = "grant_writer"
    DATA_ANALYST = "data_analyst"
    VOLUNTEER = "volunteer"
    DONOR = "donor"
    
    # Define permissions
    PERMISSIONS = {
        SUPER_ADMIN: [
            "manage_all_organizations",
            "manage_all_users",
            "manage_system_settings",
            "view_all_data",
            "manage_billing",
            "manage_api_keys",
        ],
        ORG_ADMIN: [
            "manage_organization",
            "manage_org_users",
            "manage_programs",
            "manage_grants",
            "view_org_analytics",
            "manage_partners",
            "export_data",
        ],
        PROGRAM_MANAGER: [
            "manage_programs",
            "create_impact_reports",
            "manage_evidence",
            "view_program_analytics",
            "manage_volunteers",
        ],
        GRANT_WRITER: [
            "create_grant_proposals",
            "edit_grant_proposals",
            "submit_grants",
            "view_grant_analytics",
            "access_grant_assistant",
        ],
        DATA_ANALYST: [
            "view_all_analytics",
            "create_custom_reports",
            "export_data",
            "manage_dashboards",
        ],
        VOLUNTEER: [
            "view_programs",
            "submit_evidence",
            "view_impact_reports",
        ],
        DONOR: [
            "view_impact_reports",
            "view_public_analytics",
            "manage_donations",
        ],
    }
    
    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """
        Check if a role has a specific permission
        
        Args:
            role: User role
            permission: Permission to check
            
        Returns:
            True if role has permission, False otherwise
        """
        return permission in cls.PERMISSIONS.get(role, [])
    
    @classmethod
    def get_permissions(cls, role: str) -> list[str]:
        """
        Get all permissions for a role
        
        Args:
            role: User role
            
        Returns:
            List of permissions
        """
        return cls.PERMISSIONS.get(role, [])