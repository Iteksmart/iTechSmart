"""
Proof creation and verification endpoints
"""

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
    BackgroundTasks,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime, timedelta
import json

from app.core.database import get_db
from app.core.security import hash_file, generate_proof_link
from app.core.exceptions import ValidationError, ProofCreationError, NotFoundError
from app.api.deps import get_current_user, get_current_verified_user, verify_api_key
from app.models.user import User
from app.models.proof import (
    Proof,
    ProofType,
    ProofStatus,
    VerificationMethod,
    ProofVerification,
)

router = APIRouter()


# Schemas
class ProofCreate(BaseModel):
    proof_type: ProofType
    file_name: Optional[str] = None
    is_public: bool = True
    is_downloadable: bool = False
    metadata: Optional[dict] = None


class ProofResponse(BaseModel):
    id: str
    proof_link: str
    proof_type: ProofType
    status: ProofStatus
    file_name: Optional[str]
    file_hash: str
    timestamp: datetime
    verification_url: str
    qr_code_url: str

    class Config:
        from_attributes = True


class ProofVerifyRequest(BaseModel):
    proof_link: str
    file_hash: Optional[str] = None


class ProofVerifyResponse(BaseModel):
    verified: bool
    proof: dict
    confidence_score: Optional[float]
    tamper_detected: bool
    verification_details: dict


class ProofListResponse(BaseModel):
    proofs: List[ProofResponse]
    total: int
    page: int
    page_size: int


