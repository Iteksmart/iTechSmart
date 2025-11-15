# iTechSmart Enterprise

## Overview

Integration Hub - Central coordination platform for all iTechSmart products

## Features

- **Service registration and discovery**
- **Health monitoring (30-second intervals)**
- **Metrics collection (60-second intervals)**
- **Cross-product routing**
- **Unified authentication (SSO)**
- **Configuration management**
- **Event broadcasting**
- **API gateway**


## Technology Stack

FastAPI, PostgreSQL, Redis, WebSocket

## Installation

### Using Docker (Recommended)

```bash
cd itechsmart-enterprise
docker-compose up -d
```

### Manual Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
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

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## Integration with iTechSmart Suite

iTechSmart Enterprise integrates with:

All 32 iTechSmart products

## Support

For support and documentation:
- API Documentation: http://localhost:8001/docs
- Email: support@itechsmart.dev

## License

Copyright © 2025 iTechSmart. All rights reserved.

---

**Part of the iTechSmart Suite** - The world's most comprehensive enterprise software ecosystem.
