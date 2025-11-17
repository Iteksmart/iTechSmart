"""
iTechSmart Vault - Main FastAPI Application
Secrets Management Platform
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from database import get_db, init_db
from models import (
    User,
    Vault,
    Secret,
    SecretVersion,
    Policy,
    AccessGrant,
    AuditLog,
    SecretRotation,
    SecretShare,
    APIKey,
    EncryptionKey,
    SecretStatus,
    AuditAction,
)
from schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    VaultCreate,
    VaultUpdate,
    VaultResponse,
    SecretCreate,
    SecretUpdate,
    SecretResponse,
    SecretWithValue,
    SecretListResponse,
    SecretVersionResponse,
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    AccessGrantCreate,
    AccessGrantUpdate,
    AccessGrantResponse,
    AuditLogResponse,
    SecretRotationRequest,
    SecretRotationResponse,
    SecretShareCreate,
    SecretShareResponse,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyWithValue,
    VaultAnalytics,
    SecretAccessStats,
    Token,
    TokenData,
)
from crypto import crypto_service

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create FastAPI app
app = FastAPI(
    title="iTechSmart Vault",
    description="Enterprise Secrets Management Platform",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def log_audit(
    db: Session,
    user_id: Optional[int],
    action: AuditAction,
    resource_type: str,
    resource_id: Optional[int] = None,
    resource_name: Optional[str] = None,
    vault_id: Optional[int] = None,
    details: dict = None,
    success: bool = True,
    error_message: str = None,
    ip_address: str = None,
):
    """Log audit event"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        vault_id=vault_id,
        details=details,
        success=success,
        error_message=error_message,
        ip_address=ip_address,
    )
    db.add(audit_log)
    db.commit()


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "iTechSmart Vault"}


# Authentication endpoints
@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    "/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create default vault for user
    default_vault = Vault(
        name="Default Vault",
        description="Default vault for storing secrets",
        owner_id=db_user.id,
        is_default=True,
    )
    db.add(default_vault)
    db.commit()

    return db_user


