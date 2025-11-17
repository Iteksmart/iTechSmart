"""
iTechSmart Workflow - Main FastAPI Application
Business Process Automation Platform with Automation Orchestrator
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Import API routers
from app.api.automation_orchestrator import router as automation_router

from database import get_db, init_db
from models import (
    User,
    Workflow,
    Execution,
    TaskExecution,
    Trigger,
    WorkflowVariable,
    Integration,
    Template,
    Schedule,
    ExecutionLog,
    AuditLog,
    WorkflowStatus,
    ExecutionStatus,
)
from schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    ExecutionCreate,
    ExecutionResponse,
    ExecutionListResponse,
    TaskExecutionResponse,
    TriggerCreate,
    TriggerUpdate,
    TriggerResponse,
    WorkflowVariableCreate,
    WorkflowVariableUpdate,
    WorkflowVariableResponse,
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationResponse,
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ExecutionLogResponse,
    WorkflowAnalytics,
    ExecutionAnalytics,
    TopWorkflow,
    Token,
    TokenData,
)

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create FastAPI app
app = FastAPI(
    title="iTechSmart Workflow",
    description="Business Process Automation Platform with Visual Workflow Builder",
    version="1.1.0",
)

# Include routers
app.include_router(automation_router)

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


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "iTechSmart Workflow"}


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
    # Check if user exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# Workflow endpoints
@app.get("/workflows", response_model=List[WorkflowListResponse])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List workflows"""
    query = db.query(Workflow).filter(Workflow.owner_id == current_user.id)

    if status:
        query = query.filter(Workflow.status == status)
    if category:
        query = query.filter(Workflow.category == category)
    if search:
        query = query.filter(Workflow.name.ilike(f"%{search}%"))

    workflows = query.offset(skip).limit(limit).all()
    return workflows


@app.post(
    "/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED
)
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new workflow"""
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        definition=workflow.definition,
        status=workflow.status,
        category=workflow.category,
        tags=workflow.tags,
        owner_id=current_user.id,
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


@app.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get workflow by ID"""
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id, Workflow.owner_id == current_user.id)
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow


@app.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update workflow"""
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id, Workflow.owner_id == current_user.id)
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Update fields
    update_data = workflow_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)

    workflow.version += 1
    workflow.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(workflow)
    return workflow


@app.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete workflow"""
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id, Workflow.owner_id == current_user.id)
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    db.delete(workflow)
    db.commit()
    return None


