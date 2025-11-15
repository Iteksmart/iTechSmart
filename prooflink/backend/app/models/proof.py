"""
Proof models
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum as SQLEnum, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from app.core.database import Base


class ProofStatus(str, enum.Enum):
    """Proof status"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class ProofType(str, enum.Enum):
    """Proof type"""
    FILE = "file"
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    CODE = "code"
    OTHER = "other"


class VerificationMethod(str, enum.Enum):
    """Verification method"""
    HASH = "hash"
    SIGNATURE = "signature"
    AI = "ai"
    TIMESTAMP = "timestamp"
    COMBINED = "combined"


class Proof(Base):
    """Proof model"""
    __tablename__ = "proofs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Proof details
    proof_link = Column(String, unique=True, nullable=False, index=True)
    proof_type = Column(SQLEnum(ProofType), nullable=False)
    status = Column(SQLEnum(ProofStatus), default=ProofStatus.PENDING)
    
    # File information
    file_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    file_type = Column(String, nullable=True)
    file_url = Column(String, nullable=True)  # S3 URL
    
    # Hashing
    file_hash = Column(String, nullable=False, index=True)
    hash_algorithm = Column(String, default="SHA256")
    
    # Signature
    signature = Column(Text, nullable=True)
    signature_algorithm = Column(String, nullable=True)
    public_key = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=func.now())
    timestamp_authority = Column(String, nullable=True)
    
    # Metadata
    metadata = Column(Text, nullable=True)  # JSON
    device_info = Column(Text, nullable=True)  # JSON
    location = Column(String, nullable=True)
    
    # Verification
    verification_method = Column(SQLEnum(VerificationMethod), default=VerificationMethod.HASH)
    verification_count = Column(Integer, default=0)
    last_verified_at = Column(DateTime, nullable=True)
    
    # AI Verification
    ai_verified = Column(Boolean, default=False)
    ai_confidence_score = Column(Float, nullable=True)
    ai_tamper_detected = Column(Boolean, default=False)
    ai_analysis = Column(Text, nullable=True)  # JSON
    
    # Expiry
    expires_at = Column(DateTime, nullable=True)
    
    # Privacy
    is_public = Column(Boolean, default=True)
    is_downloadable = Column(Boolean, default=False)
    
    # Tracking
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="proofs")
    verifications = relationship("ProofVerification", back_populates="proof", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Proof {self.proof_link}>"


class ProofVerification(Base):
    """Proof verification history"""
    __tablename__ = "proof_verifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    proof_id = Column(String, ForeignKey("proofs.id", ondelete="CASCADE"), nullable=False)
    
    # Verification details
    verified_by = Column(String, nullable=True)  # User ID or IP
    verification_result = Column(Boolean, nullable=False)
    verification_method = Column(String, nullable=False)
    
    # Details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    # Metadata
    metadata = Column(Text, nullable=True)  # JSON
    
    verified_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    proof = relationship("Proof", back_populates="verifications")
    
    def __repr__(self):
        return f"<ProofVerification {self.id}>"


class ProofTemplate(Base):
    """Proof template for organizations"""
    __tablename__ = "proof_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Template configuration
    template_config = Column(Text, nullable=False)  # JSON
    
    # Branding
    logo_url = Column(String, nullable=True)
    brand_color = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProofTemplate {self.name}>"