# iTechSmart Port Manager - Dynamic Port Management System

## Overview

iTechSmart Port Manager is a comprehensive port management system that dynamically allocates, monitors, and resolves port conflicts across all 32 iTechSmart Suite products. It ensures smooth operation by preventing port conflicts and enabling easy port reconfiguration.

## Features

### Dynamic Port Allocation
- Automatic port assignment for new services
- Conflict detection and resolution
- Port reservation system
- Range-based allocation
- Smart port suggestions

### Conflict Detection
- Real-time conflict monitoring
- Automatic conflict resolution
- Severity-based prioritization
- Historical conflict tracking
- Prevention strategies

### Service Management
- Service registration and discovery
- Health monitoring
- Status tracking
- Automatic restart on port changes
- Graceful shutdown handling

### Port Analytics
- Usage statistics
- Uptime tracking
- Performance metrics
- Historical trends
- Capacity planning

### Real-time Updates
- WebSocket-based live updates
- Instant conflict notifications
- Service status changes
- Port availability updates

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **WebSocket**: Real-time communication
- **API**: RESTful with automatic OpenAPI documentation

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI)
- **Real-time**: WebSocket integration
- **Charts**: Recharts for analytics

## Installation

### Using Docker (Recommended)

```bash
cd itechsmart-port-manager
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

- **Frontend**: http://localhost:3100
- **Backend API**: http://localhost:8100
- **API Documentation**: http://localhost:8100/docs
- **WebSocket**: ws://localhost:8100/ws
- **Health Check**: http://localhost:8100/health

## Quick Start

### Registering a Service

```bash
curl -X POST http://localhost:8100/api/services/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-service",
    "current_port": 8080,
    "health_endpoint": "http://localhost:8080/health"
  }'
```

### Checking Port Availability

```bash
curl http://localhost:8100/api/ports/8080/available
```

### Resolving Conflicts

```bash
curl -X POST http://localhost:8100/api/conflicts/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "my-service",
    "strategy": "auto"
  }'
```

## Database Models

### Core Models
- **Service** - Service information and configuration
- **Port** - Port status and availability
- **PortAssignment** - Port assignment history
- **PortConflict** - Conflict detection and resolution
- **PortRange** - Port range configurations
- **Configuration** - System configuration
- **HealthCheck** - Service health check results
- **PortStatistic** - Usage statistics

## Port Management

### Port Ranges
- **System Ports**: 0-1023 (Reserved)
- **Registered Ports**: 1024-49151 (Assignable)
- **Dynamic Ports**: 49152-65535 (Temporary)

### iTechSmart Suite Ports
- **8001-8032**: Core products
- **8100-8300**: Infrastructure products
- **3001-3032**: Frontend applications
- **3100-3300**: Infrastructure frontends

### Conflict Resolution Strategies
1. **Auto**: Automatically assign next available port
2. **Manual**: User selects new port
3. **Swap**: Swap ports between services
4. **Reserve**: Reserve port for future use

## API Endpoints

### Services
- `POST /api/services/register` - Register service
- `GET /api/services` - List all services
- `GET /api/services/{name}` - Get service details
- `PUT /api/services/{name}/port` - Update service port
- `DELETE /api/services/{name}` - Unregister service

### Ports
- `GET /api/ports` - List all ports
- `GET /api/ports/{port}/available` - Check availability
- `POST /api/ports/assign` - Assign port to service
- `POST /api/ports/release` - Release port
- `GET /api/ports/suggest` - Get port suggestions

### Conflicts
- `GET /api/conflicts` - List conflicts
- `POST /api/conflicts/detect` - Detect conflicts
- `POST /api/conflicts/resolve` - Resolve conflict
- `GET /api/conflicts/history` - Conflict history

### Health
- `GET /api/health/services` - All service health
- `GET /api/health/{service}` - Specific service health
- `POST /api/health/check` - Trigger health check

### Statistics
- `GET /api/stats/ports` - Port usage statistics
- `GET /api/stats/services` - Service statistics
- `GET /api/stats/conflicts` - Conflict statistics

## WebSocket Events

### Client → Server
- `subscribe` - Subscribe to updates
- `unsubscribe` - Unsubscribe from updates
- `ping` - Keep-alive ping

### Server → Client
- `service_registered` - New service registered
- `port_assigned` - Port assigned to service
- `conflict_detected` - Port conflict detected
- `conflict_resolved` - Conflict resolved
- `service_health` - Health status update

## Configuration

### Environment Variables

```env
DATABASE_URL=sqlite:///./port_manager.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/port_manager

PORT=8100
HEALTH_CHECK_INTERVAL=30
CONFLICT_CHECK_INTERVAL=60
```

## Integration with iTechSmart Suite

Port Manager integrates with:

- **Enterprise Hub** - Service coordination
- **Ninja** - Self-healing and monitoring
- **All 32 Products** - Port management for entire suite
- **MDM Agent** - Deployment coordination

## Monitoring & Alerts

### Health Monitoring
- Automatic health checks every 30 seconds
- Service availability tracking
- Response time monitoring
- Error detection and logging

### Conflict Alerts
- Real-time conflict detection
- Severity-based notifications
- Automatic resolution attempts
- Alert history and tracking

## Best Practices

### Port Assignment
1. Use port ranges for related services
2. Reserve ports for critical services
3. Document port assignments
4. Regular conflict checks
5. Monitor port usage

### Conflict Prevention
1. Register services before starting
2. Use health endpoints
3. Implement graceful shutdown
4. Handle port changes dynamically
5. Test port availability

### Performance
1. Limit concurrent health checks
2. Cache port availability
3. Use WebSocket for real-time updates
4. Regular database cleanup
5. Monitor system resources

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Check what's using the port
curl http://localhost:8100/api/ports/8080

# Resolve conflict
curl -X POST http://localhost:8100/api/conflicts/resolve \
  -d '{"service_name": "my-service", "strategy": "auto"}'
```

**Service Not Responding:**
```bash
# Check service health
curl http://localhost:8100/api/health/my-service

# Restart service
curl -X POST http://localhost:8100/api/services/my-service/restart
```

**Conflict Not Resolving:**
```bash
# Get conflict details
curl http://localhost:8100/api/conflicts

# Manual resolution
curl -X POST http://localhost:8100/api/conflicts/resolve \
  -d '{"service_name": "my-service", "strategy": "manual", "new_port": 8081}'
```

## Security Features

- Service authentication
- Port access control
- Audit logging
- Secure WebSocket connections
- Rate limiting

## Support

For support and documentation:
- API Documentation: http://localhost:8100/docs
- GitHub Issues: [Report issues]
- Email: support@itechsmart.dev

## License

Copyright © 2025 iTechSmart. All rights reserved.

---

**Part of the iTechSmart Suite** - The world's most comprehensive enterprise software ecosystem.