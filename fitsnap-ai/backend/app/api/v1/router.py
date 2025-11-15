"""
API V1 Router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, scans, users, chat, products

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(scans.router, prefix="/scans", tags=["Outfit Scans"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Stylist Chat"])
api_router.include_router(products.router, prefix="/products", tags=["Product Recommendations"])