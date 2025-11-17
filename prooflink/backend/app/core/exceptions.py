"""
Custom exceptions for ProofLink.AI
"""

from typing import Optional, Dict, Any
from fastapi import status


class ProofLinkException(Exception):
    """Base exception for ProofLink"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(ProofLinkException):
    """Authentication failed"""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(ProofLinkException):
    """User not authorized"""

    def __init__(
        self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class NotFoundError(ProofLinkException):
    """Resource not found"""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details,
        )


class ValidationError(ProofLinkException):
    """Validation error"""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class RateLimitError(ProofLinkException):
    """Rate limit exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


class FileUploadError(ProofLinkException):
    """File upload error"""

    def __init__(
        self,
        message: str = "File upload failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_UPLOAD_ERROR",
            details=details,
        )


class ProofCreationError(ProofLinkException):
    """Proof creation error"""

    def __init__(
        self,
        message: str = "Proof creation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="PROOF_CREATION_ERROR",
            details=details,
        )


class ProofVerificationError(ProofLinkException):
    """Proof verification error"""

    def __init__(
        self,
        message: str = "Proof verification failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="PROOF_VERIFICATION_ERROR",
            details=details,
        )


class PaymentError(ProofLinkException):
    """Payment processing error"""

    def __init__(
        self,
        message: str = "Payment processing failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code="PAYMENT_ERROR",
            details=details,
        )


class SubscriptionError(ProofLinkException):
    """Subscription error"""

    def __init__(
        self,
        message: str = "Subscription error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code="SUBSCRIPTION_ERROR",
            details=details,
        )


class IntegrationError(ProofLinkException):
    """Third-party integration error"""

    def __init__(
        self,
        message: str = "Integration error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="INTEGRATION_ERROR",
            details=details,
        )


class AIVerificationError(ProofLinkException):
    """AI verification error"""

    def __init__(
        self,
        message: str = "AI verification failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="AI_VERIFICATION_ERROR",
            details=details,
        )


class MCPError(ProofLinkException):
    """MCP server error"""

    def __init__(
        self,
        message: str = "MCP operation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="MCP_ERROR",
            details=details,
        )
