# 🚀 iTechSmart ImpactOS - Quick Start Guide

## ⚡ Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Step 1: Clone & Setup

```bash
# Clone repository
git clone https://github.com/itechsmart/impactos.git
cd itechsmart-impactos

# Copy environment file
cp .env.example .env
```

### Step 2: Configure Environment

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/impactos_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here

# AI Models (Optional - for AI features)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_AI_API_KEY=your-google-key
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Setup Database

```bash
# Create database
createdb impactos_db

# Run migrations
alembic upgrade head
```

### Step 5: Start Services

```bash
# Start Redis
redis-server

# Start backend (in another terminal)
cd backend
uvicorn app.main:app --reload
```

### Step 6: Access Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health

---

## 🎯 First Steps

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "full_name": "Admin User",
    "password": "SecurePass123!"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Get Current User

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🐳 Docker Quick Start

```bash
# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 📚 Next Steps

1. **Explore API**: Visit http://localhost:8000/api/v1/docs
2. **Read Documentation**: Check `docs/` folder
3. **Create Organization**: Use the API to create your first organization
4. **Generate Report**: Try the AI-powered report generation
5. **Explore MCP Tools**: Test the 8 built-in tools

---

## 🆘 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string in .env
DATABASE_URL=postgresql://user:pass@localhost:5432/impactos_db
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Need Help?

- **Documentation**: See `docs/` folder
- **API Docs**: http://localhost:8000/api/v1/docs
- **Issues**: GitHub Issues
- **Email**: support@itechsmart.dev

---

**🎉 You're all set! Start building amazing impact reports!**