# Endpoints
@router.post(
    "/create", response_model=ProofResponse, status_code=status.HTTP_201_CREATED
)
async def create_proof(
    file: UploadFile = File(...),
    proof_type: ProofType = Form(ProofType.FILE),
    is_public: bool = Form(True),
    is_downloadable: bool = Form(False),
    metadata: Optional[str] = Form(None),
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new proof"""

    # Check user limits
    if current_user.role.value == "free":
        if current_user.proofs_created_this_month >= 10:
            raise ValidationError(
                "Free tier limit reached. Upgrade to create more proofs."
            )

    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)

    max_size = (
        10 * 1024 * 1024 if current_user.role.value == "free" else 100 * 1024 * 1024
    )
    if file_size > max_size:
        raise ValidationError(f"File size exceeds limit of {max_size // (1024*1024)}MB")

    # Hash the file
    file_hash = hash_file(file_content, algorithm="SHA256")

    # Generate proof link
    proof_link = generate_proof_link()

    # Parse metadata
    metadata_dict = json.loads(metadata) if metadata else {}

    # Create proof
    proof = Proof(
        user_id=current_user.id,
        proof_link=proof_link,
        proof_type=proof_type,
        status=ProofStatus.VERIFIED,
        file_name=file.filename,
        file_size=file_size,
        file_type=file.content_type,
        file_hash=file_hash,
        hash_algorithm="SHA256",
        timestamp=datetime.utcnow(),
        verification_method=VerificationMethod.HASH,
        is_public=is_public,
        is_downloadable=is_downloadable,
        metadata=json.dumps(metadata_dict),
    )

    db.add(proof)

    # Update user stats
    current_user.proofs_created_this_month += 1
    current_user.storage_used_mb += file_size // (1024 * 1024)

    await db.commit()
    await db.refresh(proof)

    # TODO: Upload file to S3
    # TODO: Generate QR code
    # TODO: Trigger AI verification (background task)

    return ProofResponse(
        id=proof.id,
        proof_link=proof.proof_link,
        proof_type=proof.proof_type,
        status=proof.status,
        file_name=proof.file_name,
        file_hash=proof.file_hash,
        timestamp=proof.timestamp,
        verification_url=f"https://prooflink.ai/verify/{proof.proof_link}",
        qr_code_url=f"https://prooflink.ai/qr/{proof.proof_link}",
    )


@router.post("/verify", response_model=ProofVerifyResponse)
async def verify_proof(
    verify_data: ProofVerifyRequest, db: AsyncSession = Depends(get_db)
):
    """Verify a proof"""

    # Get proof by link
    result = await db.execute(
        select(Proof).where(Proof.proof_link == verify_data.proof_link)
    )
    proof = result.scalar_one_or_none()

    if not proof:
        raise NotFoundError("Proof not found")

    # Check if proof is public
    if not proof.is_public:
        raise ValidationError("This proof is private")

    # Verify hash if provided
    hash_match = True
    if verify_data.file_hash:
        hash_match = verify_data.file_hash == proof.file_hash

    # Update verification count
    proof.verification_count += 1
    proof.last_verified_at = datetime.utcnow()

    # Create verification record
    verification = ProofVerification(
        proof_id=proof.id,
        verification_result=hash_match,
        verification_method="hash",
        verified_at=datetime.utcnow(),
    )

    db.add(verification)
    await db.commit()

    return ProofVerifyResponse(
        verified=hash_match and proof.status == ProofStatus.VERIFIED,
        proof={
            "id": proof.id,
            "proof_link": proof.proof_link,
            "file_name": proof.file_name,
            "file_hash": proof.file_hash,
            "timestamp": proof.timestamp.isoformat(),
            "created_by": proof.user_id,
            "verification_count": proof.verification_count,
        },
        confidence_score=proof.ai_confidence_score,
        tamper_detected=proof.ai_tamper_detected,
        verification_details={
            "hash_match": hash_match,
            "status": proof.status.value,
            "verification_method": proof.verification_method.value,
            "ai_verified": proof.ai_verified,
        },
    )


@router.get("/verify/{proof_link}", response_model=ProofVerifyResponse)
async def verify_proof_by_link(proof_link: str, db: AsyncSession = Depends(get_db)):
    """Verify a proof by link (public endpoint)"""

    result = await db.execute(select(Proof).where(Proof.proof_link == proof_link))
    proof = result.scalar_one_or_none()

    if not proof:
        raise NotFoundError("Proof not found")

    if not proof.is_public:
        raise ValidationError("This proof is private")

    # Update stats
    proof.verification_count += 1
    proof.view_count += 1
    proof.last_verified_at = datetime.utcnow()
    await db.commit()

    return ProofVerifyResponse(
        verified=proof.status == ProofStatus.VERIFIED,
        proof={
            "id": proof.id,
            "proof_link": proof.proof_link,
            "file_name": proof.file_name,
            "file_hash": proof.file_hash,
            "timestamp": proof.timestamp.isoformat(),
            "verification_count": proof.verification_count,
        },
        confidence_score=proof.ai_confidence_score,
        tamper_detected=proof.ai_tamper_detected,
        verification_details={
            "status": proof.status.value,
            "verification_method": proof.verification_method.value,
            "ai_verified": proof.ai_verified,
        },
    )


@router.get("/my-proofs", response_model=ProofListResponse)
async def get_my_proofs(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's proofs"""

    # Get total count
    count_result = await db.execute(
        select(func.count(Proof.id)).where(Proof.user_id == current_user.id)
    )
    total = count_result.scalar()

    # Get proofs
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Proof)
        .where(Proof.user_id == current_user.id)
        .order_by(Proof.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    proofs = result.scalars().all()

    return ProofListResponse(
        proofs=[
            ProofResponse(
                id=proof.id,
                proof_link=proof.proof_link,
                proof_type=proof.proof_type,
                status=proof.status,
                file_name=proof.file_name,
                file_hash=proof.file_hash,
                timestamp=proof.timestamp,
                verification_url=f"https://prooflink.ai/verify/{proof.proof_link}",
                qr_code_url=f"https://prooflink.ai/qr/{proof.proof_link}",
            )
            for proof in proofs
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{proof_id}", response_model=ProofResponse)
async def get_proof(
    proof_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get proof details"""

    result = await db.execute(
        select(Proof).where(
            and_(Proof.id == proof_id, Proof.user_id == current_user.id)
        )
    )
    proof = result.scalar_one_or_none()

    if not proof:
        raise NotFoundError("Proof not found")

    return ProofResponse(
        id=proof.id,
        proof_link=proof.proof_link,
        proof_type=proof.proof_type,
        status=proof.status,
        file_name=proof.file_name,
        file_hash=proof.file_hash,
        timestamp=proof.timestamp,
        verification_url=f"https://prooflink.ai/verify/{proof.proof_link}",
        qr_code_url=f"https://prooflink.ai/qr/{proof.proof_link}",
    )


@router.delete("/{proof_id}")
async def delete_proof(
    proof_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a proof"""

    result = await db.execute(
        select(Proof).where(
            and_(Proof.id == proof_id, Proof.user_id == current_user.id)
        )
    )
    proof = result.scalar_one_or_none()

    if not proof:
        raise NotFoundError("Proof not found")

    # TODO: Delete file from S3

    await db.delete(proof)
    await db.commit()

    return {"message": "Proof deleted successfully"}


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_batch_proofs(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple proofs at once"""

    if current_user.role.value == "free":
        raise ValidationError("Batch processing requires premium subscription")

    if len(files) > 100:
        raise ValidationError("Maximum 100 files per batch")

    created_proofs = []

    for file in files:
        file_content = await file.read()
        file_hash = hash_file(file_content, algorithm="SHA256")
        proof_link = generate_proof_link()

        proof = Proof(
            user_id=current_user.id,
            proof_link=proof_link,
            proof_type=ProofType.FILE,
            status=ProofStatus.VERIFIED,
            file_name=file.filename,
            file_size=len(file_content),
            file_type=file.content_type,
            file_hash=file_hash,
            hash_algorithm="SHA256",
            timestamp=datetime.utcnow(),
            verification_method=VerificationMethod.HASH,
        )

        db.add(proof)
        created_proofs.append(proof)

    await db.commit()

    return {
        "message": f"Created {len(created_proofs)} proofs successfully",
        "proofs": [
            {
                "id": proof.id,
                "proof_link": proof.proof_link,
                "file_name": proof.file_name,
                "verification_url": f"https://prooflink.ai/verify/{proof.proof_link}",
            }
            for proof in created_proofs
        ],
    }
