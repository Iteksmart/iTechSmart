"""
Database initialization script
Creates initial admin user and default settings
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.database import User, UserSettings, Template
from app.core.security import get_password_hash
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Initialize database with default data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        
        if not admin:
            # Create admin user
            admin = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info(f"Admin user created: {settings.ADMIN_EMAIL}")
            
            # Create default settings for admin
            admin_settings = UserSettings(
                user_id=admin.id,
                theme="dark",
                language="en",
                notifications_enabled=True
            )
            db.add(admin_settings)
            db.commit()
            logger.info("Admin settings created")
        else:
            logger.info("Admin user already exists")
        
        # Create default templates if they don't exist
        template_count = db.query(Template).count()
        if template_count == 0:
            default_templates = [
                Template(
                    name="Web Research",
                    description="Research a topic using web search and multiple sources",
                    task_type="research",
                    parameters={
                        "num_sources": 5,
                        "include_citations": True
                    },
                    is_public=True
                ),
                Template(
                    name="Code Generation",
                    description="Generate code from description",
                    task_type="code",
                    parameters={
                        "language": "python",
                        "include_tests": True
                    },
                    is_public=True
                ),
                Template(
                    name="Data Analysis",
                    description="Analyze dataset and generate insights",
                    task_type="analysis",
                    parameters={
                        "analysis_type": "descriptive",
                        "create_visualizations": True
                    },
                    is_public=True
                ),
                Template(
                    name="Documentation Writer",
                    description="Generate comprehensive documentation",
                    task_type="documentation",
                    parameters={
                        "doc_type": "readme",
                        "include_examples": True
                    },
                    is_public=True
                ),
                Template(
                    name="Bug Debugger",
                    description="Debug and fix code errors",
                    task_type="debug",
                    parameters={
                        "include_fix": True,
                        "explain_root_cause": True
                    },
                    is_public=True
                )
            ]
            
            for template in default_templates:
                db.add(template)
            
            db.commit()
            logger.info(f"Created {len(default_templates)} default templates")
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()