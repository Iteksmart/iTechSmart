"""
API dependencies for authentication and authorization
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token, verify_token_type, RolePermissions
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import TokenPayload


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    try:
        payload = decode_token(token)
        verify_token_type(payload, "access")

        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user

    Args:
        current_user: Current user from token

    Returns:
        Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current superuser

    Args:
        current_user: Current user from token

    Returns:
        Current superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


def require_permission(permission: str):
    """
    Dependency factory to require specific permission

    Args:
        permission: Required permission

    Returns:
        Dependency function
    """

    async def permission_checker(
        current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
    ) -> User:
        """Check if user has required permission"""

        # Superusers have all permissions
        if current_user.is_superuser:
            return current_user

        # Get user's roles in all organizations
        from app.models.user import UserOrganization

        user_orgs = (
            db.query(UserOrganization)
            .filter(
                UserOrganization.user_id == current_user.id,
                UserOrganization.is_active == True,
            )
            .all()
        )

        # Check if any role has the required permission
        has_permission = False
        for user_org in user_orgs:
            if RolePermissions.has_permission(user_org.role.value, permission):
                has_permission = True
                break

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {permission}",
            )

        return current_user

    return permission_checker


def require_role(role: UserRole):
    """
    Dependency factory to require specific role

    Args:
        role: Required role

    Returns:
        Dependency function
    """

    async def role_checker(
        current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
    ) -> User:
        """Check if user has required role"""

        # Superusers bypass role checks
        if current_user.is_superuser:
            return current_user

        # Get user's roles in all organizations
        from app.models.user import UserOrganization

        user_orgs = (
            db.query(UserOrganization)
            .filter(
                UserOrganization.user_id == current_user.id,
                UserOrganization.is_active == True,
            )
            .all()
        )

        # Check if user has the required role
        has_role = any(user_org.role == role for user_org in user_orgs)

        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role denied. Required role: {role.value}",
            )

        return current_user

    return role_checker


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise

    Args:
        credentials: HTTP authorization credentials (optional)
        db: Database session

    Returns:
        Current user or None
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
