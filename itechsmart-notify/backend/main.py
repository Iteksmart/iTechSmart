"""
iTechSmart Notify - Main FastAPI Application
Notification Service Platform
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, BackgroundTasks
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
    Notification,
    Template,
    Channel,
    DeliveryLog,
    Schedule,
    Subscriber,
    Webhook,
    AuditLog,
    NotificationStatus,
    NotificationPriority,
    ChannelType,
)
from schemas import (
    UserCreate,
    UserResponse,
    NotificationCreate,
    NotificationResponse,
    TemplateCreate,
    TemplateResponse,
    ChannelCreate,
    ChannelResponse,
    NotificationAnalytics,
    Token,
)

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create FastAPI app
app = FastAPI(
    title="iTechSmart Notify",
    description="Enterprise Notification Service Platform",
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


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
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


async def send_notification_task(notification_id: int, db: Session):
    """Background task to send notification"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )
    if not notification:
        return

    # Update status to sending
    notification.status = NotificationStatus.SENDING
    db.commit()

    # Simulate sending (in production, integrate with actual services)
    try:
        # Log delivery attempt
        log = DeliveryLog(
            notification_id=notification.id,
            attempt_number=notification.retry_count + 1,
            status=NotificationStatus.SENT,
            response_code="200",
            response_message="Success",
            attempted_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=100,
        )
        db.add(log)

        # Update notification status
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        # Log failure
        log = DeliveryLog(
            notification_id=notification.id,
            attempt_number=notification.retry_count + 1,
            status=NotificationStatus.FAILED,
            error_message=str(e),
            attempted_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.add(log)

        notification.status = NotificationStatus.FAILED
        notification.error_message = str(e)
        notification.retry_count += 1
        db.commit()


# Startup event
@app.on_event("startup")
async def startup_event():
    init_db()


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "iTechSmart Notify"}


# Authentication endpoints
@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
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
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone_number=user.phone_number,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


# Notification endpoints
@app.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    status: Optional[str] = None,
    channel_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if status:
        query = query.filter(Notification.status == status)
    if channel_type:
        query = query.filter(Notification.channel_type == channel_type)

    notifications = (
        query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    )
    return notifications


@app.post(
    "/notifications",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Create notification
    db_notification = Notification(
        user_id=current_user.id,
        channel_type=notification.channel_type,
        recipient=notification.recipient,
        recipient_name=notification.recipient_name,
        subject=notification.subject,
        body=notification.body,
        html_body=notification.html_body,
        priority=notification.priority,
        template_id=notification.template_id,
        template_variables=notification.template_variables,
        scheduled_at=notification.scheduled_at,
        metadata=notification.metadata,
        tags=notification.tags,
        status=(
            NotificationStatus.QUEUED
            if not notification.scheduled_at
            else NotificationStatus.PENDING
        ),
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # Queue for sending if not scheduled
    if not notification.scheduled_at:
        background_tasks.add_task(send_notification_task, db_notification.id, db)

    return db_notification


@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id, Notification.user_id == current_user.id
        )
        .first()
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@app.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id, Notification.user_id == current_user.id
        )
        .first()
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return None


# Template endpoints
@app.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    template_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Template).filter(Template.created_by_id == current_user.id)

    if template_type:
        query = query.filter(Template.template_type == template_type)

    templates = query.offset(skip).limit(limit).all()
    return templates


@app.post(
    "/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED
)
async def create_template(
    template: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_template = Template(
        name=template.name,
        description=template.description,
        template_type=template.template_type,
        subject=template.subject,
        body=template.body,
        html_body=template.html_body,
        variables=template.variables,
        category=template.category,
        tags=template.tags,
        created_by_id=current_user.id,
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@app.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.created_by_id == current_user.id)
        .first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@app.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.created_by_id == current_user.id)
        .first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()
    return None


# Channel endpoints
@app.get("/channels", response_model=List[ChannelResponse])
async def list_channels(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    channels = db.query(Channel).filter(Channel.owner_id == current_user.id).all()
    return channels


@app.post(
    "/channels", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED
)
async def create_channel(
    channel: ChannelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_channel = Channel(
        name=channel.name,
        channel_type=channel.channel_type,
        description=channel.description,
        configuration=channel.configuration,
        rate_limit_per_minute=channel.rate_limit_per_minute,
        rate_limit_per_hour=channel.rate_limit_per_hour,
        rate_limit_per_day=channel.rate_limit_per_day,
        owner_id=current_user.id,
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


# Analytics endpoints
@app.get("/analytics/overview", response_model=NotificationAnalytics)
async def get_analytics_overview(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    notifications = (
        db.query(Notification).filter(Notification.user_id == current_user.id).all()
    )

    total = len(notifications)
    sent = sum(1 for n in notifications if n.status == NotificationStatus.SENT)
    delivered = sum(
        1 for n in notifications if n.status == NotificationStatus.DELIVERED
    )
    failed = sum(1 for n in notifications if n.status == NotificationStatus.FAILED)
    pending = sum(1 for n in notifications if n.status == NotificationStatus.PENDING)

    delivery_rate = (delivered / total * 100) if total > 0 else 0

    # Count by channel
    by_channel = {}
    for n in notifications:
        channel = n.channel_type.value
        by_channel[channel] = by_channel.get(channel, 0) + 1

    return NotificationAnalytics(
        total_notifications=total,
        sent_notifications=sent,
        delivered_notifications=delivered,
        failed_notifications=failed,
        pending_notifications=pending,
        delivery_rate=delivery_rate,
        notifications_by_channel=by_channel,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
