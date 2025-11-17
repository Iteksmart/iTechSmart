# iTechSmart Notify

A comprehensive notification management system for sending multi-channel notifications (Email, SMS, Push, Webhook) with template management, delivery tracking, and analytics.

## 🎯 Features

- **Multi-Channel Support**: Email, SMS, Push Notifications, and Webhooks
- **Template Management**: Create and manage reusable notification templates with variable substitution
- **Channel Configuration**: Configure multiple notification channels with different providers
- **Delivery Tracking**: Real-time tracking of notification status and delivery history
- **Analytics & Reporting**: Comprehensive performance metrics and delivery rate monitoring
- **Queue Management**: Redis-based queue for reliable message delivery
- **API-First Design**: RESTful API with comprehensive Swagger documentation
- **Modern UI**: Beautiful, responsive React frontend with Tailwind CSS
- **Scalable Architecture**: Built with FastAPI and PostgreSQL for high performance

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Message Broker**: RabbitMQ 3
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **API Documentation**: Swagger/OpenAPI

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Icons**: Lucide React
- **Routing**: React Router DOM v6
- **HTTP Client**: Fetch API

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose (recommended)
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd itechsmart-notify
```

2. **Start all services**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- RabbitMQ message broker (ports 5672, 15672)
- Backend API (port 8000)
- Frontend UI (port 80)

3. **Access the application**
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (user: notify, pass: notify_pass)

### Local Development Setup

#### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## 📚 API Documentation

### Authentication
All API endpoints require authentication using API keys or JWT tokens.

### Core Endpoints

#### Notifications
- `POST /api/notifications` - Send a notification
- `GET /api/notifications` - List notifications with filtering
- `GET /api/notifications/{id}` - Get notification details
- `GET /api/notifications/stats` - Get notification statistics
- `GET /api/notifications/stats/channels` - Get channel statistics
- `GET /api/notifications/export` - Export notifications to CSV

#### Templates
- `POST /api/templates` - Create a template
- `GET /api/templates` - List templates
- `GET /api/templates/{id}` - Get template details
- `PUT /api/templates/{id}` - Update a template
- `DELETE /api/templates/{id}` - Delete a template

#### Channels
- `POST /api/channels` - Create a channel
- `GET /api/channels` - List channels
- `GET /api/channels/{id}` - Get channel details
- `PUT /api/channels/{id}` - Update a channel
- `DELETE /api/channels/{id}` - Delete a channel

#### Analytics
- `GET /api/analytics` - Get analytics data with date range
- `GET /api/analytics/export` - Export analytics report (PDF/CSV)

#### Settings
- `GET /api/settings` - Get system settings
- `PUT /api/settings` - Update system settings

### Example: Send a Notification

```bash
curl -X POST http://localhost:8000/api/notifications \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "channel": "email",
    "recipient": "user@example.com",
    "template_id": "welcome_email",
    "variables": {
      "user_name": "John Doe",
      "company_name": "iTechSmart"
    }
  }'
```

### Example: Create a Template

```bash
curl -X POST http://localhost:8000/api/templates \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "name": "Welcome Email",
    "channel": "email",
    "subject": "Welcome to {{company_name}}",
    "content": "Hello {{user_name}}, welcome to our platform!",
    "variables": ["user_name", "company_name"]
  }'
```

## 🎨 Frontend Features

### Dashboard
- Real-time notification statistics
- Delivery rate monitoring
- Channel distribution visualization
- Recent notifications feed

### Templates
- Visual template editor
- Variable management
- Template preview
- Duplicate and edit functionality

### Channels
- Multi-provider support
- Channel configuration wizard
- Enable/disable channels
- Provider-specific settings

### History
- Advanced filtering and search
- Detailed notification tracking
- Status timeline
- Export capabilities

### Analytics
- Time-series data visualization
- Channel performance comparison
- Top performing templates
- Custom date range selection

### Settings
- General configuration
- Notification preferences
- Security settings
- Email configuration
- Database management

## 🏛️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   PostgreSQL    │
│  (React + TS)   │     │    (FastAPI)    │     │    Database     │
│   Port: 80      │     │   Port: 8000    │     │   Port: 5432    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ├────▶ Redis (Cache/Queue)
                               │      Port: 6379
                               │
                               └────▶ RabbitMQ (Message Broker)
                                      Ports: 5672, 15672
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://notify_user:notify_pass@localhost:5432/itechsmart_notify

# Redis
REDIS_URL=redis://localhost:6379

# RabbitMQ
RABBITMQ_URL=amqp://notify:notify_pass@localhost:5672

# Security
JWT_SECRET=your_jwt_secret_here_change_in_production
API_KEY_SECRET=your_api_key_secret_here_change_in_production

# Application
APP_NAME=iTechSmart Notify
ENVIRONMENT=production
LOG_LEVEL=info
```

