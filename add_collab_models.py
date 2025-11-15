import re

# Read the database models file
with open('itechsmart-ninja/backend/app/models/database.py', 'r') as f:
    content = f.read()

# Add Collaboration models before VideoGeneration
collab_models = '''

class Team(Base):
    """Team for collaboration"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan = Column(String, default="free")  # free, pro, enterprise
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User")


class TeamMember(Base):
    """Team membership"""
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # owner, admin, member, viewer
    status = Column(String, default="active")  # active, inactive
    
    # Timestamp
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


class Workspace(Base):
    """Team workspace"""
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, unique=True, index=True, nullable=False)
    team_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")


class Comment(Base):
    """Comments on resources"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String, nullable=False)  # code, file, task, workflow
    resource_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    team_id = Column(Integer)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
'''

# Insert before VideoGeneration
if 'class VideoGeneration(Base):' in content:
    content = content.replace(
        'class VideoGeneration(Base):',
        collab_models + '\n\nclass VideoGeneration(Base):'
    )
    print("Added Collaboration models to database.py")
else:
    print("Warning: Could not find VideoGeneration class")

# Write back
with open('itechsmart-ninja/backend/app/models/database.py', 'w') as f:
    f.write(content)

print("Collaboration models added successfully")