"""
MCP (Model Context Protocol) server endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.core.database import get_db
from app.api.deps import get_current_user, verify_api_key
from app.models.user import User
from app.core.exceptions import MCPError

router = APIRouter()


# Schemas
class MCPRequest(BaseModel):
    function: str
    params: Dict[str, Any]


class MCPResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


class MCPToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


# MCP Functions
async def mcp_create_proof(
    params: Dict[str, Any], user: User, db: AsyncSession
) -> Dict[str, Any]:
    """MCP function: create_proof"""

    from app.models.proof import Proof, ProofType, ProofStatus, VerificationMethod
    from app.core.security import hash_file, generate_proof_link
    from datetime import datetime

    # Extract parameters
    file_hash = params.get("file_hash")
    user_id = params.get("user_id", user.id)
    timestamp = params.get("timestamp", datetime.utcnow().isoformat())
    signature = params.get("signature")

    if not file_hash:
        raise MCPError("file_hash is required")

    # Generate proof link
    proof_link = generate_proof_link()

    # Create proof
    proof = Proof(
        user_id=user_id,
        proof_link=proof_link,
        proof_type=ProofType.FILE,
        status=ProofStatus.VERIFIED,
        file_hash=file_hash,
        hash_algorithm="SHA256",
        signature=signature,
        timestamp=(
            datetime.fromisoformat(timestamp)
            if isinstance(timestamp, str)
            else timestamp
        ),
        verification_method=VerificationMethod.HASH,
    )

    db.add(proof)
    await db.commit()
    await db.refresh(proof)

    return {
        "proof_id": proof.id,
        "proof_link": proof.proof_link,
        "verification_url": f"https://prooflink.ai/verify/{proof.proof_link}",
    }


async def mcp_verify_proof(
    params: Dict[str, Any], user: User, db: AsyncSession
) -> Dict[str, Any]:
    """MCP function: verify_proof"""

    from app.models.proof import Proof
    from sqlalchemy import select

    proof_link = params.get("proof_link")

    if not proof_link:
        raise MCPError("proof_link is required")

    result = await db.execute(select(Proof).where(Proof.proof_link == proof_link))
    proof = result.scalar_one_or_none()

    if not proof:
        return {"verified": False, "error": "Proof not found"}

    return {
        "verified": True,
        "proof_id": proof.id,
        "file_hash": proof.file_hash,
        "timestamp": proof.timestamp.isoformat(),
        "status": proof.status.value,
    }


async def mcp_get_user_proofs(
    params: Dict[str, Any], user: User, db: AsyncSession
) -> Dict[str, Any]:
    """MCP function: get_user_proofs"""

    from app.models.proof import Proof
    from sqlalchemy import select

    limit = params.get("limit", 10)

    result = await db.execute(
        select(Proof)
        .where(Proof.user_id == user.id)
        .order_by(Proof.created_at.desc())
        .limit(limit)
    )
    proofs = result.scalars().all()

    return {
        "proofs": [
            {
                "id": proof.id,
                "proof_link": proof.proof_link,
                "file_name": proof.file_name,
                "file_hash": proof.file_hash,
                "timestamp": proof.timestamp.isoformat(),
            }
            for proof in proofs
        ]
    }


# MCP Function Registry
MCP_FUNCTIONS = {
    "create_proof": mcp_create_proof,
    "verify_proof": mcp_verify_proof,
    "get_user_proofs": mcp_get_user_proofs,
}


# Endpoints
@router.get("/tools")
async def get_mcp_tools():
    """Get available MCP tools"""

    return {
        "tools": [
            {
                "name": "create_proof",
                "description": "Create a new proof for a file or content",
                "parameters": {
                    "file_hash": {
                        "type": "string",
                        "required": True,
                        "description": "SHA-256 hash of the file",
                    },
                    "user_id": {
                        "type": "string",
                        "required": False,
                        "description": "User ID (defaults to current user)",
                    },
                    "timestamp": {
                        "type": "string",
                        "required": False,
                        "description": "ISO-8601 timestamp",
                    },
                    "signature": {
                        "type": "string",
                        "required": False,
                        "description": "Optional PGP signature",
                    },
                },
            },
            {
                "name": "verify_proof",
                "description": "Verify a proof by its link",
                "parameters": {
                    "proof_link": {
                        "type": "string",
                        "required": True,
                        "description": "Proof link to verify",
                    }
                },
            },
            {
                "name": "get_user_proofs",
                "description": "Get user's proofs",
                "parameters": {
                    "limit": {
                        "type": "integer",
                        "required": False,
                        "description": "Number of proofs to return (default: 10)",
                    }
                },
            },
        ]
    }


@router.post("/execute", response_model=MCPResponse)
async def execute_mcp_function(
    request: MCPRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute an MCP function"""

    function_name = request.function
    params = request.params

    # Get function
    function = MCP_FUNCTIONS.get(function_name)

    if not function:
        raise MCPError(f"Unknown function: {function_name}")

    try:
        # Execute function
        result = await function(params, current_user, db)

        return MCPResponse(success=True, result=result)

    except Exception as e:
        return MCPResponse(success=False, error=str(e))


@router.get("/resources")
async def get_mcp_resources():
    """Get available MCP resources"""

    return {
        "resources": [
            {
                "name": "user_profile",
                "description": "Current user's profile information",
                "uri": "prooflink://user/profile",
            },
            {
                "name": "proof_templates",
                "description": "Available proof templates",
                "uri": "prooflink://templates",
            },
            {
                "name": "verification_guide",
                "description": "Guide for verifying proofs",
                "uri": "prooflink://guides/verification",
            },
        ]
    }


@router.get("/prompts")
async def get_mcp_prompts():
    """Get available MCP prompts"""

    return {
        "prompts": [
            {
                "name": "create_proof_prompt",
                "description": "Guide user through creating a proof",
                "template": "I'll help you create a proof. Please provide the file you want to verify.",
            },
            {
                "name": "verify_proof_prompt",
                "description": "Guide user through verifying a proof",
                "template": "I'll help you verify a proof. Please provide the proof link.",
            },
            {
                "name": "explain_verification",
                "description": "Explain how verification works",
                "template": "ProofLink uses cryptographic hashing to verify file authenticity. Here's how it works...",
            },
        ]
    }
