# PassPort

## Overview

Identity Management - Unified authentication and access control

## Features

- **Single Sign-On (SSO)**
- **Multi-factor authentication (MFA)**
- **Role-based access control (RBAC)**
- **OAuth2 integration**
- **LDAP/Active Directory sync**
- **Session management**
- **Audit logging**
- **Password policies**


## Technology Stack

FastAPI, PostgreSQL, JWT, OAuth2

## Installation

### Using Docker (Recommended)

```bash
cd passport
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

- **Frontend**: http://localhost:3007
- **Backend API**: http://localhost:8007
- **API Documentation**: http://localhost:8007/docs
- **Health Check**: http://localhost:8007/health

## Integration with iTechSmart Suite

PassPort integrates with:

All 32 iTechSmart products

## Support

For support and documentation:
- API Documentation: http://localhost:8007/docs
- Email: support@itechsmart.dev

## License

Copyright © 2025 iTechSmart. All rights reserved.

---

**Part of the iTechSmart Suite** - The world's most comprehensive enterprise software ecosystem.
