# iTechSmart Pulse - Analytics &amp; Business Intelligence Platform

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node](https://img.shields.io/badge/node-20.x-green.svg)
![Docker](https://img.shields.io/badge/docker-24.0+-blue.svg)

**Enterprise-grade analytics and business intelligence platform with real-time data processing, interactive visualizations, and advanced reporting capabilities.**

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture) • [Contributing](#contributing)

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
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

iTechSmart Pulse is a comprehensive analytics and business intelligence platform designed for enterprises that need powerful data analysis, visualization, and reporting capabilities. Built with modern technologies and best practices, it provides:

- **Real-time Analytics**: Process and analyze data in real-time with ClickHouse
- **Interactive Dashboards**: Create beautiful, responsive dashboards with 8+ chart types
- **Advanced Reporting**: Generate PDF, Excel, and CSV reports with scheduling
- **SQL Query Builder**: Visual and code-based query building with syntax highlighting
- **Data Source Integration**: Connect to 100+ data sources including PostgreSQL, MySQL, MongoDB, Salesforce, and more
- **Alert System**: Set up intelligent alerts with multiple notification channels
- **Role-Based Access**: Granular permissions and user management
- **API-First Design**: RESTful API with comprehensive documentation

### Market Value
**Estimated Value**: $800K - $1.5M

### Use Cases
- Executive dashboards and KPI tracking
- Sales and marketing analytics
- Financial reporting and analysis
- Customer behavior analysis
- Operational metrics monitoring
- Data exploration and discovery

---

## ✨ Features

### 📊 Data Visualization
- **8+ Chart Types**: Line, Bar, Pie, Area, Scatter, Heatmap, Gauge, Funnel
- **Interactive Charts**: Zoom, pan, filter, and drill-down capabilities
- **Real-time Updates**: Live data streaming and automatic refresh
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Export Options**: PNG, SVG, PDF export for all visualizations

### 📈 Analytics &amp; Reporting
- **Ad-hoc Analysis**: Quick data exploration with drag-and-drop interface
- **Scheduled Reports**: Automated report generation and distribution
- **Custom Metrics**: Define and track custom KPIs and metrics
- **Trend Analysis**: Identify patterns and trends in your data
- **Comparative Analysis**: Compare metrics across time periods and segments

### 🔌 Data Integration
- **100+ Connectors**: Pre-built connectors for popular data sources
- **Custom Connectors**: Build your own connectors with our SDK
- **Real-time Sync**: Continuous data synchronization
- **Data Transformation**: ETL capabilities with custom transformations
- **Data Quality**: Built-in validation and quality checks

### 🔍 Query Builder
- **Visual Builder**: Drag-and-drop query construction
- **SQL Editor**: Advanced SQL editor with syntax highlighting
- **Query History**: Track and reuse previous queries
- **Query Optimization**: Automatic query optimization suggestions
- **Saved Queries**: Save and share queries with your team

### 🔔 Alerts &amp; Notifications
- **Intelligent Alerts**: Set up alerts based on thresholds and conditions
- **Multiple Channels**: Email, Slack, SMS, Webhook notifications
- **Alert History**: Track all alert triggers and responses
- **Escalation Rules**: Define escalation paths for critical alerts
- **Snooze &amp; Acknowledge**: Manage alert fatigue effectively

### 👥 User Management
- **Role-Based Access**: Admin, Analyst, Viewer roles with custom permissions
- **Team Collaboration**: Share dashboards, reports, and queries
- **Audit Logs**: Complete audit trail of all user actions
- **SSO Integration**: SAML, OAuth2, LDAP support
- **API Keys**: Programmatic access with API key management

---

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0 (Python 3.11+)
- **Database**: PostgreSQL 15 (Primary), ClickHouse (Analytics)
- **Cache**: Redis 7
- **Message Queue**: RabbitMQ 3
- **Object Storage**: MinIO
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT with OAuth2
- **API Documentation**: OpenAPI/Swagger

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5
- **UI Library**: Tailwind CSS 3
- **Charts**: Recharts 2.10
- **Routing**: React Router 6
- **State Management**: React Context API
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker 24+, Docker Compose 2+
- **Orchestration**: Kubernetes (optional)
- **CI/CD**: GitHub Actions, GitLab CI
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

### Development Tools
- **Code Quality**: Black, Flake8, MyPy, ESLint, Prettier
- **Testing**: Pytest, Jest, React Testing Library
- **Documentation**: Sphinx, Storybook
- **Version Control**: Git, GitHub/GitLab

---

## 🚀 Quick Start

### Prerequisites
- Docker 24.0+ and Docker Compose 2.0+
- 8GB+ RAM (16GB recommended)
- 20GB+ free disk space

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd itechsmart-pulse
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

5. **Login with default credentials**
```
Email: admin@itechsmart.dev
Password: password
```

### First Steps

1. **Connect a Data Source**
   - Navigate to Data Sources
   - Click "Add Data Source"
   - Select your database type
   - Enter connection details
   - Test and save

2. **Create a Dataset**
   - Go to Datasets
   - Click "New Dataset"
   - Select your data source
   - Write or build your query
   - Save the dataset

3. **Build a Dashboard**
   - Navigate to Dashboards
   - Click "Create Dashboard"
   - Add visualizations
   - Arrange and configure
   - Save and share

4. **Generate a Report**
   - Go to Reports
   - Click "New Report"
   - Select dataset and format
   - Configure schedule (optional)
   - Generate or schedule

---

## 🏗 Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  React 18 + TypeScript + Tailwind CSS + Recharts           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway / Load Balancer             │
│                         (Nginx / Traefik)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        Backend Layer                         │
│              FastAPI + SQLAlchemy + Celery                   │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │   Auth   │   Data   │  Query   │  Report  │  Alert   │  │
│  │ Service  │ Service  │ Service  │ Service  │ Service  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │PostgreSQL│ClickHouse│  Redis   │ RabbitMQ │  MinIO   │  │
│  │(Primary) │(Analytics)│ (Cache)  │ (Queue)  │(Storage) │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    External Data Sources                     │
│  PostgreSQL │ MySQL │ MongoDB │ Salesforce │ S3 │ APIs     │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

#### PostgreSQL (Primary Database)
- **users**: User accounts and authentication
- **data_sources**: Connected data sources
- **datasets**: Defined datasets and queries
- **reports**: Report definitions and schedules
- **dashboards**: Dashboard configurations
- **visualizations**: Chart and visualization configs
- **queries**: Saved SQL queries
- **alerts**: Alert definitions and rules
- **scheduled_jobs**: Background job schedules
- **audit_logs**: Complete audit trail
- **api_keys**: API key management

#### ClickHouse (Analytics Database)
- **events**: User interaction events
- **query_metrics**: Query performance metrics
- **dashboard_views**: Dashboard usage analytics
- **report_executions**: Report generation logs
- **data_source_metrics**: Data source performance
- **alert_triggers**: Alert trigger history
- **user_activity**: User activity tracking
- **system_performance**: System metrics

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
  -d "username=admin&amp;password=password"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "username": "admin",
    "email": "admin@itechsmart.dev",
    "role": "admin"
  }
}
```

#### Use Token in Requests
```bash
curl -X GET "http://localhost:8000/data-sources" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 💻 Development

### Backend Development

#### Setup Local Environment
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

#### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Frontend Development

#### Setup Local Environment
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

#### Run Tests
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage
```

---

## 🚢 Deployment

### Docker Compose (Recommended for Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions.

---

## 🧪 Testing

### Backend Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=. --cov-report=html
```

### Frontend Tests

```bash
# Unit tests
npm run test:unit

# Component tests
npm run test:components

# All tests with coverage
npm run test:coverage
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation**: [Full Documentation](https://docs.itechsmart.dev/pulse)
- **Issues**: [GitHub Issues](https://github.com/itechsmart/pulse/issues)
- **Email**: support@itechsmart.dev

---

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Production Ready (100% Complete)
- **Last Updated**: January 2024
- **Maintainer**: iTechSmart Team

---

<div align="center">

**Made with ❤️ by the iTechSmart Team**

[Website](https://itechsmart.dev) • [Documentation](https://docs.itechsmart.dev) • [Blog](https://blog.itechsmart.dev)

</div>