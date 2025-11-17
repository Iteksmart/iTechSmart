# iTechSmart Connect - API Management Platform

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node](https://img.shields.io/badge/node-20.x-green.svg)
![Docker](https://img.shields.io/badge/docker-24.0+-blue.svg)

**Enterprise API management platform with gateway, monitoring, analytics, and developer portal capabilities.**

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [License](#license)

---

## 🎯 Overview

iTechSmart Connect is a comprehensive API management platform designed for enterprises that need to manage, monitor, and secure their APIs. Built with modern technologies and best practices, it provides:

- **API Gateway**: Centralized API routing and management
- **API Keys Management**: Secure authentication with scoped permissions
- **Rate Limiting**: Protect your APIs from abuse
- **Real-time Analytics**: Monitor API performance and usage
- **Developer Portal**: Interactive API documentation
- **Webhook Support**: Event-driven integrations
- **Request Logging**: Complete audit trail of all API calls

### Market Value
**Estimated Value**: $600K - $1M

### Use Cases
- API gateway and routing
- API key management and authentication
- Rate limiting and throttling
- API analytics and monitoring
- Developer documentation portal
- Webhook management

---

## ✨ Features

### 🔐 API Management
- **API Registry**: Centralized catalog of all APIs
- **Version Control**: Manage multiple API versions
- **Endpoint Management**: Configure individual endpoints
- **Status Monitoring**: Track API health and uptime
- **Deprecation Management**: Gracefully sunset old APIs

### 🔑 Authentication & Security
- **API Key Generation**: Secure key generation with scopes
- **JWT Authentication**: Token-based authentication
- **Role-Based Access**: Admin, Developer, Viewer roles
- **IP Whitelisting**: Restrict access by IP address
- **2FA Support**: Two-factor authentication

### 📊 Analytics & Monitoring
- **Real-time Metrics**: Live API performance data
- **Request Analytics**: Detailed request/response tracking
- **Performance Metrics**: Response time percentiles (P50, P95, P99)
- **Error Tracking**: Monitor and analyze API errors
- **Geographic Distribution**: Track requests by region
- **Top APIs Dashboard**: Identify most-used endpoints

### 🚦 Rate Limiting
- **Flexible Limits**: Per-minute, per-hour, per-day limits
- **Scope-based**: Global, API, endpoint, or user-level limits
- **Redis-backed**: High-performance rate limiting
- **Custom Rules**: Define custom rate limit rules

### 📚 Developer Portal
- **Interactive Documentation**: Auto-generated API docs
- **Code Examples**: Sample requests in multiple languages
- **Try It Out**: Test APIs directly from documentation
- **Changelog**: Track API changes and updates

### 🔔 Webhooks
- **Event Subscriptions**: Subscribe to API events
- **Retry Logic**: Automatic retry on failure
- **Delivery Tracking**: Monitor webhook deliveries
- **Secret Verification**: Secure webhook payloads

---

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0 (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT with OAuth2
- **API Documentation**: OpenAPI/Swagger

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5
- **UI Library**: Tailwind CSS 3
- **Charts**: Recharts 2.10
- **Routing**: React Router 6
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker 24+, Docker Compose 2+
- **Reverse Proxy**: Nginx (optional)
- **Monitoring**: Prometheus, Grafana (optional)

---

## 🚀 Quick Start

### Prerequisites
- Docker 24.0+ and Docker Compose 2.0+
- 4GB+ RAM (8GB recommended)
- 10GB+ free disk space

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd itechsmart-connect
```

2. **Start all services**
```bash
./start.sh
```

3. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

4. **Login with default credentials**
```
Admin:
  Email: admin@itechsmart.dev
  Password: password

Developer:
  Email: developer@itechsmart.dev
  Password: password

Viewer:
  Email: viewer@itechsmart.dev
  Password: password
```

### First Steps

1. **Register an API**
   - Navigate to APIs page
   - Click "Create API"
   - Enter API details (name, base URL, version)
   - Save the API

2. **Generate API Key**
   - Go to API Keys page
   - Click "Generate New Key"
   - Set scopes and expiration
   - Copy and save the key securely

3. **Configure Rate Limits**
   - Navigate to Settings > Advanced
   - Set rate limits (per minute, hour, day)
   - Apply limits globally or per API

4. **View Analytics**
   - Go to Analytics page
   - Monitor request trends
   - Check response times
   - Analyze error rates

---

## 🏗 Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│         React 18 + TypeScript + Tailwind CSS                │
│                                                              │
│  ┌──────────┬──────────┬──────────┬──────────┐             │
│  │Dashboard │   APIs   │ API Keys │Analytics │             │
│  └──────────┴──────────┴──────────┴──────────┘             │
└─────────────────────────────────────────────────────────────┘
                         ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                        Backend Layer                         │
│              FastAPI + SQLAlchemy + Redis                   │
│                                                              │
│  ┌──────────┬──────────┬──────────┬──────────┐             │
│  │   Auth   │   API    │   Rate   │ Webhook  │             │
│  │ Service  │ Gateway  │ Limiter  │ Service  │             │
│  └──────────┴──────────┴──────────┴──────────┘             │
└─────────────────────────────────────────────────────────────┘
                         ↓ SQL/Cache
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│                                                              │
│  ┌──────────────────┬──────────────────┐                   │
│  │   PostgreSQL 15  │     Redis 7      │                   │
│  │   (Primary DB)   │     (Cache)      │                   │
│  └──────────────────┴──────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

#### Core Tables (13)
- **users**: User accounts and authentication
- **apis**: API registry and configuration
- **api_endpoints**: Individual API endpoints
- **api_versions**: API version management
- **api_keys**: API key management
- **request_logs**: Request/response logging
- **rate_limits**: Rate limit configurations
- **webhooks**: Webhook configurations
- **webhook_deliveries**: Webhook delivery tracking
- **api_metrics**: API performance metrics
- **api_documentation**: API documentation
- **audit_logs**: Complete audit trail

---

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

All API endpoints (except `/token` and `/health`) require authentication using JWT Bearer tokens.

#### Get Access Token
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

#### Use Token in Requests
```bash
curl -X GET "http://localhost:8000/apis" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Key Endpoints

**APIs Management**
- `GET /apis` - List all APIs
- `POST /apis` - Create new API
- `GET /apis/{id}` - Get API details
- `PUT /apis/{id}` - Update API
- `DELETE /apis/{id}` - Delete API

**API Keys**
- `GET /api-keys` - List API keys
- `POST /api-keys` - Generate new key
- `DELETE /api-keys/{id}` - Revoke key

**Analytics**
- `GET /analytics/overview` - Overview metrics
- `GET /analytics/requests` - Request analytics
- `GET /analytics/top-apis` - Top APIs by traffic

**Rate Limiting**
- `GET /rate-limits` - List rate limits
- `POST /rate-limits` - Create rate limit

**Webhooks**
- `GET /webhooks` - List webhooks
- `POST /webhooks` - Create webhook

---

## 💻 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Database Operations

```bash
# Connect to database
docker-compose exec postgres psql -U connect_user -d connect

# Backup database
docker-compose exec postgres pg_dump -U connect_user connect > backup.sql

# Restore database
docker-compose exec -T postgres psql -U connect_user connect < backup.sql
```

---

## 🚢 Deployment

### Docker Compose (Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Production Deployment

For production deployment, see the detailed deployment guide in `DEPLOYMENT.md`.

Key considerations:
- Use strong secret keys
- Enable SSL/TLS
- Configure firewall rules
- Set up monitoring
- Configure backups
- Use environment-specific configs

---

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Production Ready (100% Complete)
- **Last Updated**: January 2025
- **Maintainer**: iTechSmart Inc

### Features Complete
- ✅ API Management (100%)
- ✅ API Keys Management (100%)
- ✅ Rate Limiting (100%)
- ✅ Analytics & Monitoring (100%)
- ✅ Developer Documentation (100%)
- ✅ Webhook Support (100%)
- ✅ Authentication & Security (100%)
- ✅ Database & Infrastructure (100%)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation**: [Full Documentation](https://docs.itechsmart.dev/connect)
- **Issues**: [GitHub Issues](https://github.com/itechsmart/connect/issues)
- **Email**: support@itechsmart.dev

---

<div align="center">

**Made with ❤️ by the iTechSmart Inc**

[Website](https://itechsmart.dev) • [Documentation](https://docs.itechsmart.dev) • [Blog](https://blog.itechsmart.dev)

</div>