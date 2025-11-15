"""
Admin API Routes
Administrative functions for user management, system settings, and monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.database import User, Task, APIKey, AuditLog, UserSettings
from app.api.auth import get_current_user, require_admin
from app.core.security import get_password_hash, encryption_manager
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "user"

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    points: int
    level: int
    created_at: str
    last_login: Optional[str]
    
    class Config:
        from_attributes = True

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    running_tasks: int
    total_api_keys: int
    active_api_keys: int

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    details: dict
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True

class AIProviderSettings(BaseModel):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    default_provider: str = "openai"
    default_model: str = "gpt-4"

# User Management
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            points=user.points,
            level=user.level,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        for user in users
    ]

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    valid_roles = ["user", "admin", "premium"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Create user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create audit log
    audit_log = AuditLog(
        user_id=admin_user.id,
        action="user_created",
        details={"created_user_email": new_user.email, "role": new_user.role}
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"User created by admin: {new_user.email}")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        is_active=new_user.is_active,
        points=new_user.points,
        level=new_user.level,
        created_at=new_user.created_at.isoformat(),
        last_login=None
    )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get user details (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        points=user.points,
        level=user.level,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.email is not None:
        # Check if email already exists
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = user_data.email
    
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    if user_data.role is not None:
        valid_roles = ["user", "admin", "premium"]
        if user_data.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        user.role = user_data.role
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    # Create audit log
    audit_log = AuditLog(
        user_id=admin_user.id,
        action="user_updated",
        details={"updated_user_id": user_id, "changes": user_data.dict(exclude_unset=True)}
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"User updated by admin: {user.email}")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        points=user.points,
        level=user.level,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting yourself
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Create audit log before deletion
    audit_log = AuditLog(
        user_id=admin_user.id,
        action="user_deleted",
        details={"deleted_user_email": user.email}
    )
    db.add(audit_log)
    
    # Delete user (cascade will handle related records)
    db.delete(user)
    db.commit()
    
    logger.info(f"User deleted by admin: {user.email}")
    
    return None

# System Statistics
@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "completed").count()
    failed_tasks = db.query(Task).filter(Task.status == "failed").count()
    running_tasks = db.query(Task).filter(Task.status == "running").count()
    
    total_api_keys = db.query(APIKey).count()
    active_api_keys = db.query(APIKey).filter(APIKey.is_active == True).count()
    
    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        running_tasks=running_tasks,
        total_api_keys=total_api_keys,
        active_api_keys=active_api_keys
    )

# Audit Logs
@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin only)"""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            details=log.details,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at.isoformat()
        )
        for log in logs
    ]

# AI Provider Settings
@router.get("/settings/ai-providers")
async def get_ai_provider_settings(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get AI provider settings (admin only)"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == admin_user.id).first()
    
    if not settings:
        return {
            "openai_api_key": None,
            "anthropic_api_key": None,
            "google_api_key": None,
            "deepseek_api_key": None,
            "default_provider": "openai",
            "default_model": "gpt-4"
        }
    
    # Decrypt API keys
    ai_settings = settings.ai_settings or {}
    
    return {
        "openai_api_key": "***" if ai_settings.get("openai_api_key") else None,
        "anthropic_api_key": "***" if ai_settings.get("anthropic_api_key") else None,
        "google_api_key": "***" if ai_settings.get("google_api_key") else None,
        "deepseek_api_key": "***" if ai_settings.get("deepseek_api_key") else None,
        "default_provider": ai_settings.get("default_provider", "openai"),
        "default_model": ai_settings.get("default_model", "gpt-4")
    }

@router.post("/settings/ai-providers")
async def update_ai_provider_settings(
    settings_data: AIProviderSettings,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update AI provider settings (admin only)"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == admin_user.id).first()
    
    if not settings:
        settings = UserSettings(user_id=admin_user.id)
        db.add(settings)
    
    # Get existing settings
    ai_settings = settings.ai_settings or {}
    
    # Update API keys (only if provided)
    if settings_data.openai_api_key:
        ai_settings["openai_api_key"] = encryption_manager.encrypt(settings_data.openai_api_key)
    
    if settings_data.anthropic_api_key:
        ai_settings["anthropic_api_key"] = encryption_manager.encrypt(settings_data.anthropic_api_key)
    
    if settings_data.google_api_key:
        ai_settings["google_api_key"] = encryption_manager.encrypt(settings_data.google_api_key)
    
    if settings_data.deepseek_api_key:
        ai_settings["deepseek_api_key"] = encryption_manager.encrypt(settings_data.deepseek_api_key)
    
    # Update default provider and model
    ai_settings["default_provider"] = settings_data.default_provider
    ai_settings["default_model"] = settings_data.default_model
    
    settings.ai_settings = ai_settings
    db.commit()
    
    # Create audit log
    audit_log = AuditLog(
        user_id=admin_user.id,
        action="ai_settings_updated",
        details={"provider": settings_data.default_provider, "model": settings_data.default_model}
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"AI provider settings updated by admin: {admin_user.email}")
    
    return {"message": "AI provider settings updated successfully"}