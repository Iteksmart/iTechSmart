"""
API v1 router
"""

from fastapi import APIRouter

from app.api.v1 import auth, users, proofs, payments, integrations, mcp, ai

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(proofs.router, prefix="/proofs", tags=["proofs"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])