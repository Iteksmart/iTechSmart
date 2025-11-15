"""
Payment and subscription endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole, SubscriptionStatus
from app.core.config import settings
from app.core.exceptions import PaymentError

router = APIRouter()


# Schemas
class SubscriptionPlan(BaseModel):
    plan_id: str
    name: str
    price: float
    interval: str
    features: list


class CheckoutSession(BaseModel):
    session_id: str
    checkout_url: str


class SubscriptionResponse(BaseModel):
    status: str
    plan: str
    expires_at: Optional[datetime]


# Endpoints
@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    
    return {
        "plans": [
            {
                "plan_id": "free",
                "name": "Free",
                "price": 0,
                "interval": "forever",
                "features": [
                    "10 proofs per month",
                    "10MB file size limit",
                    "Basic verification",
                    "Public proofs only"
                ]
            },
            {
                "plan_id": "monthly",
                "name": "Premium Monthly",
                "price": 1.00,
                "interval": "month",
                "stripe_price_id": settings.STRIPE_MONTHLY_PRICE_ID,
                "features": [
                    "Unlimited proofs",
                    "100MB file size limit",
                    "AI verification",
                    "Private proofs",
                    "API access",
                    "Batch processing",
                    "Custom branding"
                ]
            },
            {
                "plan_id": "yearly",
                "name": "Premium Yearly",
                "price": 10.00,
                "interval": "year",
                "stripe_price_id": settings.STRIPE_YEARLY_PRICE_ID,
                "features": [
                    "Unlimited proofs",
                    "100MB file size limit",
                    "AI verification",
                    "Private proofs",
                    "API access",
                    "Batch processing",
                    "Custom branding",
                    "Priority support",
                    "Save $2/year"
                ]
            },
            {
                "plan_id": "lifetime",
                "name": "Lifetime",
                "price": 5.00,
                "interval": "lifetime",
                "stripe_price_id": settings.STRIPE_LIFETIME_PRICE_ID,
                "features": [
                    "All Premium features",
                    "Lifetime access",
                    "One-time payment",
                    "Best value!"
                ]
            }
        ]
    }


@router.post("/checkout", response_model=CheckoutSession)
async def create_checkout_session(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create Stripe checkout session"""
    
    # In production, integrate with Stripe
    # For now, return mock data
    
    if not settings.STRIPE_SECRET_KEY:
        raise PaymentError("Payment system not configured")
    
    # Map plan_id to Stripe price ID
    price_id_map = {
        "monthly": settings.STRIPE_MONTHLY_PRICE_ID,
        "yearly": settings.STRIPE_YEARLY_PRICE_ID,
        "lifetime": settings.STRIPE_LIFETIME_PRICE_ID
    }
    
    price_id = price_id_map.get(plan_id)
    if not price_id:
        raise PaymentError("Invalid plan")
    
    # TODO: Create actual Stripe checkout session
    # import stripe
    # stripe.api_key = settings.STRIPE_SECRET_KEY
    # session = stripe.checkout.Session.create(...)
    
    return CheckoutSession(
        session_id="mock_session_id",
        checkout_url=f"https://checkout.stripe.com/mock?plan={plan_id}"
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Stripe webhooks"""
    
    # TODO: Implement Stripe webhook handling
    # Verify webhook signature
    # Handle events: checkout.session.completed, subscription.updated, etc.
    
    return {"status": "success"}


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user)
):
    """Get current subscription status"""
    
    return SubscriptionResponse(
        status=current_user.subscription_status.value,
        plan=current_user.role.value,
        expires_at=current_user.subscription_expires_at
    )


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel subscription"""
    
    if current_user.role == UserRole.FREE:
        raise PaymentError("No active subscription")
    
    # TODO: Cancel Stripe subscription
    
    current_user.subscription_status = SubscriptionStatus.CANCELLED
    await db.commit()
    
    return {"message": "Subscription cancelled successfully"}


@router.get("/billing-portal")
async def get_billing_portal(
    current_user: User = Depends(get_current_user)
):
    """Get Stripe billing portal URL"""
    
    # TODO: Create Stripe billing portal session
    
    return {
        "portal_url": "https://billing.stripe.com/mock"
    }