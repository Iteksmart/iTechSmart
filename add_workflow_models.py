import re

# Read the database models file
with open('itechsmart-ninja/backend/app/models/database.py', 'r') as f:
    content = f.read()

# Add Workflow models before VideoGeneration
workflow_models = '''

class Workflow(Base):
    """Workflow definitions"""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Workflow details
    workflow_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    definition = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")


class WorkflowExecution(Base):
    """Workflow execution history"""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workflow_id = Column(String, nullable=False)
    
    # Execution details
    execution_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False)  # pending, running, completed, failed
    context = Column(JSON)
    logs = Column(JSON)
    error = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
'''

# Insert before VideoGeneration
if 'class VideoGeneration(Base):' in content:
    content = content.replace(
        'class VideoGeneration(Base):',
        workflow_models + '\n\nclass VideoGeneration(Base):'
    )
    print("Added Workflow models to database.py")
else:
    print("Warning: Could not find VideoGeneration class")

# Write back
with open('itechsmart-ninja/backend/app/models/database.py', 'w') as f:
    f.write(content)

print("Workflow models added successfully")