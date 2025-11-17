# iTechSmart Port Manager

**Dynamic Port Configuration and Management for the iTechSmart Suite**

The iTechSmart Port Manager is a comprehensive solution for managing port assignments across all 27 products in the iTechSmart Suite. It provides automatic conflict detection, dynamic port reassignment, real-time monitoring, and seamless integration with Enterprise Hub and Ninja.

---

## 🌟 Features

### Core Capabilities
- ✅ **Dynamic Port Allocation** - Automatically assign and manage ports for all services
- ✅ **Conflict Detection** - Real-time detection of port conflicts and duplicates
- ✅ **Automatic Resolution** - AI-powered automatic conflict resolution
- ✅ **Real-Time Monitoring** - Live monitoring of all service ports and health
- ✅ **Suite-Wide Management** - Manage all 27 iTechSmart products from one interface
- ✅ **Individual Service Control** - Update ports for specific services
- ✅ **Port Availability Checking** - Verify port availability before assignment
- ✅ **Configuration Backup/Restore** - Save and restore port configurations
- ✅ **WebSocket Real-Time Updates** - Live updates via WebSocket connections
- ✅ **Enterprise Hub Integration** - Full integration with iTechSmart Enterprise
- ✅ **Ninja Integration** - Self-healing and monitoring via Ninja

### Advanced Features
- 🔄 **Automatic Port Reassignment** - Intelligently reassign ports when conflicts occur
- 📊 **Port Usage Statistics** - Comprehensive statistics and analytics
- 📜 **Port History Tracking** - Track all port changes over time
- 🔒 **Port Reservation** - Reserve ports to prevent assignment
- 🎯 **Bulk Updates** - Update multiple services simultaneously
- 🔍 **Service Discovery** - Automatically discover all suite services
- 💾 **Persistent Configuration** - Configuration saved to disk
- 🚀 **Zero-Downtime Updates** - Update ports without service interruption

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              iTechSmart Port Manager (Port 8100)             │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Port Manager │  │    Suite     │  │  Integration │      │
│  │    Core      │  │ Communicator │  │    Module    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                    ┌───────┴───────┐
                    │               │
            ┌───────▼──────┐ ┌─────▼──────┐
            │ Enterprise   │ │   Ninja    │
            │     Hub      │ │ Monitoring │
            └──────────────┘ └────────────┘
                    │               │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │  All 27 Suite │
                    │   Products    │
                    └───────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Backend Setup

```bash
# Navigate to backend directory
cd itechsmart-port-manager/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m app.main
```

The backend will start on **http://localhost:8100**

### Frontend Setup

```bash
# Navigate to frontend directory
cd itechsmart-port-manager/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on **http://localhost:3000**

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d
```

---

## 📖 API Documentation

### Port Management Endpoints

#### Get All Port Assignments
```http
GET /api/ports/assignments
```

**Response:**
```json
{
  "success": true,
  "assignments": {
    "itechsmart-enterprise": 8001,
    "itechsmart-ninja": 8002,
    "legalai-pro": 8000,
    ...
  },
  "total": 27
}
```

#### Get Service Port
```http
GET /api/ports/assignments/{service_id}
```

**Response:**
```json
{
  "success": true,
  "service_id": "legalai-pro",
  "port": 8000
}
```

#### Assign Port
```http
POST /api/ports/assign
```

**Request Body:**
```json
{
  "service_id": "legalai-pro",
  "port": 8050,
  "force": false
}
```

**Response:**
```json
{
  "success": true,
  "service_id": "legalai-pro",
  "port": 8050,
  "message": "Assigned port 8050 to legalai-pro"
}
```

#### Reassign Port
```http
POST /api/ports/reassign
```

**Request Body:**
```json
{
  "service_id": "legalai-pro",
  "new_port": 8075
}
```

**Response:**
```json
{
  "success": true,
  "service_id": "legalai-pro",
  "old_port": 8050,
  "new_port": 8075,
  "message": "Reassigned legalai-pro from port 8050 to 8075",
  "update_result": {
    "success": true,
    "message": "Service updated successfully"
  }
}
```

#### Bulk Update Ports
```http
POST /api/ports/bulk-update
```

**Request Body:**
```json
{
  "updates": {
    "legalai-pro": 8000,
    "itechsmart-analytics": 8003,
    "itechsmart-shield": 8017
  }
}
```

#### Detect Conflicts
```http
GET /api/ports/conflicts
```

**Response:**
```json
{
  "success": true,
  "conflicts": [
    {
      "type": "duplicate_assignment",
      "port": 8000,
      "services": ["service1", "service2"],
      "severity": "high"
    }
  ],
  "count": 1
}
```

