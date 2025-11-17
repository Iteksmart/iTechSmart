"""
iTechSmart Connect - API Management Platform
Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, Query, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import uvicorn
import os
import time
import hashlib
import secrets

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize FastAPI app
app = FastAPI(
    title="iTechSmart Connect API",
    description="Enterprise API Management Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo (replace with database in production)
api_registry = {}
api_keys_store = {}
request_logs = []
rate_limits = {}

# ============================================================================
# AUTHENTICATION UTILITIES
# ============================================================================


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username, "id": payload.get("user_id")}
    except JWTError:
        raise credentials_exception


def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"sk_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


# ============================================================================
# MIDDLEWARE FOR API KEY VALIDATION
# ============================================================================


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests"""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log request
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "client_ip": request.client.host if request.client else None,
    }
    request_logs.append(log_entry)

    # Keep only last 1000 logs
    if len(request_logs) > 1000:
        request_logs.pop(0)

    return response


# ============================================================================
# HEALTH & ROOT ENDPOINTS
# ============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iTechSmart Connect",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to iTechSmart Connect API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint - returns JWT access token"""
    # Mock authentication
    mock_users = {
        "admin": {
            "username": "admin",
            "email": "admin@itechsmart.dev",
            "password_hash": get_password_hash("password"),
            "id": "user_001",
            "role": "admin",
        }
    }

    user = mock_users.get(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": user["id"], "role": user["role"]},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        },
    }


@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# ============================================================================
# API GATEWAY ENDPOINTS
# ============================================================================