# Execution endpoints
@app.get("/executions", response_model=List[ExecutionListResponse])
async def list_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    workflow_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List executions"""
    query = (
        db.query(Execution).join(Workflow).filter(Workflow.owner_id == current_user.id)
    )

    if workflow_id:
        query = query.filter(Execution.workflow_id == workflow_id)
    if status:
        query = query.filter(Execution.status == status)

    executions = (
        query.order_by(Execution.created_at.desc()).offset(skip).limit(limit).all()
    )
    return executions


@app.post(
    "/executions", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED
)
async def create_execution(
    execution: ExecutionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new execution (trigger workflow)"""
    # Verify workflow exists and belongs to user
    workflow = (
        db.query(Workflow)
        .filter(
            Workflow.id == execution.workflow_id, Workflow.owner_id == current_user.id
        )
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.status != WorkflowStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Workflow is not active")

    # Create execution
    db_execution = Execution(
        workflow_id=execution.workflow_id,
        trigger_type=execution.trigger_type,
        triggered_by_user_id=current_user.id,
        input_data=execution.input_data,
        status=ExecutionStatus.PENDING,
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)

    # Update workflow execution count
    workflow.execution_count += 1
    db.commit()

    return db_execution


@app.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get execution by ID"""
    execution = (
        db.query(Execution)
        .join(Workflow)
        .filter(Execution.id == execution_id, Workflow.owner_id == current_user.id)
        .first()
    )

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution


@app.get("/executions/{execution_id}/tasks", response_model=List[TaskExecutionResponse])
async def get_execution_tasks(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get tasks for an execution"""
    execution = (
        db.query(Execution)
        .join(Workflow)
        .filter(Execution.id == execution_id, Workflow.owner_id == current_user.id)
        .first()
    )

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    tasks = (
        db.query(TaskExecution).filter(TaskExecution.execution_id == execution_id).all()
    )
    return tasks


@app.get("/executions/{execution_id}/logs", response_model=List[ExecutionLogResponse])
async def get_execution_logs(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get logs for an execution"""
    execution = (
        db.query(Execution)
        .join(Workflow)
        .filter(Execution.id == execution_id, Workflow.owner_id == current_user.id)
        .first()
    )

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    logs = (
        db.query(ExecutionLog)
        .filter(ExecutionLog.execution_id == execution_id)
        .order_by(ExecutionLog.created_at)
        .all()
    )
    return logs


# Trigger endpoints
@app.get("/triggers", response_model=List[TriggerResponse])
async def list_triggers(
    workflow_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List triggers"""
    query = (
        db.query(Trigger).join(Workflow).filter(Workflow.owner_id == current_user.id)
    )

    if workflow_id:
        query = query.filter(Trigger.workflow_id == workflow_id)

    triggers = query.all()
    return triggers


@app.post(
    "/triggers", response_model=TriggerResponse, status_code=status.HTTP_201_CREATED
)
async def create_trigger(
    trigger: TriggerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new trigger"""
    # Verify workflow exists and belongs to user
    workflow = (
        db.query(Workflow)
        .filter(
            Workflow.id == trigger.workflow_id, Workflow.owner_id == current_user.id
        )
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    db_trigger = Trigger(
        workflow_id=trigger.workflow_id,
        name=trigger.name,
        trigger_type=trigger.trigger_type,
        configuration=trigger.configuration,
        is_active=trigger.is_active,
    )
    db.add(db_trigger)
    db.commit()
    db.refresh(db_trigger)
    return db_trigger


@app.put("/triggers/{trigger_id}", response_model=TriggerResponse)
async def update_trigger(
    trigger_id: int,
    trigger_update: TriggerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update trigger"""
    trigger = (
        db.query(Trigger)
        .join(Workflow)
        .filter(Trigger.id == trigger_id, Workflow.owner_id == current_user.id)
        .first()
    )

    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    update_data = trigger_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trigger, field, value)

    trigger.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(trigger)
    return trigger


@app.delete("/triggers/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trigger(
    trigger_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete trigger"""
    trigger = (
        db.query(Trigger)
        .join(Workflow)
        .filter(Trigger.id == trigger_id, Workflow.owner_id == current_user.id)
        .first()
    )

    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    db.delete(trigger)
    db.commit()
    return None


# Integration endpoints
@app.get("/integrations", response_model=List[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """List integrations"""
    integrations = (
        db.query(Integration).filter(Integration.owner_id == current_user.id).all()
    )
    return integrations


@app.post(
    "/integrations",
    response_model=IntegrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_integration(
    integration: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new integration"""
    db_integration = Integration(
        name=integration.name,
        type=integration.type,
        description=integration.description,
        configuration=integration.configuration,
        is_active=integration.is_active,
        owner_id=current_user.id,
    )
    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)
    return db_integration


# Template endpoints
@app.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List workflow templates"""
    query = db.query(Template)

    if category:
        query = query.filter(Template.category == category)
    if featured is not None:
        query = query.filter(Template.is_featured == featured)

    templates = query.all()
    return templates


@app.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get template by ID"""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


# Analytics endpoints
@app.get("/analytics/overview", response_model=WorkflowAnalytics)
async def get_analytics_overview(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get analytics overview"""
    workflows = db.query(Workflow).filter(Workflow.owner_id == current_user.id).all()
    executions = (
        db.query(Execution)
        .join(Workflow)
        .filter(Workflow.owner_id == current_user.id)
        .all()
    )

    total_workflows = len(workflows)
    active_workflows = sum(1 for w in workflows if w.status == WorkflowStatus.ACTIVE)
    draft_workflows = sum(1 for w in workflows if w.status == WorkflowStatus.DRAFT)
    paused_workflows = sum(1 for w in workflows if w.status == WorkflowStatus.PAUSED)
    archived_workflows = sum(
        1 for w in workflows if w.status == WorkflowStatus.ARCHIVED
    )

    total_executions = len(executions)
    successful_executions = sum(
        1 for e in executions if e.status == ExecutionStatus.COMPLETED
    )
    failed_executions = sum(1 for e in executions if e.status == ExecutionStatus.FAILED)

    avg_execution_time = 0
    if executions:
        durations = [e.duration_seconds for e in executions if e.duration_seconds]
        if durations:
            avg_execution_time = sum(durations) / len(durations)

    return WorkflowAnalytics(
        total_workflows=total_workflows,
        active_workflows=active_workflows,
        draft_workflows=draft_workflows,
        paused_workflows=paused_workflows,
        archived_workflows=archived_workflows,
        total_executions=total_executions,
        successful_executions=successful_executions,
        failed_executions=failed_executions,
        avg_execution_time=avg_execution_time,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