#### Resolve Conflicts
```http
POST /api/ports/resolve-conflicts
```

**Response:**
```json
{
  "success": true,
  "resolutions": [
    {
      "service": "service2",
      "old_port": 8000,
      "new_port": 8027,
      "success": true,
      "message": "Reassigned successfully"
    }
  ],
  "count": 1
}
```

#### Find Available Port
```http
GET /api/ports/available?start_port=8000
```

**Response:**
```json
{
  "success": true,
  "port": 8027
}
```

#### Get Port History
```http
GET /api/ports/history/{service_id}
```

**Response:**
```json
{
  "success": true,
  "service_id": "legalai-pro",
  "history": [8000, 8050, 8075]
}
```

#### Reserve Port
```http
POST /api/ports/reserve
```

**Request Body:**
```json
{
  "port": 8888
}
```

#### Unreserve Port
```http
DELETE /api/ports/reserve/{port}
```

#### Get Statistics
```http
GET /api/ports/statistics
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_services": 27,
    "used_ports": 27,
    "available_ports": 973,
    "reserved_ports": 0,
    "port_range": [8000, 9000],
    "conflicts": 0
  }
}
```

#### Backup Configuration
```http
POST /api/ports/backup
```

**Response:**
```json
{
  "success": true,
  "backup_file": "port_config_backup_20251212_143022.json",
  "message": "Configuration backed up"
}
```

#### Restore Configuration
```http
POST /api/ports/restore?backup_file=port_config_backup_20251212_143022.json
```

#### Reset to Defaults
```http
POST /api/ports/reset
```

### Service Management Endpoints

#### Discover Services
```http
GET /api/services/discover
```

#### Get All Service Status
```http
GET /api/services/status
```

**Response:**
```json
{
  "success": true,
  "statuses": [
    {
      "service_id": "legalai-pro",
      "port": 8000,
      "status": "healthy",
      "last_checked": "2025-12-12T14:30:22Z"
    }
  ],
  "total": 27,
  "healthy": 25,
  "unhealthy": 2
}
```

#### Get Service Status
```http
GET /api/services/status/{service_id}
```

#### Restart Service
```http
POST /api/services/restart
```

**Request Body:**
```json
{
  "service_id": "legalai-pro"
}
```

#### Check Service Health
```http
GET /api/services/health/{service_id}
```

### Health Endpoints

#### Basic Health Check
```http
GET /api/health/
```

#### Detailed Health Check
```http
GET /api/health/detailed
```

### WebSocket Endpoint

#### Real-Time Updates
```
ws://localhost:8100/ws/updates
```

**Message Types:**
- `connected` - Connection established
- `port_change` - Port assignment changed
- `conflicts_detected` - Conflicts detected
- `service_status` - Service status changed

---

## 🎨 Frontend Features

### Dashboard
- Real-time statistics cards
- Port usage distribution chart
- Service health status chart
- Port range utilization
- Quick stats overview

### Port Management
- View all port assignments
- Edit individual port assignments
- View port history
- Filter by service category
- Bulk port updates

### Service Status
- Real-time service health monitoring
- Service restart capability
- Health status indicators
- Auto-refresh every 15 seconds

### Conflict Resolution
- Automatic conflict detection
- One-click auto-resolution
- Conflict severity indicators
- Detailed conflict information

### Configuration
- Backup current configuration
- Restore from backup
- Reset to defaults
- Configuration management

---

## 🔧 Configuration

### Environment Variables

```bash
# Backend Configuration
PORT=8100
HOST=0.0.0.0

# Hub Configuration
HUB_URL=http://itechsmart-enterprise:8001
ENABLE_HUB=true

# Ninja Configuration
NINJA_URL=http://itechsmart-ninja:8002
ENABLE_NINJA=true

# Port Range
PORT_RANGE_START=8000
PORT_RANGE_END=9000
```

### Default Port Assignments