@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# Vault endpoints
@app.get("/vaults", response_model=List[VaultResponse])
async def list_vaults(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List vaults"""
    vaults = (
        db.query(Vault)
        .filter(Vault.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return vaults


@app.post("/vaults", response_model=VaultResponse, status_code=status.HTTP_201_CREATED)
async def create_vault(
    vault: VaultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new vault"""
    db_vault = Vault(
        name=vault.name,
        description=vault.description,
        owner_id=current_user.id,
        is_default=vault.is_default,
        tags=vault.tags,
    )
    db.add(db_vault)
    db.commit()
    db.refresh(db_vault)

    log_audit(
        db, current_user.id, AuditAction.CREATE, "vault", db_vault.id, db_vault.name
    )

    return db_vault


@app.get("/vaults/{vault_id}", response_model=VaultResponse)
async def get_vault(
    vault_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get vault by ID"""
    vault = (
        db.query(Vault)
        .filter(Vault.id == vault_id, Vault.owner_id == current_user.id)
        .first()
    )

    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")

    return vault


@app.put("/vaults/{vault_id}", response_model=VaultResponse)
async def update_vault(
    vault_id: int,
    vault_update: VaultUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update vault"""
    vault = (
        db.query(Vault)
        .filter(Vault.id == vault_id, Vault.owner_id == current_user.id)
        .first()
    )

    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")

    update_data = vault_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vault, field, value)

    vault.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(vault)

    log_audit(db, current_user.id, AuditAction.UPDATE, "vault", vault.id, vault.name)

    return vault


@app.delete("/vaults/{vault_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vault(
    vault_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete vault"""
    vault = (
        db.query(Vault)
        .filter(Vault.id == vault_id, Vault.owner_id == current_user.id)
        .first()
    )

    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")

    if vault.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default vault")

    log_audit(db, current_user.id, AuditAction.DELETE, "vault", vault.id, vault.name)

    db.delete(vault)
    db.commit()
    return None


# Secret endpoints
@app.get("/secrets", response_model=List[SecretListResponse])
async def list_secrets(
    vault_id: Optional[int] = None,
    secret_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List secrets"""
    query = db.query(Secret).join(Vault).filter(Vault.owner_id == current_user.id)

    if vault_id:
        query = query.filter(Secret.vault_id == vault_id)
    if secret_type:
        query = query.filter(Secret.secret_type == secret_type)
    if status:
        query = query.filter(Secret.status == status)

    secrets = query.offset(skip).limit(limit).all()
    return secrets


@app.post(
    "/secrets", response_model=SecretResponse, status_code=status.HTTP_201_CREATED
)
async def create_secret(
    secret: SecretCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new secret"""
    # Verify vault exists and belongs to user
    vault = (
        db.query(Vault)
        .filter(Vault.id == secret.vault_id, Vault.owner_id == current_user.id)
        .first()
    )

    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")

    # Encrypt secret value
    encrypted_value = crypto_service.encrypt(secret.value)

    # Create secret
    db_secret = Secret(
        vault_id=secret.vault_id,
        name=secret.name,
        description=secret.description,
        secret_type=secret.secret_type,
        encrypted_value=encrypted_value,
        created_by_id=current_user.id,
        tags=secret.tags,
        expires_at=secret.expires_at,
        rotation_interval_days=secret.rotation_interval_days,
    )
    db.add(db_secret)
    db.commit()
    db.refresh(db_secret)

    # Create initial version
    version = SecretVersion(
        secret_id=db_secret.id,
        version_number=1,
        encrypted_value=encrypted_value,
        created_by_id=current_user.id,
        change_description="Initial version",
    )
    db.add(version)

    # Update vault secret count
    vault.secret_count += 1

    db.commit()

    log_audit(
        db,
        current_user.id,
        AuditAction.CREATE,
        "secret",
        db_secret.id,
        db_secret.name,
        vault.id,
    )

    return db_secret


@app.get("/secrets/{secret_id}", response_model=SecretWithValue)
async def get_secret(
    secret_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get secret by ID with decrypted value"""
    secret = (
        db.query(Secret)
        .join(Vault)
        .filter(Secret.id == secret_id, Vault.owner_id == current_user.id)
        .first()
    )

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")

    # Decrypt value
    decrypted_value = crypto_service.decrypt(secret.encrypted_value)

    # Update access tracking
    secret.access_count += 1
    secret.last_accessed_at = datetime.utcnow()
    db.commit()

    log_audit(
        db,
        current_user.id,
        AuditAction.READ,
        "secret",
        secret.id,
        secret.name,
        secret.vault_id,
    )

    # Return secret with decrypted value
    secret_dict = SecretResponse.from_orm(secret).dict()
    secret_dict["value"] = decrypted_value

    return secret_dict


@app.put("/secrets/{secret_id}", response_model=SecretResponse)
async def update_secret(
    secret_id: int,
    secret_update: SecretUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update secret"""
    secret = (
        db.query(Secret)
        .join(Vault)
        .filter(Secret.id == secret_id, Vault.owner_id == current_user.id)
        .first()
    )

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")

    # If value is being updated, create new version
    if secret_update.value:
        encrypted_value = crypto_service.encrypt(secret_update.value)
        secret.encrypted_value = encrypted_value
        secret.version += 1

        # Create new version
        version = SecretVersion(
            secret_id=secret.id,
            version_number=secret.version,
            encrypted_value=encrypted_value,
            created_by_id=current_user.id,
            change_description="Manual update",
        )
        db.add(version)

    # Update other fields
    update_data = secret_update.dict(exclude_unset=True, exclude={"value"})
    for field, value in update_data.items():
        setattr(secret, field, value)

    secret.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(secret)

    log_audit(
        db,
        current_user.id,
        AuditAction.UPDATE,
        "secret",
        secret.id,
        secret.name,
        secret.vault_id,
    )

    return secret


@app.delete("/secrets/{secret_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_secret(
    secret_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete secret"""
    secret = (
        db.query(Secret)
        .join(Vault)
        .filter(Secret.id == secret_id, Vault.owner_id == current_user.id)
        .first()
    )

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")

    vault = secret.vault
    vault.secret_count -= 1

    log_audit(
        db,
        current_user.id,
        AuditAction.DELETE,
        "secret",
        secret.id,
        secret.name,
        secret.vault_id,
    )

    db.delete(secret)
    db.commit()
    return None


@app.post("/secrets/{secret_id}/rotate", response_model=SecretRotationResponse)
async def rotate_secret(
    secret_id: int,
    rotation_request: SecretRotationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rotate secret (generate new value)"""
    secret = (
        db.query(Secret)
        .join(Vault)
        .filter(Secret.id == secret_id, Vault.owner_id == current_user.id)
        .first()
    )

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")

    old_version = secret.version

    # Generate new secret value based on type
    new_value = crypto_service.generate_token(32)
    encrypted_value = crypto_service.encrypt(new_value)

    secret.encrypted_value = encrypted_value
    secret.version += 1
    secret.last_rotated_at = datetime.utcnow()

    # Create new version
    version = SecretVersion(
        secret_id=secret.id,
        version_number=secret.version,
        encrypted_value=encrypted_value,
        created_by_id=current_user.id,
        change_description=rotation_request.rotation_reason or "Manual rotation",
    )
    db.add(version)

    # Log rotation
    rotation = SecretRotation(
        secret_id=secret.id,
        old_version=old_version,
        new_version=secret.version,
        rotation_type="manual",
        rotated_by_id=current_user.id,
        rotation_reason=rotation_request.rotation_reason,
        success=True,
    )
    db.add(rotation)

    db.commit()
    db.refresh(rotation)

    log_audit(
        db,
        current_user.id,
        AuditAction.ROTATE,
        "secret",
        secret.id,
        secret.name,
        secret.vault_id,
    )

    return rotation


@app.get("/secrets/{secret_id}/versions", response_model=List[SecretVersionResponse])
async def get_secret_versions(
    secret_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get secret version history"""
    secret = (
        db.query(Secret)
        .join(Vault)
        .filter(Secret.id == secret_id, Vault.owner_id == current_user.id)
        .first()
    )

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")

    versions = (
        db.query(SecretVersion)
        .filter(SecretVersion.secret_id == secret_id)
        .order_by(SecretVersion.version_number.desc())
        .all()
    )

    return versions


# Analytics endpoints
@app.get("/analytics/overview", response_model=VaultAnalytics)
async def get_analytics_overview(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get analytics overview"""
    vaults = db.query(Vault).filter(Vault.owner_id == current_user.id).all()
    secrets = (
        db.query(Secret).join(Vault).filter(Vault.owner_id == current_user.id).all()
    )

    total_vaults = len(vaults)
    total_secrets = len(secrets)
    active_secrets = sum(1 for s in secrets if s.status == SecretStatus.ACTIVE)
    expired_secrets = sum(1 for s in secrets if s.status == SecretStatus.EXPIRED)
    revoked_secrets = sum(1 for s in secrets if s.status == SecretStatus.REVOKED)

    # Count secrets by type
    secrets_by_type = {}
    for secret in secrets:
        secret_type = secret.secret_type.value
        secrets_by_type[secret_type] = secrets_by_type.get(secret_type, 0) + 1

    total_access_grants = (
        db.query(AccessGrant)
        .join(Secret)
        .join(Vault)
        .filter(Vault.owner_id == current_user.id)
        .count()
    )

    total_policies = (
        db.query(Policy).join(Vault).filter(Vault.owner_id == current_user.id).count()
    )

    return VaultAnalytics(
        total_vaults=total_vaults,
        total_secrets=total_secrets,
        active_secrets=active_secrets,
        expired_secrets=expired_secrets,
        revoked_secrets=revoked_secrets,
        total_access_grants=total_access_grants,
        total_policies=total_policies,
        secrets_by_type=secrets_by_type,
    )


@app.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    vault_id: Optional[int] = None,
    action: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get audit logs"""
    query = db.query(AuditLog).filter(AuditLog.user_id == current_user.id)

    if vault_id:
        query = query.filter(AuditLog.vault_id == vault_id)
    if action:
        query = query.filter(AuditLog.action == action)

    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
