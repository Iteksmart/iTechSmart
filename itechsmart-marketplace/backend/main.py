from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets
import json

from database import get_db, get_redis, cache, rate_limiter, analytics_tracker
from models import (
    User, DeveloperProfile, Category, App, AppVersion, Review, ReviewResponse,
    Purchase, PaymentMethod, AppAnalytics, Wishlist, AppReport, AuditLog,
    UserRole, AppStatus, PurchaseStatus, ReviewStatus
)
from schemas import (
    UserCreate, UserUpdate, UserResponse, DeveloperProfileCreate, DeveloperProfileUpdate,
    DeveloperProfileResponse, CategoryCreate, CategoryUpdate, CategoryResponse,
    AppCreate, AppUpdate, AppResponse, AppDetailResponse, AppVersionCreate, AppVersionResponse,
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewResponseCreate, ReviewResponseResponse,
    PurchaseCreate, PurchaseResponse, PaymentMethodCreate, PaymentMethodResponse,
    AppAnalyticsResponse, DashboardStats, DeveloperStats, WishlistCreate, WishlistResponse,
    AppReportCreate, AppReportResponse, AppSearchParams, Token, TokenData
)

# Initialize FastAPI app
app = FastAPI(
    title="iTechSmart Marketplace API",
    description="Enterprise App Store Platform API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

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

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for certain paths
    if request.url.path in ["/docs", "/openapi.json", "/health"]:
        return await call_next(request)
    
    # Get client identifier (IP address or user ID)
    client_id = request.client.host
    
    # Check rate limit (100 requests per minute)
    if not rate_limiter.check_rate_limit(f"rate_limit:{client_id}", 100, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    response = await call_next(request)
    return response

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# ==================== Authentication Endpoints ====================

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(
        or_(User.email == user.email, User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        avatar_url=user.avatar_url,
        bio=user.bio,
        company=user.company,
        website=user.website
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create developer profile if role is developer
    if user.role == UserRole.DEVELOPER:
        dev_profile = DeveloperProfile(user_id=db_user.id)
        db.add(dev_profile)
        db.commit()
    
    return db_user

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    return current_user

# ==================== Category Endpoints ====================

@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    categories = db.query(Category).filter(Category.is_active == True).offset(skip).limit(limit).all()
    return categories

@app.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# ==================== App Endpoints ====================

@app.get("/apps", response_model=List[AppResponse])
async def get_apps(
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    is_featured: Optional[bool] = None,
    status: Optional[AppStatus] = AppStatus.APPROVED,
    sort_by: str = "popularity",
    db: Session = Depends(get_db)
):
    query = db.query(App).filter(App.status == status)
    
    if category_id:
        query = query.filter(App.category_id == category_id)
    
    if is_featured is not None:
        query = query.filter(App.is_featured == is_featured)
    
    # Sorting
    if sort_by == "popularity":
        query = query.order_by(desc(App.total_downloads))
    elif sort_by == "rating":
        query = query.order_by(desc(App.average_rating))
    elif sort_by == "newest":
        query = query.order_by(desc(App.published_at))
    elif sort_by == "price_low":
        query = query.order_by(App.price)
    elif sort_by == "price_high":
        query = query.order_by(desc(App.price))
    
    apps = query.offset(skip).limit(limit).all()
    return apps

@app.post("/apps", response_model=AppResponse)
async def create_app(
    app: AppCreate,
    current_user: User = Depends(require_role(UserRole.DEVELOPER)),
    db: Session = Depends(get_db)
):
    # Get developer profile
    dev_profile = db.query(DeveloperProfile).filter(DeveloperProfile.user_id == current_user.id).first()
    if not dev_profile:
        raise HTTPException(status_code=400, detail="Developer profile not found")
    
    db_app = App(
        developer_id=dev_profile.id,
        **app.dict()
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/apps/{app_id}", response_model=AppDetailResponse)
async def get_app(app_id: int, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Track view
    analytics_tracker.track_view(app_id)
    
    return app

@app.put("/apps/{app_id}", response_model=AppResponse)
async def update_app(
    app_id: int,
    app_update: AppUpdate,
    current_user: User = Depends(require_role(UserRole.DEVELOPER)),
    db: Session = Depends(get_db)
):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Check ownership
    dev_profile = db.query(DeveloperProfile).filter(DeveloperProfile.user_id == current_user.id).first()
    if app.developer_id != dev_profile.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for field, value in app_update.dict(exclude_unset=True).items():
        setattr(app, field, value)
    
    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    return app

@app.delete("/apps/{app_id}")
async def delete_app(
    app_id: int,
    current_user: User = Depends(require_role(UserRole.DEVELOPER)),
    db: Session = Depends(get_db)
):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Check ownership
    dev_profile = db.query(DeveloperProfile).filter(DeveloperProfile.user_id == current_user.id).first()
    if app.developer_id != dev_profile.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(app)
    db.commit()
    return {"message": "App deleted successfully"}

@app.post("/apps/search", response_model=List[AppResponse])
async def search_apps(search_params: AppSearchParams, db: Session = Depends(get_db)):
    query = db.query(App).filter(App.status == AppStatus.APPROVED)
    
    # Text search
    if search_params.query:
        search_term = f"%{search_params.query}%"
        query = query.filter(
            or_(
                App.name.ilike(search_term),
                App.description.ilike(search_term),
                App.tagline.ilike(search_term)
            )
        )
    
    # Category filter
    if search_params.category_id:
        query = query.filter(App.category_id == search_params.category_id)
    
    # Price filters
    if search_params.is_free is not None:
        query = query.filter(App.is_free == search_params.is_free)
    if search_params.min_price is not None:
        query = query.filter(App.price >= search_params.min_price)
    if search_params.max_price is not None:
        query = query.filter(App.price <= search_params.max_price)
    
    # Rating filter
    if search_params.min_rating:
        query = query.filter(App.average_rating >= search_params.min_rating)
    
    # Sorting
    if search_params.sort_by == "popularity":
        query = query.order_by(desc(App.total_downloads))
    elif search_params.sort_by == "rating":
        query = query.order_by(desc(App.average_rating))
    elif search_params.sort_by == "price":
        query = query.order_by(App.price)
    elif search_params.sort_by == "newest":
        query = query.order_by(desc(App.published_at))
    
    # Pagination
    skip = (search_params.page - 1) * search_params.page_size
    apps = query.offset(skip).limit(search_params.page_size).all()
    
    return apps

# ==================== Review Endpoints ====================

@app.get("/apps/{app_id}/reviews", response_model=List[ReviewResponse])
async def get_app_reviews(
    app_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.app_id == app_id,
        Review.status == ReviewStatus.APPROVED
    ).offset(skip).limit(limit).all()
    return reviews

@app.post("/reviews", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user has purchased the app
    purchase = db.query(Purchase).filter(
        Purchase.user_id == current_user.id,
        Purchase.app_id == review.app_id,
        Purchase.status == PurchaseStatus.COMPLETED
    ).first()
    
    is_verified = purchase is not None
    
    # Check if user already reviewed
    existing_review = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.app_id == review.app_id
    ).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this app")
    
    db_review = Review(
        user_id=current_user.id,
        is_verified_purchase=is_verified,
        **review.dict()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Update app rating
    update_app_rating(review.app_id, db)
    
    return db_review

@app.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for field, value in review_update.dict(exclude_unset=True).items():
        setattr(review, field, value)
    
    review.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(review)
    
    # Update app rating
    update_app_rating(review.app_id, db)
    
    return review

def update_app_rating(app_id: int, db: Session):
    """Update app average rating and total reviews"""
    result = db.query(
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('total_reviews')
    ).filter(
        Review.app_id == app_id,
        Review.status == ReviewStatus.APPROVED
    ).first()
    
    app = db.query(App).filter(App.id == app_id).first()
    if app:
        app.average_rating = float(result.avg_rating or 0)
        app.total_reviews = result.total_reviews or 0
        db.commit()

# ==================== Purchase Endpoints ====================

@app.post("/purchases", response_model=PurchaseResponse)
async def create_purchase(
    purchase: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get app
    app = db.query(App).filter(App.id == purchase.app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Check if already purchased
    existing_purchase = db.query(Purchase).filter(
        Purchase.user_id == current_user.id,
        Purchase.app_id == purchase.app_id,
        Purchase.status == PurchaseStatus.COMPLETED
    ).first()
    if existing_purchase:
        raise HTTPException(status_code=400, detail="App already purchased")
    
    # Create purchase
    transaction_id = secrets.token_urlsafe(32)
    db_purchase = Purchase(
        user_id=current_user.id,
        app_id=purchase.app_id,
        transaction_id=transaction_id,
        amount=app.price,
        status=PurchaseStatus.COMPLETED,  # Simulated payment
        payment_method="stripe",
        completed_at=datetime.utcnow()
    )
    db.add(db_purchase)
    
    # Update app stats
    app.total_downloads += 1
    app.total_revenue += app.price
    
    # Update developer stats
    developer = db.query(DeveloperProfile).filter(DeveloperProfile.id == app.developer_id).first()
    if developer:
        developer.total_downloads += 1
        developer.total_revenue += app.price
    
    db.commit()
    db.refresh(db_purchase)
    
    # Track purchase
    analytics_tracker.track_purchase(purchase.app_id, app.price)
    
    return db_purchase

@app.get("/purchases", response_model=List[PurchaseResponse])
async def get_my_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    purchases = db.query(Purchase).filter(Purchase.user_id == current_user.id).all()
    return purchases

# ==================== Developer Endpoints ====================

@app.get("/developer/profile", response_model=DeveloperProfileResponse)
async def get_developer_profile(
    current_user: User = Depends(require_role(UserRole.DEVELOPER)),
    db: Session = Depends(get_db)
):
    profile = db.query(DeveloperProfile).filter(DeveloperProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Developer profile not found")
    return profile

@app.put("/developer/profile", response_model=DeveloperProfileResponse)
async def update_developer_profile(
    profile_update: DeveloperProfileUpdate,
    current_user: User = Depends(require_role(UserRole.DEVELOPER)),
    db: Session = Depends(get_db)
):
    profile = db.query(DeveloperProfile).filter(DeveloperProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Developer profile not found")
    
    for field, value in profile_update.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile

@app.get("/developer/apps", response_model=List[AppResponse])
async def get_developer_apps(
    current_user: User = Depends(require_role(UserRole.DEVELOPER)),
    db: Session = Depends(get_db)
):
    profile = db.query(DeveloperProfile).filter(DeveloperProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Developer profile not found")
    
    apps = db.query(App).filter(App.developer_id == profile.id).all()
    return apps

@app.get("/developer/stats", response_model=DeveloperStats)
async def get_developer_stats(
    current_user: User = Depends(require_role(UserRole.DEVELOPER)),
    db: Session = Depends(get_db)
):
    profile = db.query(DeveloperProfile).filter(DeveloperProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Developer profile not found")
    
    apps = db.query(App).filter(App.developer_id == profile.id).all()
    
    total_apps = len(apps)
    total_downloads = sum(app.total_downloads for app in apps)
    total_revenue = sum(app.total_revenue for app in apps)
    total_reviews = sum(app.total_reviews for app in apps)
    avg_rating = sum(app.average_rating for app in apps) / total_apps if total_apps > 0 else 0
    
    # Get active users (users who purchased in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(func.count(func.distinct(Purchase.user_id))).filter(
        Purchase.app_id.in_([app.id for app in apps]),
        Purchase.completed_at >= thirty_days_ago
    ).scalar()
    
    return DeveloperStats(
        total_apps=total_apps,
        total_downloads=total_downloads,
        total_revenue=total_revenue,
        average_rating=avg_rating,
        total_reviews=total_reviews,
        active_users=active_users or 0
    )

# ==================== Admin Endpoints ====================

@app.get("/admin/dashboard", response_model=DashboardStats)
async def get_admin_dashboard(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    total_apps = db.query(func.count(App.id)).scalar()
    total_downloads = db.query(func.sum(App.total_downloads)).scalar() or 0
    total_revenue = db.query(func.sum(App.total_revenue)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar()
    total_developers = db.query(func.count(DeveloperProfile.id)).scalar()
    total_reviews = db.query(func.count(Review.id)).scalar()
    avg_rating = db.query(func.avg(App.average_rating)).scalar() or 0
    
    return DashboardStats(
        total_apps=total_apps,
        total_downloads=total_downloads,
        total_revenue=float(total_revenue),
        total_users=total_users,
        total_developers=total_developers,
        total_reviews=total_reviews,
        average_rating=float(avg_rating)
    )

# ==================== Wishlist Endpoints ====================

@app.post("/wishlist", response_model=WishlistResponse)
async def add_to_wishlist(
    wishlist: WishlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if already in wishlist
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.app_id == wishlist.app_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="App already in wishlist")
    
    db_wishlist = Wishlist(user_id=current_user.id, app_id=wishlist.app_id)
    db.add(db_wishlist)
    db.commit()
    db.refresh(db_wishlist)
    return db_wishlist

@app.get("/wishlist", response_model=List[WishlistResponse])
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wishlist = db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()
    return wishlist

@app.delete("/wishlist/{app_id}")
async def remove_from_wishlist(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.app_id == app_id
    ).first()
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    
    db.delete(wishlist_item)
    db.commit()
    return {"message": "Removed from wishlist"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)