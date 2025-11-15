# iTechSmart Ninja - Quick Start Guide

Get up and running with iTechSmart Ninja in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- 4GB RAM minimum
- 10GB free disk space

## Installation

### 1. Navigate to Backend Directory
```bash
cd itechsmart-ninja/backend
```

### 2. Start the Application
```bash
./start.sh
```

That's it! The script will:
- Create necessary directories
- Copy environment configuration
- Start all Docker services
- Initialize the database
- Create admin user

## Access the Application

### API Endpoints
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)
- **Health Check**: http://localhost:8000/health

### Default Admin Credentials
```
Email: admin@itechsmart.ninja
Password: admin123
```

⚠️ **IMPORTANT**: Change the admin password after first login!

## Quick Test

### 1. Get Access Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@itechsmart.ninja&password=admin123"
```

Save the `access_token` from the response.

### 2. Create a Task
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Research Task",
    "description": "Research AI trends in 2024",
    "task_type": "research",
    "parameters": {
      "query": "AI trends 2024",
      "num_sources": 3
    }
  }'
```

### 3. Check Task Status
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Common Commands

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
./stop.sh
```

### Restart Services
```bash
docker-compose restart
```

### Check Service Status
```bash
docker-compose ps
```

## Next Steps

1. **Explore API Documentation**: Visit http://localhost:8000/docs
2. **Create API Keys**: Use the `/api/v1/auth/api-keys` endpoint
3. **Configure AI Providers**: Add your API keys via admin endpoints
4. **Try Different Agents**: Test Researcher, Coder, Writer, Analyst, Debugger
5. **Upload Files**: Use the `/api/v1/files/upload` endpoint
6. **Deploy Projects**: Try deploying to Vercel, Netlify, or S3

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
# Or stop the conflicting service
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
```bash
# Restart PostgreSQL
docker-compose restart postgres
```

### Permission Denied (Docker Socket)
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

## Configuration

### Add AI Provider API Keys

Edit `.env` file:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

Or configure via API:
```bash
curl -X POST "http://localhost:8000/api/v1/admin/settings/ai-providers" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "openai_api_key": "sk-...",
    "default_provider": "openai",
    "default_model": "gpt-4"
  }'
```

## Support

- **Documentation**: See [README.md](backend/README.md)
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues

## What's Next?

- **Phase 3**: Frontend dashboard (React + Material-UI)
- **Phase 4**: Kubernetes & Terraform
- **Phase 5**: Mobile app (React Native)
- **Phase 6**: CLI tool
- **Phase 7**: SDKs (Python, JS, Go, Java)

---

**Status**: ✅ Backend Complete - Ready for Frontend Development  
**Version**: 1.0.0  
**Last Updated**: 2024