@app.get("/apis")
async def list_apis(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """List all registered APIs"""
    apis = list(api_registry.values())

    # Filter by status if provided
    if status:
        apis = [api for api in apis if api.get("status") == status]

    return {
        "data": apis[skip : skip + limit],
        "total": len(apis),
        "skip": skip,
        "limit": limit,
    }


@app.post("/apis")
async def create_api(
    name: str,
    base_url: str,
    version: str = "v1",
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Register a new API"""
    api_id = f"api_{len(api_registry) + 1}"

    api = {
        "id": api_id,
        "name": name,
        "base_url": base_url,
        "version": version,
        "description": description,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "created_by": current_user["id"],
        "endpoints": [],
        "rate_limit": 1000,
        "timeout": 30,
    }

    api_registry[api_id] = api
    return api


@app.get("/apis/{api_id}")
async def get_api(api_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific API details"""
    if api_id not in api_registry:
        raise HTTPException(status_code=404, detail="API not found")

    return api_registry[api_id]


@app.put("/apis/{api_id}")
async def update_api(
    api_id: str,
    name: Optional[str] = None,
    base_url: Optional[str] = None,
    version: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Update API configuration"""
    if api_id not in api_registry:
        raise HTTPException(status_code=404, detail="API not found")

    api = api_registry[api_id]

    if name:
        api["name"] = name
    if base_url:
        api["base_url"] = base_url
    if version:
        api["version"] = version
    if description:
        api["description"] = description
    if status:
        api["status"] = status

    api["updated_at"] = datetime.utcnow().isoformat()

    return api


@app.delete("/apis/{api_id}")
async def delete_api(api_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an API"""
    if api_id not in api_registry:
        raise HTTPException(status_code=404, detail="API not found")

    del api_registry[api_id]

    return {"message": "API deleted successfully", "api_id": api_id}


# ============================================================================
# API ENDPOINTS MANAGEMENT
# ============================================================================


@app.get("/apis/{api_id}/endpoints")
async def list_api_endpoints(
    api_id: str, current_user: dict = Depends(get_current_user)
):
    """List all endpoints for an API"""
    if api_id not in api_registry:
        raise HTTPException(status_code=404, detail="API not found")

    return {"api_id": api_id, "endpoints": api_registry[api_id].get("endpoints", [])}


@app.post("/apis/{api_id}/endpoints")
async def create_api_endpoint(
    api_id: str,
    path: str,
    method: str,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Add an endpoint to an API"""
    if api_id not in api_registry:
        raise HTTPException(status_code=404, detail="API not found")

    endpoint = {
        "id": f"endpoint_{len(api_registry[api_id]['endpoints']) + 1}",
        "path": path,
        "method": method.upper(),
        "description": description,
        "created_at": datetime.utcnow().isoformat(),
    }

    api_registry[api_id]["endpoints"].append(endpoint)

    return endpoint


# ============================================================================
# API KEYS MANAGEMENT
# ============================================================================


@app.get("/api-keys")
async def list_api_keys(
    skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user)
):
    """List all API keys"""
    keys = [
        {**key, "key": "sk_***" + key["key"][-8:]}  # Mask the key
        for key in api_keys_store.values()
        if key["user_id"] == current_user["id"]
    ]

    return {"data": keys[skip : skip + limit], "total": len(keys)}


@app.post("/api-keys")
async def create_api_key(
    name: str,
    scopes: List[str] = [],
    expires_in_days: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
):
    """Create a new API key"""
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)

    expires_at = None
    if expires_in_days:
        expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()

    key_data = {
        "id": f"key_{len(api_keys_store) + 1}",
        "name": name,
        "key": api_key,
        "key_hash": key_hash,
        "scopes": scopes,
        "user_id": current_user["id"],
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at,
        "is_active": True,
        "last_used": None,
    }

    api_keys_store[key_hash] = key_data

    return {
        "id": key_data["id"],
        "name": name,
        "key": api_key,  # Only shown once
        "scopes": scopes,
        "expires_at": expires_at,
        "created_at": key_data["created_at"],
    }


@app.delete("/api-keys/{key_id}")
async def revoke_api_key(key_id: str, current_user: dict = Depends(get_current_user)):
    """Revoke an API key"""
    for key_hash, key_data in api_keys_store.items():
        if key_data["id"] == key_id and key_data["user_id"] == current_user["id"]:
            key_data["is_active"] = False
            key_data["revoked_at"] = datetime.utcnow().isoformat()
            return {"message": "API key revoked successfully", "key_id": key_id}

    raise HTTPException(status_code=404, detail="API key not found")


# ============================================================================
# RATE LIMITING
# ============================================================================


@app.get("/rate-limits")
async def list_rate_limits(current_user: dict = Depends(get_current_user)):
    """List all rate limit configurations"""
    return {"data": list(rate_limits.values()), "total": len(rate_limits)}


@app.post("/rate-limits")
async def create_rate_limit(
    api_id: str,
    limit: int,
    window_seconds: int = 60,
    current_user: dict = Depends(get_current_user),
):
    """Create a rate limit for an API"""
    if api_id not in api_registry:
        raise HTTPException(status_code=404, detail="API not found")

    rate_limit_id = f"rl_{len(rate_limits) + 1}"

    rate_limit = {
        "id": rate_limit_id,
        "api_id": api_id,
        "limit": limit,
        "window_seconds": window_seconds,
        "created_at": datetime.utcnow().isoformat(),
    }

    rate_limits[rate_limit_id] = rate_limit

    return rate_limit


# ============================================================================
# ANALYTICS & MONITORING
# ============================================================================


@app.get("/analytics/overview")
async def get_analytics_overview(current_user: dict = Depends(get_current_user)):
    """Get analytics overview"""
    total_requests = len(request_logs)
    successful_requests = len(
        [log for log in request_logs if 200 <= log["status_code"] < 300]
    )
    failed_requests = len([log for log in request_logs if log["status_code"] >= 400])

    avg_duration = (
        sum(log["duration_ms"] for log in request_logs) / total_requests
        if total_requests > 0
        else 0
    )

    return {
        "total_apis": len(api_registry),
        "total_api_keys": len(api_keys_store),
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate": (
            successful_requests / total_requests if total_requests > 0 else 0
        ),
        "avg_response_time_ms": round(avg_duration, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/analytics/requests")
async def get_request_analytics(
    hours: int = 24, current_user: dict = Depends(get_current_user)
):
    """Get request analytics"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    recent_logs = [
        log
        for log in request_logs
        if datetime.fromisoformat(log["timestamp"]) > cutoff_time
    ]

    # Group by hour
    hourly_stats = {}
    for log in recent_logs:
        hour = log["timestamp"][:13]  # YYYY-MM-DDTHH
        if hour not in hourly_stats:
            hourly_stats[hour] = {"count": 0, "errors": 0, "total_duration": 0}

        hourly_stats[hour]["count"] += 1
        if log["status_code"] >= 400:
            hourly_stats[hour]["errors"] += 1
        hourly_stats[hour]["total_duration"] += log["duration_ms"]

    return {
        "period_hours": hours,
        "total_requests": len(recent_logs),
        "hourly_stats": hourly_stats,
    }


@app.get("/analytics/top-apis")
async def get_top_apis(limit: int = 10, current_user: dict = Depends(get_current_user)):
    """Get top APIs by request count"""
    # Mock data for demonstration
    top_apis = [
        {
            "api_id": api_id,
            "name": api["name"],
            "request_count": len(request_logs) // len(api_registry),
        }
        for api_id, api in list(api_registry.items())[:limit]
    ]

    return {"data": top_apis, "total": len(top_apis)}


# ============================================================================
# REQUEST LOGS
# ============================================================================


@app.get("/logs")
async def get_request_logs(
    skip: int = 0,
    limit: int = 100,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
):
    """Get request logs"""
    logs = request_logs.copy()

    # Filter by method
    if method:
        logs = [log for log in logs if log["method"] == method.upper()]

    # Filter by status code
    if status_code:
        logs = [log for log in logs if log["status_code"] == status_code]

    # Sort by timestamp (newest first)
    logs.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "data": logs[skip : skip + limit],
        "total": len(logs),
        "skip": skip,
        "limit": limit,
    }


# ============================================================================
# API VERSIONING
# ============================================================================


@app.get("/apis/{api_id}/versions")
async def list_api_versions(
    api_id: str, current_user: dict = Depends(get_current_user)
):
    """List all versions of an API"""
    if api_id not in api_registry:
        raise HTTPException(status_code=404, detail="API not found")

    # Mock versions
    versions = [
        {
            "version": "v1",
            "status": "active",
            "created_at": "2024-01-01T00:00:00",
            "is_default": True,
        },
        {
            "version": "v2",
            "status": "beta",
            "created_at": "2024-01-15T00:00:00",
            "is_default": False,
        },
    ]

    return {"api_id": api_id, "versions": versions}


# ============================================================================
# WEBHOOKS
# ============================================================================


@app.get("/webhooks")
async def list_webhooks(current_user: dict = Depends(get_current_user)):
    """List all webhooks"""
    # Mock webhooks
    webhooks = [
        {
            "id": "webhook_001",
            "name": "API Status Change",
            "url": "https://example.com/webhook",
            "events": ["api.created", "api.updated", "api.deleted"],
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
        }
    ]

    return {"data": webhooks, "total": len(webhooks)}


@app.post("/webhooks")
async def create_webhook(
    name: str,
    url: str,
    events: List[str],
    current_user: dict = Depends(get_current_user),
):
    """Create a new webhook"""
    webhook = {
        "id": f"webhook_{secrets.token_hex(8)}",
        "name": name,
        "url": url,
        "events": events,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": current_user["id"],
    }

    return webhook


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
