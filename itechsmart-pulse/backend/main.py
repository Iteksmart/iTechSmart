"""
iTechSmart Pulse - Analytics & Business Intelligence Platform
Main FastAPI Application with Authentication
"""

from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import uvicorn
import os

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize FastAPI app
app = FastAPI(
    title="iTechSmart Pulse API",
    description="Enterprise Analytics & Business Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTHENTICATION UTILITIES
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
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

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from token"""
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

# ============================================================================
# HEALTH & ROOT ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iTechSmart Pulse",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to iTechSmart Pulse API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - returns JWT access token
    Default credentials: admin@itechsmart.dev / password
    """
    # Mock authentication - replace with actual database lookup
    mock_users = {
        "admin": {
            "username": "admin",
            "email": "admin@itechsmart.dev",
            "password_hash": get_password_hash("password"),
            "id": "user_001",
            "role": "admin"
        },
        "analyst": {
            "username": "analyst",
            "email": "analyst@itechsmart.dev",
            "password_hash": get_password_hash("password"),
            "id": "user_002",
            "role": "analyst"
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
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/users/register")
async def register_user(username: str, email: str, password: str, full_name: Optional[str] = None):
    """Register a new user"""
    # Mock registration - replace with actual database insert
    password_hash = get_password_hash(password)
    return {
        "message": "User registered successfully",
        "username": username,
        "email": email
    }

# ============================================================================
# DATA SOURCES ENDPOINTS
# ============================================================================

@app.get("/data-sources")
async def get_data_sources(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get all data sources"""
    mock_sources = [
        {
            "id": "ds_001",
            "name": "Production Database",
            "type": "postgresql",
            "status": "active",
            "last_tested": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "ds_002",
            "name": "Analytics Warehouse",
            "type": "clickhouse",
            "status": "active",
            "last_tested": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "ds_003",
            "name": "Sales CRM",
            "type": "mysql",
            "status": "active",
            "last_tested": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    return {"data": mock_sources[skip:skip+limit], "total": len(mock_sources)}

@app.post("/data-sources")
async def create_data_source(
    name: str,
    type: str,
    connection_string: str,
    current_user: dict = Depends(get_current_user)
):
    """Create a new data source"""
    return {
        "id": "ds_new",
        "name": name,
        "type": type,
        "status": "active",
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/data-sources/{source_id}")
async def get_data_source(
    source_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific data source"""
    return {
        "id": source_id,
        "name": "Production Database",
        "type": "postgresql",
        "status": "active",
        "connection_string": "postgresql://user:***@localhost:5432/prod",
        "last_tested": datetime.utcnow().isoformat()
    }

@app.post("/data-sources/{source_id}/test")
async def test_data_source(
    source_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Test data source connection"""
    return {
        "status": "success",
        "message": "Connection successful",
        "latency_ms": 45,
        "tested_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# DATASETS ENDPOINTS
# ============================================================================

@app.get("/datasets")
async def get_datasets(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get all datasets"""
    mock_datasets = [
        {
            "id": "dataset_001",
            "name": "Sales Transactions",
            "description": "Daily sales transaction data",
            "row_count": 125000,
            "size_bytes": 5242880,
            "last_refreshed": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "dataset_002",
            "name": "Customer Analytics",
            "description": "Customer behavior and demographics",
            "row_count": 50000,
            "size_bytes": 2097152,
            "last_refreshed": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    return {"data": mock_datasets[skip:skip+limit], "total": len(mock_datasets)}

@app.post("/datasets")
async def create_dataset(
    name: str,
    source_id: str,
    query: str,
    current_user: dict = Depends(get_current_user)
):
    """Create a new dataset"""
    return {
        "id": "dataset_new",
        "name": name,
        "source_id": source_id,
        "query": query,
        "created_at": datetime.utcnow().isoformat()
    }

@app.post("/datasets/{dataset_id}/refresh")
async def refresh_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Refresh dataset data"""
    return {
        "status": "success",
        "message": "Dataset refresh initiated",
        "dataset_id": dataset_id,
        "started_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# REPORTS ENDPOINTS
# ============================================================================

@app.get("/reports")
async def get_reports(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get all reports"""
    mock_reports = [
        {
            "id": "report_001",
            "name": "Monthly Sales Report",
            "type": "tabular",
            "last_run": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "report_002",
            "name": "Customer Segmentation",
            "type": "analytical",
            "last_run": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    return {"data": mock_reports[skip:skip+limit], "total": len(mock_reports)}

@app.post("/reports")
async def create_report(
    name: str,
    type: str,
    dataset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Create a new report"""
    return {
        "id": "report_new",
        "name": name,
        "type": type,
        "dataset_id": dataset_id,
        "created_at": datetime.utcnow().isoformat()
    }

@app.post("/reports/{report_id}/execute")
async def execute_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Execute a report"""
    return {
        "status": "success",
        "message": "Report execution initiated",
        "report_id": report_id,
        "execution_id": "exec_001",
        "started_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# DASHBOARDS ENDPOINTS
# ============================================================================

@app.get("/dashboards")
async def get_dashboards(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get all dashboards"""
    mock_dashboards = [
        {
            "id": "dashboard_001",
            "name": "Executive Dashboard",
            "description": "High-level business metrics",
            "is_public": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "dashboard_002",
            "name": "Sales Analytics",
            "description": "Detailed sales performance",
            "is_public": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    return {"data": mock_dashboards[skip:skip+limit], "total": len(mock_dashboards)}

@app.post("/dashboards")
async def create_dashboard(
    name: str,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new dashboard"""
    return {
        "id": "dashboard_new",
        "name": name,
        "description": description,
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/dashboards/{dashboard_id}")
async def get_dashboard(
    dashboard_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific dashboard"""
    return {
        "id": dashboard_id,
        "name": "Executive Dashboard",
        "description": "High-level business metrics",
        "layout": {"widgets": []},
        "created_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# VISUALIZATIONS ENDPOINTS
# ============================================================================

@app.get("/visualizations")
async def get_visualizations(
    dashboard_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all visualizations"""
    mock_visualizations = [
        {
            "id": "viz_001",
            "name": "Revenue Trend",
            "type": "line",
            "dashboard_id": "dashboard_001",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "viz_002",
            "name": "Customer Segments",
            "type": "pie",
            "dashboard_id": "dashboard_002",
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    if dashboard_id:
        mock_visualizations = [v for v in mock_visualizations if v["dashboard_id"] == dashboard_id]
    
    return {"data": mock_visualizations, "total": len(mock_visualizations)}

@app.post("/visualizations")
async def create_visualization(
    name: str,
    type: str,
    dataset_id: str,
    dashboard_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new visualization"""
    return {
        "id": "viz_new",
        "name": name,
        "type": type,
        "dataset_id": dataset_id,
        "dashboard_id": dashboard_id,
        "created_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# QUERIES ENDPOINTS
# ============================================================================

@app.get("/queries")
async def get_queries(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get all saved queries"""
    mock_queries = [
        {
            "id": "query_001",
            "name": "Daily Revenue",
            "sql_query": "SELECT SUM(amount) FROM sales_transactions WHERE date = CURRENT_DATE",
            "execution_count": 150,
            "avg_execution_time": 0.25,
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    return {"data": mock_queries[skip:skip+limit], "total": len(mock_queries)}

@app.post("/queries/execute")
async def execute_query(
    sql_query: str,
    data_source_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Execute a SQL query"""
    return {
        "status": "success",
        "execution_time": 0.245,
        "row_count": 1000,
        "columns": ["id", "name", "amount", "date"],
        "data": [
            {"id": 1, "name": "Product A", "amount": 100.50, "date": "2024-01-15"},
            {"id": 2, "name": "Product B", "amount": 250.75, "date": "2024-01-15"}
        ]
    }

@app.post("/queries")
async def save_query(
    name: str,
    sql_query: str,
    data_source_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Save a query"""
    return {
        "id": "query_new",
        "name": name,
        "sql_query": sql_query,
        "data_source_id": data_source_id,
        "created_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================

@app.get("/alerts")
async def get_alerts(
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all alerts"""
    mock_alerts = [
        {
            "id": "alert_001",
            "name": "Low Revenue Alert",
            "is_active": True,
            "trigger_count": 5,
            "last_triggered": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    if is_active is not None:
        mock_alerts = [a for a in mock_alerts if a["is_active"] == is_active]
    
    return {"data": mock_alerts, "total": len(mock_alerts)}

@app.post("/alerts")
async def create_alert(
    name: str,
    query_id: str,
    condition: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a new alert"""
    return {
        "id": "alert_new",
        "name": name,
        "query_id": query_id,
        "condition": condition,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/analytics/overview")
async def get_analytics_overview(current_user: dict = Depends(get_current_user)):
    """Get analytics overview metrics"""
    return {
        "total_queries": 1250,
        "total_reports": 45,
        "total_dashboards": 12,
        "total_data_sources": 8,
        "active_users": 25,
        "avg_query_time": 0.345,
        "data_processed_gb": 125.5,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/analytics/query-performance")
async def get_query_performance(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Get query performance metrics"""
    return {
        "avg_execution_time": 0.345,
        "p95_execution_time": 1.250,
        "total_queries": 1250,
        "failed_queries": 15,
        "success_rate": 0.988,
        "period_days": days
    }

@app.get("/analytics/user-activity")
async def get_user_activity(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Get user activity metrics"""
    return {
        "active_users": 25,
        "total_actions": 5420,
        "top_actions": [
            {"action": "query_execute", "count": 1250},
            {"action": "dashboard_view", "count": 850},
            {"action": "report_generate", "count": 320}
        ],
        "period_days": days
    }

# ============================================================================
# SCHEDULED JOBS ENDPOINTS
# ============================================================================

@app.get("/scheduled-jobs")
async def get_scheduled_jobs(current_user: dict = Depends(get_current_user)):
    """Get all scheduled jobs"""
    mock_jobs = [
        {
            "id": "job_001",
            "name": "Daily Sales Report",
            "type": "report_generation",
            "schedule": "0 8 * * *",
            "is_active": True,
            "next_run": datetime.utcnow().isoformat(),
            "run_count": 30
        }
    ]
    return {"data": mock_jobs, "total": len(mock_jobs)}

@app.post("/scheduled-jobs")
async def create_scheduled_job(
    name: str,
    type: str,
    schedule: str,
    current_user: dict = Depends(get_current_user)
):
    """Create a new scheduled job"""
    return {
        "id": "job_new",
        "name": name,
        "type": type,
        "schedule": schedule,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )