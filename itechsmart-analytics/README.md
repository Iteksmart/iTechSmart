# iTechSmart Analytics

**Advanced Analytics Platform for the iTechSmart Suite**

## Overview

iTechSmart Analytics is a comprehensive analytics platform that provides deep insights, predictive analytics, and business intelligence across all iTechSmart products. It aggregates data from multiple sources, performs advanced analysis, and delivers actionable insights through intuitive dashboards and reports.

## Key Features

### 1. **Agent Monitoring Integration** 🆕
- Real-time agent status monitoring
- System metrics visualization (CPU, Memory, Disk)
- Health score calculation and trending
- Alert management and notifications
- Comprehensive agent analytics dashboard

### 2. **Multi-Source Data Integration**
- Seamless integration with all iTechSmart products
- Real-time data ingestion and processing
- Support for external data sources
- Automated data synchronization

### 3. **Advanced Analytics**
- Predictive analytics and forecasting
- Machine learning-powered insights
- Anomaly detection
- Trend analysis
- Correlation analysis

### 3. **Business Intelligence**
- Custom dashboards and reports
- KPI tracking and monitoring
- Goal setting and progress tracking
- Comparative analysis

### 4. **Data Visualization**
- Interactive charts and graphs
- Real-time data updates
- Customizable visualizations
- Export capabilities

### 5. **Automated Reporting**
- Scheduled report generation
- Email delivery
- Custom report templates
- Multi-format export (PDF, Excel, CSV)

## Architecture

```
iTechSmart Analytics
├── Data Ingestion Layer
│   ├── Real-time streaming
│   ├── Batch processing
│   └── API connectors
├── Processing Engine
│   ├── Data transformation
│   ├── Aggregation
│   └── ML models
├── Analytics Engine
│   ├── Statistical analysis
│   ├── Predictive models
│   └── Pattern recognition
├── Visualization Layer
│   ├── Dashboard builder
│   ├── Chart library
│   └── Report generator
└── API Layer
    ├── REST API
    ├── GraphQL
    └── WebSocket
```

## Technology Stack

- **Backend**: Python (FastAPI), Apache Spark
- **Database**: PostgreSQL, TimescaleDB, Redis
- **ML/Analytics**: scikit-learn, TensorFlow, pandas, NumPy
- **Visualization**: D3.js, Plotly, Recharts
- **Frontend**: React, TypeScript, Material-UI
- **Message Queue**: Apache Kafka
- **Cache**: Redis

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# Clone repository
git clone https://github.com/itechsmart/analytics.git
cd analytics

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Set up database
python scripts/init_db.py

# Start services
docker-compose up -d
```

### Configuration

Create `.env` file:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/analytics
REDIS_URL=redis://localhost:6379
KAFKA_BROKERS=localhost:9092
SECRET_KEY=your-secret-key
ENTERPRISE_API_URL=http://localhost:8000
```

## Usage

### Creating a Dashboard

```python
from analytics import Dashboard, Widget

# Create dashboard
dashboard = Dashboard(
    name="Sales Analytics",
    description="Real-time sales metrics"
)

# Add widgets
dashboard.add_widget(
    Widget(
        type="line_chart",
        title="Revenue Trend",
        data_source="sales.revenue",
        time_range="30d"
    )
)

dashboard.save()
```

### Running Analytics

```python
from analytics import AnalyticsEngine

engine = AnalyticsEngine()

# Run predictive analysis
forecast = engine.forecast(
    metric="revenue",
    horizon="30d",
    model="prophet"
)

# Detect anomalies
anomalies = engine.detect_anomalies(
    metric="user_activity",
    sensitivity="high"
)
```

## API Documentation

### REST API

```
GET    /api/dashboards          - List all dashboards
POST   /api/dashboards          - Create dashboard
GET    /api/dashboards/{id}     - Get dashboard
PUT    /api/dashboards/{id}     - Update dashboard
DELETE /api/dashboards/{id}     - Delete dashboard

GET    /api/analytics/forecast  - Get forecast
GET    /api/analytics/trends    - Get trends
GET    /api/analytics/anomalies - Get anomalies

GET    /api/reports             - List reports
POST   /api/reports/generate    - Generate report
GET    /api/reports/{id}        - Get report
```