```python
{
    # Foundation Products
    "itechsmart-enterprise": 8001,
    "itechsmart-ninja": 8002,
    "itechsmart-analytics": 8003,
    "itechsmart-supreme": 8004,
    "itechsmart-hl7": 8005,
    "prooflink-ai": 8006,
    "passport": 8007,
    "impactos": 8008,
    "legalai-pro": 8000,
    
    # Strategic Products
    "itechsmart-dataflow": 8010,
    "itechsmart-pulse": 8011,
    "itechsmart-connect": 8012,
    "itechsmart-vault": 8013,
    "itechsmart-notify": 8014,
    "itechsmart-ledger": 8015,
    "itechsmart-copilot": 8016,
    "itechsmart-shield": 8017,
    "itechsmart-workflow": 8018,
    "itechsmart-marketplace": 8019,
    
    # Business Products
    "itechsmart-cloud": 8020,
    "itechsmart-devops": 8021,
    "itechsmart-mobile": 8022,
    "itechsmart-ai": 8023,
    "itechsmart-compliance": 8024,
    "itechsmart-data-platform": 8025,
    "itechsmart-customer-success": 8026,
    
    # Port Manager
    "itechsmart-port-manager": 8100
}
```

---

## 🔗 Integration

### Enterprise Hub Integration

The Port Manager automatically registers with Enterprise Hub and provides:
- Service registration
- Health reporting (every 30 seconds)
- Metrics reporting (every 60 seconds)
- Port change notifications

### Ninja Integration

The Port Manager integrates with Ninja for:
- Error detection and reporting
- Self-healing capabilities
- Performance monitoring
- Automatic recovery

---

## 📊 Use Cases

### Use Case 1: Port Conflict Resolution

**Scenario:** Two services are assigned to the same port

**Solution:**
1. Port Manager detects the conflict automatically
2. Navigate to "Conflict Resolution" page
3. Click "Auto-Resolve"
4. Port Manager reassigns one service to an available port
5. Both services updated automatically

### Use Case 2: Client Port Already in Use

**Scenario:** Client already has port 8000 in use

**Solution:**
1. Navigate to "Port Management"
2. Find the service using port 8000
3. Click edit icon
4. Enter new available port (e.g., 8050)
5. Click "Save"
6. Service automatically updated to new port

### Use Case 3: Bulk Port Migration

**Scenario:** Need to move all services to different port range

**Solution:**
1. Use API endpoint `/api/ports/bulk-update`
2. Provide mapping of service IDs to new ports
3. Port Manager updates all services simultaneously
4. Broadcasts changes to Hub and Ninja

---

## 🛠️ Development

### Project Structure

```
itechsmart-port-manager/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── core/
│   │   │   ├── port_manager.py     # Port management logic
│   │   │   └── suite_communicator.py  # Suite communication
│   │   ├── api/
│   │   │   ├── ports.py            # Port endpoints
│   │   │   ├── services.py         # Service endpoints
│   │   │   ├── health.py           # Health endpoints
│   │   │   └── websocket_api.py    # WebSocket endpoints
│   │   └── integrations/
│   │       └── integration.py      # Hub/Ninja integration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Main application
│   │   └── components/
│   │       ├── Dashboard.tsx       # Dashboard view
│   │       ├── PortManagement.tsx  # Port management
│   │       ├── ServiceStatus.tsx   # Service status
│   │       ├── ConflictResolution.tsx  # Conflicts
│   │       └── Configuration.tsx   # Configuration
│   └── package.json
└── README.md
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Backend
cd backend
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8100

# Frontend
cd frontend
npm run build
# Serve dist/ folder with nginx or similar
```

---

## 📈 Monitoring

### Metrics Available
- Total services managed
- Ports in use
- Available ports
- Reserved ports
- Conflict count
- Service health status
- Port utilization percentage

### Health Checks
- Basic health: `/api/health/`
- Detailed health: `/api/health/detailed`
- Service health: `/api/services/health/{service_id}`

---

## 🔒 Security

- JWT authentication (when integrated with PassPort)
- TLS 1.3 encryption for all communications
- Port validation and sanitization
- Rate limiting on API endpoints
- Audit logging via iTechSmart Ledger

---

## 🤝 Support

- **Documentation**: Full API documentation at `/docs`
- **WebSocket**: Real-time updates at `ws://localhost:8100/ws/updates`
- **Health Check**: Monitor at `/api/health/detailed`

---

## 📝 License

Part of the iTechSmart Suite - All rights reserved

---

## 🎉 Summary

**iTechSmart Port Manager** is the 27th product in the iTechSmart Suite, providing comprehensive port management capabilities for all suite products. With automatic conflict detection, dynamic reassignment, and seamless integration with Enterprise Hub and Ninja, it ensures smooth operation of the entire suite.

**Key Benefits:**
- ✅ Eliminates port conflicts
- ✅ Simplifies port management
- ✅ Enables dynamic reconfiguration
- ✅ Provides real-time monitoring
- ✅ Integrates with entire suite
- ✅ Supports backup/restore
- ✅ Offers beautiful UI

**Status:** 🎉 **100% Complete - Production Ready** 🎉