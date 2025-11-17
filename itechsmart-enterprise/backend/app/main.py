"""
iTechSmart Enterprise - Main Application
FastAPI backend with integration management and Service Catalog
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

# Import API routers
from ..api.service_catalog import router as service_catalog_router
from .routers.system_agents import router as system_agents_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting iTechSmart Enterprise...")
    logger.info("✅ Application started successfully")
    yield
    logger.info("👋 Shutting down iTechSmart Enterprise...")


# Create FastAPI application
app = FastAPI(
    title="iTechSmart Enterprise API",
    description="Integration management platform with Service Catalog and ITIL alignment",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(service_catalog_router)
app.include_router(
    system_agents_router, prefix="/api/v1/system-agents", tags=["System Agents"]
)


# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0", "service": "iTechSmart Enterprise"}


# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "iTechSmart Enterprise API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Integration status endpoint
@app.get("/api/integrations/status")
async def get_integrations_status() -> Dict[str, Any]:
    """Get status of all integrations"""
    return {
        "integrations": [
            {
                "id": "servicenow",
                "name": "ServiceNow",
                "status": "not_configured",
                "type": "ITSM",
                "auth_type": "OAuth 2.0",
                "sync_type": "Bi-directional",
                "production_ready": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "zendesk",
                "name": "Zendesk",
                "status": "not_configured",
                "type": "Support",
                "auth_type": "OAuth 2.0",
                "sync_type": "Bi-directional",
                "production_ready": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "itglue",
                "name": "IT Glue",
                "status": "not_configured",
                "type": "Documentation",
                "auth_type": "API Key",
                "sync_type": "Uni-directional",
                "production_ready": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "nable",
                "name": "N-able",
                "status": "not_configured",
                "type": "RMM",
                "auth_type": "JWT",
                "sync_type": "Bi-directional",
                "production_ready": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "connectwise",
                "name": "ConnectWise",
                "status": "not_configured",
                "type": "PSA",
                "auth_type": "OAuth 2.0",
                "sync_type": "Bi-directional",
                "production_ready": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "sap",
                "name": "SAP",
                "status": "not_configured",
                "type": "ERP",
                "auth_type": "SAML 2.0",
                "sync_type": "Bi-directional",
                "production_ready": False,
                "beta": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "salesforce",
                "name": "Salesforce",
                "status": "not_configured",
                "type": "CRM",
                "auth_type": "OAuth 2.0",
                "sync_type": "Bi-directional",
                "production_ready": False,
                "beta": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "workday",
                "name": "Workday",
                "status": "not_configured",
                "type": "HR",
                "auth_type": "OAuth 2.0",
                "sync_type": "Uni-directional",
                "production_ready": False,
                "beta": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "jira",
                "name": "Jira",
                "status": "not_configured",
                "type": "Issue Tracking",
                "auth_type": "OAuth 2.0",
                "sync_type": "Bi-directional",
                "production_ready": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "slack",
                "name": "Slack",
                "status": "not_configured",
                "type": "Collaboration",
                "auth_type": "Webhooks",
                "sync_type": "Uni-directional",
                "production_ready": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "prometheus",
                "name": "Prometheus",
                "status": "not_configured",
                "type": "Monitoring",
                "auth_type": "Bearer Token",
                "sync_type": "Metrics",
                "production_ready": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
            {
                "id": "wazuh",
                "name": "Wazuh",
                "status": "not_configured",
                "type": "Security",
                "auth_type": "API Key",
                "sync_type": "Security Events",
                "production_ready": True,
                "last_sync": None,
                "success_rate": 0,
                "error_count": 0,
            },
        ],
        "summary": {
            "total": 12,
            "configured": 0,
            "active": 0,
            "errors": 0,
            "production_ready": 9,
            "beta": 3,
        },
    }


# Get specific integration details
@app.get("/api/integrations/{integration_id}")
async def get_integration_details(integration_id: str) -> Dict[str, Any]:
    """Get details for a specific integration"""

    integrations_config = {
        "servicenow": {
            "id": "servicenow",
            "name": "ServiceNow",
            "description": "Complete ITSM integration with ServiceNow",
            "status": "not_configured",
            "type": "ITSM",
            "auth_type": "OAuth 2.0",
            "sync_type": "Bi-directional",
            "production_ready": True,
            "configuration_fields": [
                {
                    "name": "instance_url",
                    "label": "Instance URL",
                    "type": "url",
                    "required": True,
                    "placeholder": "https://your-instance.service-now.com",
                    "help": "Your ServiceNow instance URL",
                },
                {
                    "name": "client_id",
                    "label": "Client ID",
                    "type": "text",
                    "required": True,
                    "placeholder": "Enter OAuth Client ID",
                    "help": "OAuth 2.0 Client ID from ServiceNow",
                },
                {
                    "name": "client_secret",
                    "label": "Client Secret",
                    "type": "password",
                    "required": True,
                    "placeholder": "Enter OAuth Client Secret",
                    "help": "OAuth 2.0 Client Secret from ServiceNow",
                },
                {
                    "name": "username",
                    "label": "Username",
                    "type": "text",
                    "required": True,
                    "placeholder": "integration.user",
                    "help": "ServiceNow integration user",
                },
                {
                    "name": "password",
                    "label": "Password",
                    "type": "password",
                    "required": True,
                    "placeholder": "Enter password",
                    "help": "ServiceNow user password",
                },
            ],
            "sync_options": [
                {"id": "incidents", "label": "Sync Incidents", "enabled": True},
                {"id": "changes", "label": "Sync Changes", "enabled": True},
                {"id": "problems", "label": "Sync Problems", "enabled": False},
                {"id": "knowledge", "label": "Sync Knowledge Base", "enabled": False},
                {"id": "users", "label": "Sync Users", "enabled": False},
            ],
            "documentation_url": "/docs/integrations/servicenow",
        },
        "zendesk": {
            "id": "zendesk",
            "name": "Zendesk",
            "description": "Support ticket integration with Zendesk",
            "status": "not_configured",
            "type": "Support",
            "auth_type": "API Token",
            "sync_type": "Bi-directional",
            "production_ready": True,
            "configuration_fields": [
                {
                    "name": "subdomain",
                    "label": "Subdomain",
                    "type": "text",
                    "required": True,
                    "placeholder": "your-company",
                    "help": "Your Zendesk subdomain (e.g., 'acme' from acme.zendesk.com)",
                },
                {
                    "name": "email",
                    "label": "Email",
                    "type": "email",
                    "required": True,
                    "placeholder": "admin@company.com",
                    "help": "Zendesk admin email",
                },
                {
                    "name": "api_token",
                    "label": "API Token",
                    "type": "password",
                    "required": True,
                    "placeholder": "Enter API token",
                    "help": "API token from Zendesk settings",
                },
            ],
            "sync_options": [
                {"id": "tickets", "label": "Sync Tickets", "enabled": True},
                {"id": "users", "label": "Sync Users", "enabled": True},
                {
                    "id": "organizations",
                    "label": "Sync Organizations",
                    "enabled": False,
                },
                {"id": "tags", "label": "Sync Tags", "enabled": False},
            ],
            "documentation_url": "/docs/integrations/zendesk",
        },
        "itglue": {
            "id": "itglue",
            "name": "IT Glue",
            "description": "Documentation platform integration",
            "status": "not_configured",
            "type": "Documentation",
            "auth_type": "API Key",
            "sync_type": "Uni-directional",
            "production_ready": True,
            "configuration_fields": [
                {
                    "name": "api_key",
                    "label": "API Key",
                    "type": "password",
                    "required": True,
                    "placeholder": "Enter API key",
                    "help": "API key from IT Glue",
                },
                {
                    "name": "api_url",
                    "label": "API URL",
                    "type": "url",
                    "required": False,
                    "placeholder": "https://api.itglue.com",
                    "help": "IT Glue API URL (use default unless custom)",
                },
            ],
            "sync_options": [
                {"id": "documentation", "label": "Sync Documentation", "enabled": True},
                {
                    "id": "configurations",
                    "label": "Sync Configurations",
                    "enabled": True,
                },
                {
                    "id": "passwords",
                    "label": "Sync Passwords (Encrypted)",
                    "enabled": False,
                },
            ],
            "documentation_url": "/docs/integrations/itglue",
        },
        "jira": {
            "id": "jira",
            "name": "Jira",
            "description": "Issue tracking and project management",
            "status": "not_configured",
            "type": "Issue Tracking",
            "auth_type": "OAuth 2.0",
            "sync_type": "Bi-directional",
            "production_ready": True,
            "configuration_fields": [
                {
                    "name": "site_url",
                    "label": "Site URL",
                    "type": "url",
                    "required": True,
                    "placeholder": "https://your-company.atlassian.net",
                    "help": "Your Jira site URL",
                },
                {
                    "name": "email",
                    "label": "Email",
                    "type": "email",
                    "required": True,
                    "placeholder": "admin@company.com",
                    "help": "Atlassian account email",
                },
                {
                    "name": "api_token",
                    "label": "API Token",
                    "type": "password",
                    "required": True,
                    "placeholder": "Enter API token",
                    "help": "API token from Atlassian account",
                },
            ],
            "sync_options": [
                {"id": "issues", "label": "Sync Issues", "enabled": True},
                {"id": "projects", "label": "Sync Projects", "enabled": True},
                {"id": "users", "label": "Sync Users", "enabled": False},
                {"id": "comments", "label": "Sync Comments", "enabled": True},
            ],
            "documentation_url": "/docs/integrations/jira",
        },
        "slack": {
            "id": "slack",
            "name": "Slack",
            "description": "Team collaboration and notifications",
            "status": "not_configured",
            "type": "Collaboration",
            "auth_type": "Webhooks",
            "sync_type": "Uni-directional",
            "production_ready": True,
            "configuration_fields": [
                {
                    "name": "webhook_url",
                    "label": "Webhook URL",
                    "type": "url",
                    "required": True,
                    "placeholder": "https://hooks.slack.com/services/...",
                    "help": "Incoming webhook URL from Slack",
                },
                {
                    "name": "bot_token",
                    "label": "Bot Token (Optional)",
                    "type": "password",
                    "required": False,
                    "placeholder": "xoxb-...",
                    "help": "Bot token for advanced features",
                },
            ],
            "sync_options": [
                {"id": "notifications", "label": "Send Notifications", "enabled": True},
                {"id": "commands", "label": "Receive Commands", "enabled": False},
                {
                    "id": "interactive",
                    "label": "Interactive Messages",
                    "enabled": False,
                },
            ],
            "documentation_url": "/docs/integrations/slack",
        },
        "prometheus": {
            "id": "prometheus",
            "name": "Prometheus",
            "description": "Metrics collection and monitoring",
            "status": "not_configured",
            "type": "Monitoring",
            "auth_type": "Bearer Token",
            "sync_type": "Metrics",
            "production_ready": True,
            "configuration_fields": [
                {
                    "name": "prometheus_url",
                    "label": "Prometheus URL",
                    "type": "url",
                    "required": True,
                    "placeholder": "http://prometheus:9090",
                    "help": "Prometheus server URL",
                },
                {
                    "name": "bearer_token",
                    "label": "Bearer Token (Optional)",
                    "type": "password",
                    "required": False,
                    "placeholder": "Enter bearer token",
                    "help": "Bearer token if authentication is enabled",
                },
            ],
            "sync_options": [
                {"id": "collect_metrics", "label": "Collect Metrics", "enabled": True},
                {"id": "query_metrics", "label": "Query Metrics", "enabled": True},
                {"id": "alerts", "label": "Alert on Thresholds", "enabled": True},
            ],
            "documentation_url": "/docs/integrations/prometheus",
        },
    }

    if integration_id not in integrations_config:
        raise HTTPException(status_code=404, detail="Integration not found")

    return integrations_config[integration_id]


# Test integration connection
@app.post("/api/integrations/{integration_id}/test")
async def test_integration_connection(
    integration_id: str, credentials: Dict[str, Any]
) -> Dict[str, Any]:
    """Test integration connection with provided credentials"""

    # This is a placeholder - in production, this would actually test the connection
    logger.info(f"Testing connection for {integration_id}")

    return {
        "success": True,
        "message": f"Successfully connected to {integration_id}",
        "details": {
            "response_time": "245ms",
            "api_version": "v1",
            "authenticated": True,
        },
    }


# Save integration configuration
@app.post("/api/integrations/{integration_id}/configure")
async def configure_integration(
    integration_id: str, config: Dict[str, Any]
) -> Dict[str, Any]:
    """Save integration configuration"""

    logger.info(f"Configuring {integration_id}")

    # In production, this would save to database with encryption
    return {
        "success": True,
        "message": f"{integration_id} configured successfully",
        "integration_id": integration_id,
        "status": "configured",
    }


# Get integration logs
@app.get("/api/integrations/{integration_id}/logs")
async def get_integration_logs(integration_id: str, limit: int = 100) -> Dict[str, Any]:
    """Get logs for a specific integration"""

    return {
        "integration_id": integration_id,
        "logs": [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "level": "INFO",
                "message": "Sync completed successfully",
                "records_synced": 150,
            },
            {
                "timestamp": "2024-01-15T10:25:00Z",
                "level": "INFO",
                "message": "Starting sync",
                "sync_type": "incremental",
            },
        ],
        "total": 2,
        "limit": limit,
    }


# Dashboard statistics
@app.get("/api/dashboard/stats")
async def get_dashboard_stats() -> Dict[str, Any]:
    """Get dashboard statistics"""

    return {
        "integrations": {"total": 12, "configured": 0, "active": 0, "errors": 0},
        "syncs": {"today": 0, "this_week": 0, "this_month": 0, "success_rate": 0},
        "records": {"total_synced": 0, "last_24h": 0},
        "health": {
            "status": "healthy",
            "uptime": "99.9%",
            "last_check": "2024-01-15T10:30:00Z",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
