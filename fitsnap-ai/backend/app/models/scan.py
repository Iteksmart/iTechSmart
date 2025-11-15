"""
Outfit Scan Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class OutfitScan(Base):
    __tablename__ = "outfit_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Image
    image_path = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    
    # Analysis Results
    style_score = Column(Float, nullable=False)
    color_harmony = Column(Float, nullable=False)
    trend_match = Column(Float, nullable=False)
    overall_rating = Column(Float, nullable=False)
    
    # Detected Information
    detected_items = Column(Text, nullable=True)  # JSON string
    colors = Column(Text, nullable=True)  # JSON string
    style_category = Column(String, nullable=True)
    
    # Feedback
    feedback = Column(Text, nullable=True)  # JSON string
    suggestions = Column(Text, nullable=True)  # JSON string
    
    # Hair & Makeup Analysis
    hair_makeup_analysis = Column(Text, nullable=True)
    hair_makeup_score = Column(Float, nullable=True)
    
    # Privacy
    is_deleted = Column(Boolean, default=False)
    auto_delete_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scans")
    saved_look = relationship("SavedLook", back_populates="scan", uselist=False)


class SavedLook(Base):
    __tablename__ = "saved_looks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scan_id = Column(Integer, ForeignKey("outfit_scans.id"), nullable=False)
    
    # User Notes
    title = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # JSON string
    
    # Favorites
    is_favorite = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_looks")
    scan = relationship("OutfitScan", back_populates="saved_look")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scan_id = Column(Integer, ForeignKey("outfit_scans.id"), nullable=True)
    
    # Message
    role = Column(String, nullable=False)  # "user" or "assistant"
    message = Column(Text, nullable=False)
    
    # Context
    context = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_history")