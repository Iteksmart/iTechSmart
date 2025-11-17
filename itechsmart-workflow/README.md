# iTechSmart Workflow - Business Process Automation Platform

A comprehensive workflow automation platform for orchestrating business processes, integrating systems, and automating repetitive tasks.

## 🚀 Features

### Core Capabilities
- **Visual Workflow Builder** - Create workflows with drag-and-drop interface
- **Multi-Trigger Support** - Manual, scheduled, webhook, event, and API triggers
- **Task Execution Engine** - Execute tasks with retry logic and error handling
- **Real-time Monitoring** - Track workflow executions in real-time
- **Template Library** - Pre-built workflow templates for common use cases
- **Integration Hub** - Connect to external services (Slack, Email, AWS, etc.)
- **Scheduling** - Cron-based workflow scheduling
- **Analytics Dashboard** - Comprehensive execution analytics and insights

### Technical Features
- **RESTful API** - 30+ endpoints for complete workflow management
- **JWT Authentication** - Secure token-based authentication
- **Role-based Access** - User permissions and access control
- **Audit Logging** - Complete audit trail of all actions
- **Scalable Architecture** - Microservices-based design
- **Docker Support** - Containerized deployment
- **Database Persistence** - PostgreSQL with optimized indexes
- **Caching Layer** - Redis for performance optimization
- **Message Queue** - RabbitMQ for async task processing

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

## 🏃 Quick Start

### 1. Clone and Navigate
```bash
cd itechsmart-workflow
```

### 2. Start Services
```bash
./start.sh
```

This will:
- Build all Docker containers
- Initialize the PostgreSQL database
- Start all services (Backend, Frontend, PostgreSQL, Redis, RabbitMQ)
- Run health checks

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672

### 4. Login

Default credentials:
- **Username**: `admin`
- **Password**: `password`

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- PostgreSQL 15
- Redis 7
- RabbitMQ 3
- JWT Authentication
- Celery for async tasks

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- Recharts for visualizations
- React Router
- Axios for API calls

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL for data persistence
- Redis for caching
- RabbitMQ for message queuing

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│                    Port: 5173                            │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                   │
│                    Port: 8000                            │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  PostgreSQL  │   │    Redis     │   │  RabbitMQ    │
│  Port: 5432  │   │  Port: 6379  │   │  Port: 5672  │
└──────────────┘   └──────────────┘   └──────────────┘
```

## 📊 Database Schema

### Core Tables
- **users** - User accounts and authentication
- **workflows** - Workflow definitions and metadata
- **executions** - Workflow execution instances
- **task_executions** - Individual task executions
- **triggers** - Workflow trigger configurations
- **workflow_variables** - Workflow-specific variables
- **integrations** - External service connections
- **templates** - Pre-built workflow templates
- **execution_logs** - Detailed execution logs
- **schedules** - Cron-based schedules
- **audit_logs** - System audit trail

## 🔌 API Endpoints

### Authentication
- `POST /token` - Login and get JWT token
- `POST /users/register` - Register new user
- `GET /users/me` - Get current user info

### Workflows
- `GET /workflows` - List workflows
- `POST /workflows` - Create workflow
- `GET /workflows/{id}` - Get workflow details
- `PUT /workflows/{id}` - Update workflow
- `DELETE /workflows/{id}` - Delete workflow

### Executions
- `GET /executions` - List executions
- `POST /executions` - Trigger workflow execution
- `GET /executions/{id}` - Get execution details
- `GET /executions/{id}/tasks` - Get execution tasks
- `GET /executions/{id}/logs` - Get execution logs

### Triggers
- `GET /triggers` - List triggers
- `POST /triggers` - Create trigger
- `PUT /triggers/{id}` - Update trigger
- `DELETE /triggers/{id}` - Delete trigger

### Integrations
- `GET /integrations` - List integrations
- `POST /integrations` - Create integration
- `PUT /integrations/{id}` - Update integration
- `DELETE /integrations/{id}` - Delete integration

### Templates
- `GET /templates` - List templates
- `GET /templates/{id}` - Get template details

### Analytics
- `GET /analytics/overview` - Get analytics overview

## 🎨 Frontend Pages

1. **Dashboard** - Overview with metrics and charts
2. **Workflows** - Workflow management interface
3. **Executions** - Execution history and monitoring
4. **Templates** - Pre-built workflow templates
5. **Integrations** - External service connections
6. **Settings** - User and system settings

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://workflow_user:workflow_pass@postgres:5432/itechsmart_workflow
REDIS_URL=redis://redis:6379
RABBITMQ_URL=amqp://workflow:workflow_pass@rabbitmq:5672
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📦 Docker Commands

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

### Restart Services
```bash
docker-compose restart
```

### Rebuild Containers
```bash
docker-compose up -d --build
```

### Access Database
```bash
docker-compose exec postgres psql -U workflow_user -d itechsmart_workflow
```

## 🧪 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## 📈 Performance Optimization

- **Database Indexing** - 20+ optimized indexes
- **Connection Pooling** - PostgreSQL connection pool (10-20 connections)
- **Redis Caching** - Cache frequently accessed data
- **Async Processing** - RabbitMQ for background tasks
- **Query Optimization** - Efficient SQL queries with joins

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic schemas)
- Audit logging for all actions

## 📝 Sample Data

The database is initialized with sample data including:
- 3 users (admin, john, jane)
- 6 workflows across different categories
- 7 executions with various statuses
- 5 task executions
- 4 triggers
- 4 integrations
- 6 workflow templates

## 🐛 Troubleshooting

### Services Not Starting
```bash
# Check Docker status
docker ps

# View service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### Database Connection Issues
```bash
# Check PostgreSQL health
docker-compose exec postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up -d
```

### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "5174:5173"  # Change frontend port
  - "8001:8000"  # Change backend port
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Docker logs
3. Verify all services are healthy
4. Check database connectivity

## 📄 License

Copyright © 2025 iTechSmart. All rights reserved.

## 🎯 Roadmap

- [ ] Visual workflow builder with drag-and-drop
- [ ] Advanced scheduling with timezone support
- [ ] Workflow versioning and rollback
- [ ] Real-time collaboration
- [ ] Advanced analytics and reporting
- [ ] Mobile application
- [ ] Marketplace for workflow templates
- [ ] AI-powered workflow suggestions

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: January 2025
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

