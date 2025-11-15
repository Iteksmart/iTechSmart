from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "markdown"
    CODE = "code"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI Model Schemas
class AIModelBase(BaseModel):
    name: str
    provider: AIProvider
    model_id: str
    description: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class AIModelCreate(AIModelBase):
    pass

class AIModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class AIModelResponse(AIModelBase):
    id: int
    is_active: bool
    is_default: bool
    cost_per_1k_tokens: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Conversation Schemas
class ConversationBase(BaseModel):
    title: str
    model_id: int
    system_prompt: Optional[str] = None
    context_window: int = 10

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None
    system_prompt: Optional[str] = None
    context_window: Optional[int] = None

class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    status: ConversationStatus
    total_tokens: int
    total_cost: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    role: MessageRole
    content: str

class MessageCreate(MessageBase):
    conversation_id: int

class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    tokens: int
    cost: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat Request/Response
class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str
    model_id: Optional[int] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False

class ChatResponse(BaseModel):
    conversation_id: int
    message: MessageResponse
    response: MessageResponse
    total_tokens: int
    cost: float

# Prompt Template Schemas
class PromptTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template: str
    variables: Optional[List[str]] = []
    category: Optional[str] = None

class PromptTemplateCreate(PromptTemplateBase):
    pass

class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template: Optional[str] = None
    variables: Optional[List[str]] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None

class PromptTemplateResponse(PromptTemplateBase):
    id: int
    user_id: int
    is_public: bool
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Document Schemas
class DocumentBase(BaseModel):
    title: str
    document_type: DocumentType

class DocumentCreate(DocumentBase):
    content: str

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    file_size: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Knowledge Base Schemas
class KnowledgeBaseBase(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class KnowledgeBaseResponse(KnowledgeBaseBase):
    id: int
    user_id: int
    collection_name: str
    document_count: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Code Snippet Schemas
class CodeSnippetBase(BaseModel):
    title: str
    code: str
    language: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []

class CodeSnippetCreate(CodeSnippetBase):
    conversation_id: Optional[int] = None

class CodeSnippetUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None

class CodeSnippetResponse(CodeSnippetBase):
    id: int
    user_id: int
    conversation_id: Optional[int]
    is_favorite: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# API Key Schemas
class APIKeyCreate(BaseModel):
    provider: AIProvider
    key_name: str
    api_key: str

class APIKeyResponse(BaseModel):
    id: int
    user_id: int
    provider: AIProvider
    key_name: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Usage Statistics Schemas
class UsageStatisticResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    provider: AIProvider
    model_name: str
    total_requests: int
    total_tokens: int
    total_cost: float
    
    class Config:
        from_attributes = True

# Dashboard Statistics
class DashboardStats(BaseModel):
    total_conversations: int
    total_messages: int
    total_tokens: int
    total_cost: float
    active_conversations: int
    favorite_snippets: int
    documents_count: int
    prompts_count: int

# Feedback Schemas
class FeedbackCreate(BaseModel):
    message_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    message_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Search Schemas
class SearchRequest(BaseModel):
    query: str
    knowledge_base_id: Optional[int] = None
    limit: int = 5

class SearchResult(BaseModel):
    content: str
    score: float
    metadata: Dict[str, Any]