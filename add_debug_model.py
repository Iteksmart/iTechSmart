import re

# Read the database models file
with open("itechsmart-ninja/backend/app/models/database.py", "r") as f:
    content = f.read()

# Add DebugSession model before the last class
debug_model = '''

class DebugSession(Base):
    """Debug session tracking"""
    __tablename__ = "debug_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session details
    session_type = Column(String, nullable=False)  # breakpoint, profile, analysis
    data = Column(JSON)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
'''

# Insert before the last class (VideoGeneration)
content = content.replace(
    "class VideoGeneration(Base):", debug_model + "\n\nclass VideoGeneration(Base):"
)

# Write back
with open("itechsmart-ninja/backend/app/models/database.py", "w") as f:
    f.write(content)

print("Added DebugSession model to database.py")
