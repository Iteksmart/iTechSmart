"""
iTechSmart Enterprise - Unified Authentication System
Single sign-on (SSO) and centralized authentication for all iTechSmart products
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
import jwt
import bcrypt
import secrets
from enum import Enum

from app.models.integration import IntegratedService


class UserRole(str, Enum):
    """User roles across iTechSmart Suite"""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    USER = "user"
    VIEWER = "viewer"


class PermissionScope(str, Enum):
    """Permission scopes for different operations"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"


class UnifiedAuthSystem:
    """Unified authentication and authorization system"""

    def __init__(self, db: Session, secret_key: str):
        self.db = db
        self.secret_key = secret_key
        self.token_expiry = timedelta(hours=24)
        self.refresh_token_expiry = timedelta(days=30)

        # Role-based permissions
        self.role_permissions = {
            UserRole.SUPER_ADMIN: [
                PermissionScope.READ,
                PermissionScope.WRITE,
                PermissionScope.DELETE,
                PermissionScope.ADMIN,
                PermissionScope.EXECUTE,
            ],
            UserRole.ADMIN: [
                PermissionScope.READ,
                PermissionScope.WRITE,
                PermissionScope.DELETE,
                PermissionScope.EXECUTE,
            ],
            UserRole.DEVELOPER: [
                PermissionScope.READ,
                PermissionScope.WRITE,
                PermissionScope.EXECUTE,
            ],
            UserRole.ANALYST: [PermissionScope.READ, PermissionScope.EXECUTE],
            UserRole.USER: [PermissionScope.READ, PermissionScope.WRITE],
            UserRole.VIEWER: [PermissionScope.READ],
        }

    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate tokens

        Args:
            username: User's username or email
            password: User's password

        Returns:
            Authentication result with tokens
        """

        # In production, this would query a user database
        # For now, we'll use a simplified approach

        user = await self._get_user(username)

        if not user:
            return {"success": False, "error": "Invalid credentials"}

        # Verify password
        if not self._verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Invalid credentials"}

        # Generate tokens
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)

        # Log authentication event
        await self._log_auth_event(user["id"], "login", "success")

        return {
            "success": True,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "permissions": self.role_permissions[user["role"]],
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": int(self.token_expiry.total_seconds()),
        }

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate access token

        Args:
            token: JWT access token

        Returns:
            Validation result with user info
        """

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            # Check expiration
            if datetime.utcnow().timestamp() > payload["exp"]:
                return {"valid": False, "error": "Token expired"}

            # Get user info
            user = await self._get_user_by_id(payload["user_id"])

            if not user:
                return {"valid": False, "error": "User not found"}

            return {
                "valid": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "permissions": self.role_permissions[user["role"]],
                },
            }

        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: JWT refresh token

        Returns:
            New access token
        """

        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=["HS256"])

            # Check if it's a refresh token
            if payload.get("type") != "refresh":
                return {"success": False, "error": "Invalid token type"}

            # Get user
            user = await self._get_user_by_id(payload["user_id"])

            if not user:
                return {"success": False, "error": "User not found"}

            # Generate new access token
            access_token = self._generate_access_token(user)

            return {
                "success": True,
                "access_token": access_token,
                "expires_in": int(self.token_expiry.total_seconds()),
            }

        except jwt.InvalidTokenError:
            return {"success": False, "error": "Invalid refresh token"}

    async def authorize_action(
        self, user_id: int, service_id: int, action: PermissionScope
    ) -> bool:
        """
        Check if user is authorized to perform action on service

        Args:
            user_id: User ID
            service_id: Service ID
            action: Required permission scope

        Returns:
            True if authorized, False otherwise
        """

        user = await self._get_user_by_id(user_id)

        if not user:
            return False

        # Check role permissions
        user_permissions = self.role_permissions[user["role"]]

        if action not in user_permissions:
            return False

        # Check service-specific permissions
        service_perms = await self._get_service_permissions(user_id, service_id)

        if service_perms and action not in service_perms:
            return False

        return True

    async def generate_service_token(
        self, service_id: int, scopes: List[PermissionScope]
    ) -> str:
        """
        Generate service-to-service authentication token

        Args:
            service_id: Service ID
            scopes: List of permission scopes

        Returns:
            Service token
        """

        service = (
            self.db.query(IntegratedService)
            .filter(IntegratedService.id == service_id)
            .first()
        )

        if not service:
            raise ValueError("Service not found")

        payload = {
            "type": "service",
            "service_id": service_id,
            "service_name": service.name,
            "scopes": [s.value for s in scopes],
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256")

        return token

    async def validate_service_token(
        self, token: str, required_scope: PermissionScope
    ) -> Dict[str, Any]:
        """
        Validate service-to-service token

        Args:
            token: Service token
            required_scope: Required permission scope

        Returns:
            Validation result
        """

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            if payload.get("type") != "service":
                return {"valid": False, "error": "Invalid token type"}

            if required_scope.value not in payload.get("scopes", []):
                return {"valid": False, "error": "Insufficient permissions"}

            return {
                "valid": True,
                "service_id": payload["service_id"],
                "service_name": payload["service_name"],
                "scopes": payload["scopes"],
            }

        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}

    async def create_api_key(
        self,
        user_id: int,
        name: str,
        scopes: List[PermissionScope],
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create API key for programmatic access

        Args:
            user_id: User ID
            name: API key name/description
            scopes: List of permission scopes
            expires_in_days: Optional expiration in days

        Returns:
            API key details
        """

        user = await self._get_user_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        # Generate API key
        api_key = f"itk_{secrets.token_urlsafe(32)}"

        # Create payload
        payload = {
            "type": "api_key",
            "user_id": user_id,
            "name": name,
            "scopes": [s.value for s in scopes],
            "iat": datetime.utcnow().timestamp(),
        }

        if expires_in_days:
            payload["exp"] = (
                datetime.utcnow() + timedelta(days=expires_in_days)
            ).timestamp()

        # Store API key (in production, store hash only)
        # For now, we'll return the key directly

        return {
            "api_key": api_key,
            "name": name,
            "scopes": [s.value for s in scopes],
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (
                (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()
                if expires_in_days
                else None
            ),
        }

    # Helper methods

    def _generate_access_token(self, user: Dict[str, Any]) -> str:
        """Generate JWT access token"""

        payload = {
            "type": "access",
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + self.token_expiry).timestamp(),
        }

        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def _generate_refresh_token(self, user: Dict[str, Any]) -> str:
        """Generate JWT refresh token"""

        payload = {
            "type": "refresh",
            "user_id": user["id"],
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + self.refresh_token_expiry).timestamp(),
        }

        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    async def _get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username (mock implementation)"""
        # In production, query from database
        # This is a mock for demonstration
        return {
            "id": 1,
            "username": username,
            "email": f"{username}@itechsmart.dev",
            "role": UserRole.ADMIN,
            "password_hash": bcrypt.hashpw(
                "password".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
        }

    async def _get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID (mock implementation)"""
        # In production, query from database
        return {
            "id": user_id,
            "username": "admin",
            "email": "admin@itechsmart.dev",
            "role": UserRole.ADMIN,
        }

    async def _get_service_permissions(
        self, user_id: int, service_id: int
    ) -> Optional[List[PermissionScope]]:
        """Get user's permissions for specific service"""
        # In production, query from database
        return None

    async def _log_auth_event(self, user_id: int, event_type: str, status: str):
        """Log authentication event"""
        # In production, store in database
        print(f"Auth event: user={user_id}, type={event_type}, status={status}")
