# iTechSmart Ninja - Backend API

Complete autonomous AI agent platform backend with multi-agent orchestration, task management, and deployment capabilities.

## 🚀 Features

### Core Capabilities
- **Multi-Agent System**: 5 specialized AI agents (Researcher, Coder, Writer, Analyst, Debugger)
- **Task Orchestration**: Complex multi-step task execution with progress tracking
- **Real-time Updates**: WebSocket support for live task monitoring
- **File Management**: Upload, download, and manage files
- **Deployment System**: Deploy to Vercel, Netlify, GitHub Pages, AWS S3
- **Admin Dashboard**: User management, system monitoring, AI provider configuration

### AI Providers
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)
- Google (Gemini Pro)
- DeepSeek (DeepSeek Chat, DeepSeek Coder)
- Ollama (Local models)

### Security Features
- JWT authentication with refresh tokens
- API key management with encryption
- Role-based access control (User, Admin, Premium)
- Audit logging for all actions
- Encrypted credential storage

### Agent Capabilities

#### 1. Researcher Agent
- Web search with citations
- Deep research with multiple sources
- Fact-checking and verification
- Source ranking and credibility assessment

#### 2. Coder Agent
- Code generation in 12+ languages
- Code execution in sandboxed Docker containers
- Debugging and error fixing
- Code review and security scanning
- Test generation (pytest, jest)
- Code refactoring

#### 3. Writer Agent
- README generation
- API documentation
- User guides and tutorials
- Technical reports
- Blog posts and articles

#### 4. Analyst Agent
- Descriptive statistics
- Trend analysis
- Predictive modeling
- Data visualization
- Comparative analysis

#### 5. Debugger Agent
- Error classification (13 types)
- Stack trace analysis
- Root cause identification
- Fix generation
- Performance profiling
- Memory leak detection

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (included in Docker setup)
- Redis 7+ (included in Docker setup)

## 🛠️ Installation

### Quick Start (Docker - Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd itechsmart-ninja/backend
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start services**
```bash
./start.sh
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Local Development Setup

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL and Redis**
```bash
# Using Docker
docker run -d --name ninja-postgres -e POSTGRES_PASSWORD=ninja_password -p 5432:5432 postgres:15-alpine
docker run -d --name ninja-redis -p 6379:6379 redis:7-alpine
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Initialize database**
```bash
python -m app.core.init_db
```

6. **Run development server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql://ninja:ninja_password@localhost:5432/ninja_db

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Account
ADMIN_EMAIL=admin@itechsmart.ninja
ADMIN_PASSWORD=change-this-password

# AI Providers (Optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
DEEPSEEK_API_KEY=...

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### AI Provider Configuration

AI providers can be configured in two ways:

1. **Environment Variables** (`.env` file)
2. **Admin Dashboard** (Runtime configuration with encryption)

The admin dashboard provides a secure interface for managing API keys with automatic encryption.

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

#### Get Current User
```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Task Endpoints

#### Create Task
```bash
POST /api/v1/tasks
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Research AI Trends",
  "description": "Research the latest AI trends in 2024",
  "task_type": "research",
  "parameters": {
    "query": "AI trends 2024",
    "num_sources": 5
  }
}
```

#### List Tasks
```bash
GET /api/v1/tasks?status=completed&limit=10
Authorization: Bearer <access_token>
```

#### Get Task Details
```bash
GET /api/v1/tasks/{task_id}
Authorization: Bearer <access_token>
```

#### Cancel Task
```bash
POST /api/v1/tasks/{task_id}/cancel
Authorization: Bearer <access_token>
```

### Agent Endpoints

#### List Available Agents
```bash
GET /api/v1/agents
Authorization: Bearer <access_token>
```

#### Get Agent Capabilities
```bash
GET /api/v1/agents/{agent_type}/capabilities
Authorization: Bearer <access_token>
```

### File Endpoints

#### Upload File
```bash
POST /api/v1/files/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file=@/path/to/file.txt
```

#### List Files
```bash
GET /api/v1/files
Authorization: Bearer <access_token>
```

#### Download File
```bash
GET /api/v1/files/download/{user_id}/{filename}
Authorization: Bearer <access_token>
```

### Deployment Endpoints

#### Create Deployment
```bash
POST /api/v1/deployments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "my-website",
  "platform": "vercel",
  "source_path": "website-folder",
  "config": {
    "vercel_token": "your-token"
  }
}
```

### Admin Endpoints (Admin Only)

#### List Users
```bash
GET /api/v1/admin/users
Authorization: Bearer <admin_access_token>
```

#### Get System Stats
```bash
GET /api/v1/admin/stats
Authorization: Bearer <admin_access_token>
```

#### Update AI Provider Settings
```bash
POST /api/v1/admin/settings/ai-providers
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "openai_api_key": "sk-...",
  "default_provider": "openai",
  "default_model": "gpt-4"
}
```

## 🔌 WebSocket API

Connect to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{user_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};

// Message format:
// {
//   "type": "task_update" | "agent_status" | "notification",
//   "data": {...}
// }
```

## 🧪 Testing

### Run Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_auth.py -v
```

## 🐳 Docker Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Restart Service
```bash
docker-compose restart backend
```

### Rebuild Containers
```bash
docker-compose up -d --build
```

### Remove All Data
```bash
docker-compose down -v
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Prometheus Metrics
```bash
curl http://localhost:8000/metrics
```

### Database Status
```bash
docker-compose exec postgres pg_isready -U ninja
```

### Redis Status
```bash
docker-compose exec redis redis-cli ping
```

## 🔒 Security Best Practices

1. **Change Default Credentials**: Update admin password after first login
2. **Use Strong Secret Key**: Generate a secure SECRET_KEY (min 32 characters)
3. **Enable HTTPS**: Use reverse proxy (nginx/traefik) with SSL certificates
4. **Rotate API Keys**: Regularly rotate API keys and tokens
5. **Monitor Audit Logs**: Review audit logs for suspicious activity
6. **Limit CORS Origins**: Only allow trusted frontend domains
7. **Use Environment Variables**: Never commit secrets to version control

## 🚀 Production Deployment

### Using Docker Compose

1. **Update environment variables**
```bash
# Set production values in .env
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<generate-secure-key>
```

2. **Use production database**
```bash
DATABASE_URL=postgresql://user:pass@prod-db-host:5432/ninja_db
```

3. **Enable SSL/TLS**
```bash
# Use nginx or traefik as reverse proxy
# Configure SSL certificates (Let's Encrypt)
```

4. **Scale services**
```bash
docker-compose up -d --scale celery-worker=3
```

### Using Kubernetes

See `infrastructure/kubernetes/` for Kubernetes manifests (coming in Phase 3).

## 📝 API Rate Limits

Default rate limits:
- 60 requests per minute per user
- 1000 requests per hour per user

Configure in `.env`:
```bash
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U ninja -d ninja_db -c "SELECT 1"
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

### Docker Socket Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

## 📖 Additional Resources

- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- [ReDoc Documentation](http://localhost:8000/redoc) - Alternative API docs
- [Project Wiki](../docs/) - Detailed guides and tutorials

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Email: support@itechsmart.ninja
- Issues: GitHub Issues
- Documentation: [docs/](../docs/)

## 🎯 Roadmap

- [x] Phase 1: Core backend API
- [x] Phase 2: Multi-agent system
- [ ] Phase 3: Frontend dashboard
- [ ] Phase 4: Mobile app
- [ ] Phase 5: Browser extension
- [ ] Phase 6: CLI tool

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: ✅ Production Ready