### Channel Provider Configuration

#### Email (SMTP)
```json
{
  "host": "smtp.example.com",
  "port": 587,
  "username": "user@example.com",
  "password": "your_password",
  "from": "noreply@example.com"
}
```

#### SMS (Twilio)
```json
{
  "provider": "twilio",
  "accountSid": "your_account_sid",
  "authToken": "your_auth_token",
  "fromNumber": "+1234567890"
}
```

#### Push (Firebase)
```json
{
  "provider": "fcm",
  "serverKey": "your_server_key",
  "senderId": "your_sender_id"
}
```

## 📊 Features in Detail

### Multi-Channel Notifications
- **Email**: SMTP integration with HTML templates
- **SMS**: Twilio, Nexmo, AWS SNS support
- **Push**: Firebase Cloud Messaging, APNS, OneSignal
- **Webhook**: HTTP/HTTPS webhook delivery with retry logic

### Template System
- Variable substitution using `{{variable_name}}` syntax
- Support for all notification channels
- Template versioning and management
- Preview and testing capabilities
- Bulk operations support

### Delivery Tracking
- Real-time status updates (pending, sent, delivered, failed)
- Delivery confirmation with timestamps
- Failure tracking with detailed error messages
- Automatic retry mechanism for failed deliveries
- Comprehensive delivery history

### Analytics Dashboard
- Delivery rate metrics with trends
- Channel performance comparison
- Time-series data visualization
- Template usage statistics
- Export capabilities (CSV, PDF)
- Custom date range filtering

## 🔒 Security

- API key authentication
- JWT token support
- Rate limiting
- IP whitelisting
- Secure password hashing
- CORS configuration
- SQL injection prevention
- XSS protection

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 📦 Deployment

### Production Deployment

1. **Update environment variables** in `.env` file
2. **Build and start services**:
```bash
docker-compose up -d --build
```

3. **Verify services are running**:
```bash
docker-compose ps
```

4. **Check logs**:
```bash
docker-compose logs -f
```

### Scaling

To scale the backend service:
```bash
docker-compose up -d --scale backend=3
```

## 🛠️ Maintenance

### Database Backup
```bash
docker exec notify-postgres pg_dump -U notify_user itechsmart_notify > backup.sql
```

### Database Restore
```bash
docker exec -i notify-postgres psql -U notify_user itechsmart_notify < backup.sql
```

### Clear Redis Cache
```bash
docker exec notify-redis redis-cli FLUSHALL
```

## 📝 License

Proprietary - iTechSmart Inc.

## 🤝 Support

**Manufacturer**: iTechSmart Inc.  
**Address**: 1130 Ogletown Road, Suite 2, Newark, DE 19711, USA  
**Phone**: 310-251-3969  
**Website**: https://itechsmart.dev  
**Email**: support@itechsmart.dev

## 🎉 Acknowledgments

Built with ❤️ by iTechSmart Inc.

**Copyright © 2025 iTechSmart Inc. All rights reserved.**
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



## 🚀 Upcoming Features (v1.4.0)

1. **Multi-channel delivery**
2. **Template builder**
3. **A/B testing**
4. **Delivery tracking**
5. **Scheduled notifications**
6. **User preferences**
7. **Rate limiting**
8. **Marketing integration**

**Product Value**: $1.3M  
**Tier**: 3  
**Total Features**: 8

