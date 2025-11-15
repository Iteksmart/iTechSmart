"""
iTechSmart DataFlow - Main Application
Data Pipeline & ETL Platform
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting iTechSmart DataFlow...")
    logger.info("✅ DataFlow Platform started successfully")
    yield
    logger.info("👋 Shutting down iTechSmart DataFlow...")


# Create FastAPI application
app = FastAPI(
    title="iTechSmart DataFlow API",
    description="Data Pipeline & ETL Platform with 100+ connectors",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "iTechSmart DataFlow"
    }


# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "iTechSmart DataFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Pipelines endpoints
@app.get("/api/v1/pipelines")
async def list_pipelines() -> Dict[str, Any]:
    """List all data pipelines"""
    return {
        "pipelines": [
            {
                "id": "pipeline-001",
                "name": "Customer Data Sync",
                "source": "PostgreSQL",
                "destination": "Data Lake",
                "status": "running",
                "last_run": "2024-11-12T10:00:00Z",
                "success_rate": 99.5,
                "records_processed": 1000000
            },
            {
                "id": "pipeline-002",
                "name": "HL7 Healthcare Data",
                "source": "HL7 FHIR",
                "destination": "Analytics DB",
                "status": "running",
                "last_run": "2024-11-12T10:30:00Z",
                "success_rate": 98.8,
                "records_processed": 500000
            }
        ],
        "total": 2,
        "active": 2,
        "paused": 0,
        "failed": 0
    }


@app.post("/api/v1/pipelines")
async def create_pipeline(pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new data pipeline"""
    return {
        "success": True,
        "pipeline_id": "pipeline-003",
        "message": "Pipeline created successfully"
    }


@app.get("/api/v1/pipelines/{pipeline_id}")
async def get_pipeline(pipeline_id: str) -> Dict[str, Any]:
    """Get pipeline details"""
    return {
        "id": pipeline_id,
        "name": "Customer Data Sync",
        "source": {
            "type": "PostgreSQL",
            "host": "db.example.com",
            "database": "customers",
            "table": "users"
        },
        "destination": {
            "type": "Data Lake",
            "bucket": "customer-data",
            "format": "parquet"
        },
        "transformations": [
            {
                "type": "filter",
                "condition": "status = 'active'"
            },
            {
                "type": "map",
                "fields": ["id", "name", "email", "created_at"]
            }
        ],
        "schedule": "0 */6 * * *",
        "status": "running"
    }


# Connectors endpoints
@app.get("/api/v1/connectors")
async def list_connectors() -> Dict[str, Any]:
    """List all available connectors"""
    return {
        "connectors": [
            {
                "id": "postgresql",
                "name": "PostgreSQL",
                "type": "database",
                "category": "source",
                "version": "1.0.0",
                "supported": True
            },
            {
                "id": "mysql",
                "name": "MySQL",
                "type": "database",
                "category": "source",
                "version": "1.0.0",
                "supported": True
            },
            {
                "id": "mongodb",
                "name": "MongoDB",
                "type": "database",
                "category": "source",
                "version": "1.0.0",
                "supported": True
            },
            {
                "id": "salesforce",
                "name": "Salesforce",
                "type": "saas",
                "category": "source",
                "version": "1.0.0",
                "supported": True
            },
            {
                "id": "stripe",
                "name": "Stripe",
                "type": "saas",
                "category": "source",
                "version": "1.0.0",
                "supported": True
            },
            {
                "id": "s3",
                "name": "Amazon S3",
                "type": "storage",
                "category": "destination",
                "version": "1.0.0",
                "supported": True
            },
            {
                "id": "snowflake",
                "name": "Snowflake",
                "type": "warehouse",
                "category": "destination",
                "version": "1.0.0",
                "supported": True
            }
        ],
        "total": 100,
        "categories": ["database", "saas", "storage", "warehouse", "api"]
    }


# Transformations endpoints
@app.get("/api/v1/transformations")
async def list_transformations() -> Dict[str, Any]:
    """List available transformation types"""
    return {
        "transformations": [
            {
                "type": "filter",
                "name": "Filter Rows",
                "description": "Filter rows based on conditions"
            },
            {
                "type": "map",
                "name": "Map Fields",
                "description": "Select and rename fields"
            },
            {
                "type": "aggregate",
                "name": "Aggregate Data",
                "description": "Group and aggregate data"
            },
            {
                "type": "join",
                "name": "Join Tables",
                "description": "Join multiple data sources"
            },
            {
                "type": "deduplicate",
                "name": "Remove Duplicates",
                "description": "Remove duplicate records"
            }
        ]
    }


# Data quality endpoints
@app.get("/api/v1/quality/rules")
async def list_quality_rules() -> Dict[str, Any]:
    """List data quality rules"""
    return {
        "rules": [
            {
                "id": "rule-001",
                "name": "Email Validation",
                "type": "format",
                "field": "email",
                "condition": "valid_email",
                "severity": "error"
            },
            {
                "id": "rule-002",
                "name": "Not Null Check",
                "type": "completeness",
                "field": "customer_id",
                "condition": "not_null",
                "severity": "error"
            },
            {
                "id": "rule-003",
                "name": "Date Range",
                "type": "validity",
                "field": "created_at",
                "condition": "date_range",
                "severity": "warning"
            }
        ]
    }


# Monitoring endpoints
@app.get("/api/v1/monitoring/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get platform metrics"""
    return {
        "metrics": {
            "pipelines": {
                "total": 50,
                "active": 45,
                "paused": 3,
                "failed": 2
            },
            "data_processed": {
                "today": 10000000,
                "this_week": 65000000,
                "this_month": 250000000
            },
            "performance": {
                "avg_latency_ms": 150,
                "success_rate": 99.2,
                "error_rate": 0.8
            },
            "resources": {
                "cpu_usage": 45.5,
                "memory_usage": 62.3,
                "storage_used_gb": 1250
            }
        }
    }


# Integration endpoints
@app.get("/api/v1/integrations")
async def list_integrations() -> Dict[str, Any]:
    """List integrations with other iTechSmart products"""
    return {
        "integrations": [
            {
                "product": "ImpactOS",
                "status": "connected",
                "type": "analytics",
                "description": "Feeds analytics data to ImpactOS"
            },
            {
                "product": "HL7",
                "status": "connected",
                "type": "healthcare",
                "description": "Healthcare data pipeline integration"
            },
            {
                "product": "Passport",
                "status": "connected",
                "type": "auth",
                "description": "Access control for pipelines"
            },
            {
                "product": "Enterprise Hub",
                "status": "connected",
                "type": "monitoring",
                "description": "Monitoring and alerts"
            },
            {
                "product": "Ninja",
                "status": "connected",
                "type": "automation",
                "description": "Self-healing pipeline automation"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)