## Integration with iTechSmart Suite

iTechSmart Analytics integrates seamlessly with:

- **iTechSmart Enterprise**: Central data hub
- **iTechSmart Ninja**: Automated optimization insights
- **iTechSmart Supreme**: Healthcare analytics
- **iTechSmart HL7**: Medical data analysis
- **ProofLink.AI**: Document analytics
- **PassPort**: Identity analytics
- **ImpactOS**: Impact measurement
- **FitSnap.AI**: Fitness analytics

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.



## 🚀 Upcoming Features (v1.4.0)

1. **Real-time data streaming and processing**
2. **Custom visualization builder with templates**
3. **Machine learning models for predictive analytics**
4. **Advanced statistical analysis tools**
5. **Data export in multiple formats**
6. **Scheduled reports and dashboards**
7. **Natural language query interface**
8. **Integration with BI tools (Tableau, Power BI)**

**Product Value**: $2.2M  
**Tier**: 2  
**Total Features**: 8



## Coming in v1.5.0

**Release Date:** Q1 2025

### New Features

- AI-powered data insights
- Advanced ML model marketplace
- Enhanced real-time streaming
- Automated anomaly detection

### Enhancements

- Performance improvements across all modules
- Enhanced security features and compliance
- Improved user experience and interface
- Extended API capabilities and integrations

## License

Copyright © 2025 iTechSmart. All rights reserved.

## Support

- Documentation: https://docs.itechsmart.dev/analytics
- Email: support@itechsmart.dev
- Slack: #itechsmart-analytics
---

## 🔗 Integration Points

### Enterprise Hub Integration

iTechSmart Analytics integrates with iTechSmart Enterprise Hub for:

- **Centralized Management**: Register and manage from Hub dashboard
- **Health Monitoring**: Real-time health checks every 30 seconds
- **Metrics Reporting**: Send performance metrics to Hub
- **Configuration Updates**: Receive configuration from Hub
- **Cross-Product Workflows**: Participate in multi-product workflows
- **Unified Authentication**: Use PassPort for authentication via Hub

#### Hub Registration

On startup, iTechSmart Analytics automatically registers with Enterprise Hub:

```python
# Automatic registration on startup
{
  "product_id": "itechsmart-analytics",
  "product_name": "iTechSmart Analytics",
  "version": "1.0.0",
  "api_endpoint": "http://itechsmart-analytics:8080",
  "health_endpoint": "http://itechsmart-analytics:8080/health",
  "capabilities": ['ml_analytics', 'forecasting', 'anomaly_detection'],
  "status": "healthy"
}
```

### Ninja Integration

iTechSmart Analytics is monitored and managed by iTechSmart Ninja for:

- **Self-Healing**: Automatic detection and recovery from errors
- **Performance Optimization**: Continuous performance monitoring and optimization
- **Auto-Scaling**: Automatic scaling based on load
- **Error Detection**: Real-time error detection and alerting
- **Dependency Management**: Automatic dependency updates and patches
- **Resource Optimization**: Memory and CPU optimization

Provides ML-powered analytics for all products.

### Standalone Mode

iTechSmart Analytics can operate independently without Hub connection:

**Standalone Features:**
- ✅ Core functionality available
- ✅ Local configuration management
- ✅ File-based settings
- ✅ Offline operation
- ❌ No cross-product workflows
- ❌ No centralized monitoring
- ❌ Manual configuration updates

**Enable Standalone Mode:**
```bash
export ANALYTICS_HUB_ENABLED=false
export ANALYTICS_STANDALONE_MODE=true
```

---

## 🌐 Cross-Product Integration

### Integrated With

iTechSmart Analytics integrates with the following iTechSmart products:

**Core Integrations:**
- **Enterprise Hub**: Central management and monitoring
- **Ninja**: Self-healing and optimization
- **PassPort**: Authentication and authorization
- **Vault**: Secrets management

**Product-Specific Integrations:**
- **DataFlow**
- **Pulse**
- **All Products**

---

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

