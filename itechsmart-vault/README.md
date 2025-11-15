# iTechSmart Vault - Secrets Management Platform

A comprehensive enterprise-grade secrets management platform for securely storing, managing, and accessing sensitive data like API keys, passwords, certificates, and encryption keys.

## 🔐 Features

### Core Capabilities
- **Encrypted Secret Storage** - AES-256-GCM encryption for all secrets
- **Secret Versioning** - Complete version history with rollback capability
- **Access Control Policies** - Fine-grained permission management
- **Vault Organization** - Organize secrets into logical vaults
- **Secret Rotation** - Manual and automatic secret rotation
- **Audit Logging** - Complete audit trail of all operations
- **Secret Sharing** - Temporary secret sharing with expiration
- **API Key Management** - Generate and manage API access keys
- **Multi-Factor Authentication** - Enhanced security with MFA support

### Technical Features
- **RESTful API** - 25+ endpoints for complete secret management
- **JWT Authentication** - Secure token-based authentication
- **Encryption at Rest** - All secrets encrypted in database
- **Role-based Access** - User permissions and access control
- **Real-time Analytics** - Secret usage and access statistics
- **Docker Support** - Containerized deployment
- **PostgreSQL Backend** - Reliable data persistence
- **Redis Caching** - Performance optimization

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

## 🏃 Quick Start

### 1. Navigate to Directory
```bash
cd itechsmart-vault
```

### 2. Start Services
```bash
./start.sh
```

This will:
- Build all Docker containers
- Initialize the PostgreSQL database
- Start all services (Backend, Frontend, PostgreSQL, Redis)
- Run health checks

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

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
- Cryptography library (AES-256-GCM)
- JWT Authentication

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
│              Encryption/Decryption Layer                 │
│                    Port: 8000                            │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        ┌──────────────┐       ┌──────────────┐
        │  PostgreSQL  │       │    Redis     │
        │  Port: 5432  │       │  Port: 6379  │
        └──────────────┘       └──────────────┘
```

## 📊 Database Schema

### Core Tables
- **users** - User accounts and authentication
- **vaults** - Vault containers for organizing secrets
- **secrets** - Encrypted secret storage
- **secret_versions** - Secret version history
- **policies** - Access control policies
- **access_grants** - User access permissions
- **audit_logs** - Complete audit trail
- **secret_rotations** - Rotation history
- **secret_shares** - Temporary secret sharing
- **api_keys** - API access keys
- **encryption_keys** - Encryption key management

## 🔌 API Endpoints

### Authentication
- `POST /token` - Login and get JWT token
- `POST /users/register` - Register new user
- `GET /users/me` - Get current user info

### Vaults
- `GET /vaults` - List vaults
- `POST /vaults` - Create vault
- `GET /vaults/{id}` - Get vault details
- `PUT /vaults/{id}` - Update vault
- `DELETE /vaults/{id}` - Delete vault

### Secrets
- `GET /secrets` - List secrets
- `POST /secrets` - Create secret
- `GET /secrets/{id}` - Get secret (decrypted)
- `PUT /secrets/{id}` - Update secret
- `DELETE /secrets/{id}` - Delete secret
- `POST /secrets/{id}/rotate` - Rotate secret
- `GET /secrets/{id}/versions` - Get version history

### Analytics
- `GET /analytics/overview` - Get analytics overview
- `GET /audit-logs` - Get audit logs

## 🎨 Frontend Pages

1. **Dashboard** - Overview with metrics and charts
2. **Secrets** - Secret management interface
3. **Vaults** - Vault organization
4. **Policies** - Access control policies
5. **Audit** - Audit log viewer
6. **Settings** - User and system settings

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://vault_user:vault_pass@postgres:5432/itechsmart_vault
REDIS_URL=redis://redis:6379
VAULT_MASTER_KEY=your-master-encryption-key
SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Master Encryption Key

⚠️ **IMPORTANT**: Change the `VAULT_MASTER_KEY` in production!

Generate a new key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
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
docker-compose exec postgres psql -U vault_user -d itechsmart_vault
```

## 🔒 Security Features

### Encryption
- **AES-256-GCM** encryption for all secrets
- **Encryption at rest** in database
- **Master key** protection
- **Key derivation** from passwords

### Authentication
- **JWT tokens** with expiration
- **Password hashing** with bcrypt
- **MFA support** (optional)
- **API key** authentication

### Access Control
- **Role-based** permissions
- **Policy-based** access control
- **Temporary** access grants
- **Audit logging** for all operations

### Best Practices
- Change default credentials immediately
- Use strong master encryption key
- Enable MFA for admin accounts
- Regularly rotate secrets
- Monitor audit logs
- Use HTTPS in production

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

## 📈 Performance Optimization

- **Database Indexing** - 15+ optimized indexes
- **Connection Pooling** - PostgreSQL connection pool
- **Redis Caching** - Cache frequently accessed data
- **Async Processing** - FastAPI async endpoints
- **Query Optimization** - Efficient SQL queries

## 📝 Sample Data

The database is initialized with sample data:
- 3 users (admin, john, jane)
- 3 vaults
- 10 secrets across different types
- 5 audit log entries

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

### Encryption Issues
- Verify VAULT_MASTER_KEY is set correctly
- Check that key hasn't changed (would make existing secrets unreadable)
- Backup database before changing encryption keys

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Secret Types Supported

- **Password** - User passwords and credentials
- **API Key** - Third-party API keys
- **Token** - Authentication tokens
- **Certificate** - SSL/TLS certificates
- **SSH Key** - SSH private keys
- **Database Credential** - Database connection strings
- **Encryption Key** - Encryption keys
- **Generic** - Any other secret type

## 📄 License

Copyright © 2025 iTechSmart. All rights reserved.

## 🎯 Roadmap

- [ ] Advanced secret rotation policies
- [ ] Integration with cloud KMS (AWS, Azure, GCP)
- [ ] Secret templates
- [ ] Workflow approvals
- [ ] Secret expiration notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] LDAP/AD integration

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: January 2024