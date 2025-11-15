# iTechSmart Forge - Low-Code/No-Code Application Builder

## Overview

iTechSmart Forge is a powerful low-code/no-code platform that enables users to build custom applications through visual design, drag-and-drop components, and AI-powered generation. Perfect for rapid application development without extensive coding knowledge.

## Features

### Visual App Builder
- Drag-and-drop interface
- Real-time preview
- Component library with 150+ components
- Responsive design tools
- Custom styling options

### AI-Powered Generation
- Generate apps from natural language descriptions
- AI-suggested layouts and components
- Automatic code optimization
- Smart component recommendations

### Data Connectors
- Connect to all 31 iTechSmart products
- External database support (PostgreSQL, MySQL, MongoDB)
- REST API integration
- GraphQL support
- Real-time data sync

### Workflow Automation
- Visual workflow builder
- Conditional logic
- Event triggers
- Scheduled tasks
- Integration with other products

### One-Click Deployment
- Deploy to iTechSmart Suite
- Cloud deployment (AWS, Azure, GCP)
- Custom domain support
- SSL certificates
- Auto-scaling

### App Marketplace
- Publish apps to marketplace
- Template library
- Community sharing
- Revenue sharing (70/30)

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **AI Engine**: Custom AI models for app generation

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI)
- **Drag-and-Drop**: React Beautiful DnD
- **Grid System**: React Grid Layout

## Installation

### Using Docker (Recommended)

```bash
cd itechsmart-forge
docker-compose up -d
```

### Manual Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3032
- **Backend API**: http://localhost:8032
- **API Documentation**: http://localhost:8032/docs
- **Health Check**: http://localhost:8032/health

## Quick Start

### Creating Your First App

1. **Open Forge**: Navigate to http://localhost:3032
2. **Click "Create New App"**: Enter your app name
3. **Choose Template**: Select from pre-built templates or start blank
4. **Design Interface**: Drag components onto canvas
5. **Connect Data**: Link to data sources
6. **Preview**: Test your app in real-time
7. **Deploy**: One-click deployment to production

### Using AI Generation

1. **Describe Your App**: "Create a customer management system with contact list and notes"
2. **AI Generates**: Complete app structure with components
3. **Customize**: Modify generated app as needed
4. **Deploy**: Push to production

## Component Library

### Basic Components
- Button, Text, Input, Checkbox, Radio, Select, Switch

### Layout Components
- Container, Grid, Card, Tabs, Accordion, Divider

### Data Components
- Table, List, Tree, Timeline, Calendar

### Visualization Components
- Charts (Line, Bar, Pie, Area, Scatter)
- Gauges, Metrics, KPIs

### Form Components
- Form Builder, Validation, File Upload, Date Picker

### Advanced Components
- Map, Video Player, Audio Player, PDF Viewer

## Data Connectors

### iTechSmart Products
- Connect to any of the 31 products
- Real-time data sync
- Automatic schema detection

### External Databases
- PostgreSQL, MySQL, MongoDB
- SQL Server, Oracle
- Redis, Elasticsearch

### APIs
- REST API integration
- GraphQL support
- Webhook triggers
- OAuth authentication

## Workflow Automation

### Visual Workflow Builder
- Drag-and-drop workflow design
- Conditional branching
- Loops and iterations
- Error handling

### Triggers
- User actions (click, submit, etc.)
- Scheduled (cron jobs)
- Data changes (insert, update, delete)
- External events (webhooks)

### Actions
- Database operations
- API calls
- Email notifications
- File operations
- Custom code execution

## Deployment Options

### iTechSmart Suite
- Deploy directly to suite infrastructure
- Automatic integration with other products
- Managed hosting

### Cloud Platforms
- AWS (ECS, Lambda, S3)
- Azure (App Service, Functions)
- Google Cloud (Cloud Run, Functions)

### Custom Deployment
- Docker containers
- Kubernetes clusters
- Traditional servers

## App Marketplace

### Publishing Apps
1. Complete app development
2. Add description and screenshots
3. Set pricing (free or paid)
4. Submit for review
5. Publish to marketplace

### Revenue Sharing
- 70% to developer
- 30% to platform
- Monthly payouts
- Transparent analytics

## Integration with iTechSmart Suite

Forge integrates with:

- **Enterprise Hub** - Service coordination
- **Ninja** - Self-healing and monitoring
- **Analytics** - Usage analytics
- **All Products** - Data connectors for all 31 products

## API Endpoints

### Apps
- `POST /api/apps` - Create app
- `GET /api/apps` - List apps
- `GET /api/apps/{id}` - Get app
- `PUT /api/apps/{id}` - Update app
- `DELETE /api/apps/{id}` - Delete app

### AI Generation
- `POST /api/ai/generate` - Generate app from description
- `POST /api/ai/suggest` - Get component suggestions
- `POST /api/ai/optimize` - Optimize app structure

### Components
- `GET /api/components` - List components
- `GET /api/components/{id}` - Get component details

### Deployment
- `POST /api/deploy` - Deploy app
- `GET /api/deploy/{id}/status` - Get deployment status

## Security Features

- Role-based access control
- App-level permissions
- Data encryption
- Secure API keys
- Audit logging

## Support

For support and documentation:
- API Documentation: http://localhost:8032/docs
- GitHub Issues: [Report issues]
- Email: support@itechsmart.dev

## License

Copyright © 2025 iTechSmart. All rights reserved.

---

**Part of the iTechSmart Suite** - The world's most comprehensive enterprise software ecosystem.