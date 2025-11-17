# iTechSmart Copilot - AI Assistant Platform

**Version:** 1.0.0  
**Market Value:** $800K - $1.5M  
**Status:** Production Ready ✅

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Frontend Pages](#frontend-pages)
- [Database Schema](#database-schema)
- [AI Integration](#ai-integration)
- [Configuration](#configuration)
- [Security](#security)
- [Deployment](#deployment)
- [License](#license)

---

## 🎯 Overview

iTechSmart Copilot is a comprehensive AI assistant platform that enables users to interact with multiple AI models, manage conversations, create prompt templates, build knowledge bases, and generate code. The platform supports integration with OpenAI, Anthropic, Google AI, and other leading AI providers.

### Key Capabilities

- **Multi-Model AI Integration**: OpenAI GPT-4/3.5, Anthropic Claude, Google Gemini, Cohere
- **Conversation Management**: Create, manage, and organize AI conversations
- **Prompt Templates**: Build and share reusable prompt templates
- **Knowledge Base**: Upload documents and create searchable knowledge bases
- **Code Generation**: Generate, save, and manage code snippets
- **Real-time Analytics**: Track usage, costs, and performance metrics
- **API Access**: RESTful API with JWT authentication

---

## ✨ Features

### 1. Agent Monitoring with AI Insights 🆕
- Real-time agent status monitoring
- AI-powered performance analysis
- Intelligent recommendations and insights
- System health scoring
- Proactive issue detection
- Automated troubleshooting suggestions

### 2. Intelligent Chat Interface
- Multi-turn conversations with context awareness
- Support for multiple AI models
- Real-time streaming responses
- Message history and search
- Conversation branching and forking

### 2. Prompt Template Library
- Create custom prompt templates
- Variable substitution
- Category organization
- Public/private sharing
- Usage tracking and analytics

### 3. Knowledge Base Management
- Document upload and processing (PDF, DOCX, TXT, MD)
- Vector embeddings for semantic search
- Multiple knowledge base support
- Document chunking and indexing
- Context-aware retrieval

### 4. Code Generation & Management
- Multi-language code generation
- Syntax highlighting
- Code snippet library
- Favorite and tag system
- Export and share functionality

### 5. AI Model Configuration
- Multiple AI provider support
- Custom model parameters
- Cost tracking per model
- Performance monitoring
- Default model selection

### 6. Analytics & Reporting
- Usage statistics dashboard
- Cost breakdown by model
- Token consumption tracking
- Conversation analytics
- Export capabilities

---

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **ORM**: SQLAlchemy 2.0
- **AI Libraries**: openai, anthropic, google-generativeai
- **Vector DB**: ChromaDB
- **Document Processing**: pypdf2, python-docx

### Frontend
- **Framework**: React 18.2
- **Language**: TypeScript 5.3
- **Routing**: React Router 6.20
- **Styling**: Tailwind CSS 3.3
- **Charts**: Recharts 2.10
- **Icons**: Lucide React 0.294
- **HTTP Client**: Axios 1.6
- **Markdown**: react-markdown
- **Code Highlighting**: react-syntax-highlighter

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 15 Alpine
- **Cache**: Redis 7 Alpine
- **Web Server**: Uvicorn (ASGI)
- **Build Tool**: Vite 5.0

---

## 🏗 Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │Dashboard │   Chat   │ Prompts  │Knowledge │  Models  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Authentication │ Conversation Mgmt │ AI Integration  │  │
│  │  Prompt Engine  │ Knowledge Base    │ Code Generator  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        ┌──────────────┐        ┌──────────────┐
        │  PostgreSQL  │        │    Redis     │
        │   Database   │        │    Cache     │
        └──────────────┘        └──────────────┘
                │
                ▼
        ┌──────────────────────────────────┐
        │   AI Providers                   │
        │  • OpenAI    • Anthropic         │
        │  • Google AI • Cohere            │
        └──────────────────────────────────┘
```

### Database Schema

**Core Tables:**
- `users` - User accounts and authentication
- `ai_models` - AI model configurations
- `conversations` - Conversation management
- `messages` - Chat messages
- `prompt_templates` - Prompt templates
- `documents` - Document storage
- `document_chunks` - Document chunks for vector search
- `knowledge_bases` - Knowledge base management
- `code_snippets` - Code snippet library
- `api_keys` - AI provider API keys
- `usage_statistics` - Usage tracking
- `feedback` - User feedback
- `audit_logs` - System audit trail

---

## 🚀 Getting Started

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd itechsmart-copilot
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

4. **Default credentials**
- Email: admin@itechsmart.dev
- Password: admin123

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://copilot_user:copilot_pass@localhost:5432/copilot_db"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
echo "VITE_API_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

---

## 📚 API Documentation

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=username&password=password123
```

### Chat Operations

#### Send Message
```http
POST /chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "conversation_id": 1,
  "message": "Hello, can you help me?",
  "model_id": 1,
  "temperature": 0.7,
  "max_tokens": 1000
}
```

#### Get Conversations
```http
GET /conversations?skip=0&limit=100
Authorization: Bearer <token>
```

### Prompt Templates

#### Create Prompt
```http
POST /prompts
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Code Review",
  "description": "Review code for improvements",
  "template": "Review this code: {code}",
  "category": "Development"
}
```

### Knowledge Base

#### Create Knowledge Base
```http
POST /knowledge-bases
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Technical Docs",
  "description": "API documentation and guides"
}
```

#### Upload Document
```http
POST /documents
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "API Documentation",
  "content": "...",
  "document_type": "pdf"
}
```

---

## 🖥 Frontend Pages

### 1. Dashboard (`/`)
- Overview of AI assistant usage
- Key metrics (conversations, messages, tokens, cost)
- Token usage chart (last 7 days)
- Model usage distribution
- Cost breakdown
- Recent conversations
- Quick actions

### 2. Chat (`/chat`)
- Conversation sidebar
- Real-time chat interface
- Message history
- AI model selection
- Copy, like, dislike actions
- New conversation creation

### 3. Prompts (`/prompts`)
- Prompt template library
- Category filtering
- Create/edit/delete templates
- Public/private sharing
- Usage statistics
- Copy to clipboard

### 4. Knowledge (`/knowledge`)
- Knowledge base management
- Document upload
- Search functionality
- Document list
- File type indicators
- Size and date information

### 5. Models (`/models`)
- AI model configuration
- Provider filtering
- Model parameters
- Cost information
- Active/inactive status
- Model comparison table

### 6. Settings (`/settings`)
- Profile management
- API key configuration
- Notification preferences
- Security settings
- User preferences
- Advanced options

---

## 🗄 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    model_id INTEGER NOT NULL REFERENCES ai_models(id),
    title VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    system_prompt TEXT,
    context_window INTEGER DEFAULT 10,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    tokens INTEGER DEFAULT 0,
    cost DECIMAL(10, 4) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🤖 AI Integration

### Supported Providers

1. **OpenAI**
   - GPT-4
   - GPT-3.5 Turbo
   - Custom fine-tuned models

2. **Anthropic**
   - Claude 2
   - Claude Instant

3. **Google AI**
   - Gemini Pro
   - PaLM 2

4. **Cohere**
   - Command
   - Command Light

### Configuration

Add your API keys in the Settings page or via environment variables:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
COHERE_API_KEY=...
```

---

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://copilot_user:copilot_pass@localhost:5432/copilot_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Provider Keys (Optional - can be set via UI)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

---

## 🔒 Security

### Authentication
- JWT-based authentication with configurable expiration
- Bcrypt password hashing with salt rounds
- Secure session management
- API key encryption

### Data Protection
- Encrypted API key storage
- HTTPS enforcement in production
- CORS configuration
- Rate limiting
- Input validation

### Best Practices
- Regular security audits
- Dependency vulnerability scanning
- SQL injection prevention
- XSS protection
- Secure API key management

---

## 🚢 Deployment

### Docker Deployment

1. **Build and start services**
```bash
docker-compose up -d --build
```

2. **Check service health**
```bash
docker-compose ps
docker-compose logs -f
```

3. **Stop services**
```bash
docker-compose down
```

### Production Deployment

1. **Update environment variables**
```bash
# Set strong SECRET_KEY
# Configure production database
# Add AI provider API keys
# Enable HTTPS
```

2. **Use production configuration**
```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
    restart: always
```

3. **Set up reverse proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name copilot.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Performance

### Optimization Features
- Database connection pooling
- Redis caching for frequently accessed data
- Indexed database queries
- Lazy loading in frontend
- Code splitting and minification

### Scalability
- Horizontal scaling with load balancer
- Database read replicas
- Redis cluster for distributed caching
- Microservices architecture ready
- API rate limiting

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=.
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

---

## 📈 Monitoring

### Health Checks
- `/health` - API health status
- Database connection monitoring
- Redis connection monitoring
- AI provider availability

### Logging
- Structured logging with timestamps
- Error tracking and alerting
- Audit trail for all operations
- Performance metrics collection

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 📞 Support

For support and questions:
- Email: support@itechsmart.dev
- Documentation: https://docs.itechsmart.dev
- Issues: GitHub Issues

---

**Built with ❤️ by the iTechSmart Inc**

*iTechSmart Copilot - Your AI Assistant Platform*
## 🤖 Agent Integration

This product integrates with the iTechSmart Agent monitoring system through the License Server. The agent system provides:

- Real-time system monitoring
- Performance metrics collection
- Security status tracking
- Automated alerting

### Configuration

Set the License Server URL in your environment:

```bash
LICENSE_SERVER_URL=http://localhost:3000
```

The product will automatically connect to the License Server to access agent data and monitoring capabilities.

