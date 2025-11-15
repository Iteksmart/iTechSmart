"""
API Documentation Configuration
Enhanced OpenAPI/Swagger documentation
"""

from fastapi.openapi.utils import get_openapi
from typing import Dict, Any


def custom_openapi_schema(app) -> Dict[str, Any]:
    """
    Generate custom OpenAPI schema with enhanced documentation
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="iTechSmart HL7 API",
        version="1.0.0",
        description="""
# iTechSmart HL7 Healthcare Integration Platform

## Overview
iTechSmart HL7 is a comprehensive healthcare integration platform that connects to multiple Electronic Medical Record (EMR) systems and provides real-time data synchronization through HL7 messaging.

## Features
- **Multi-EMR Support**: Connect to Epic, Cerner, Meditech, Allscripts, and any HL7-compliant system
- **FHIR R4 Support**: Full support for FHIR R4 resources
- **HL7 v2.x Messaging**: Bidirectional HL7 messaging with MLLP protocol
- **Real-time Updates**: WebSocket support for live data streaming
- **Data Aggregation**: Combine patient data from multiple EMR sources
- **Self-Healing**: Autonomous error detection and recovery
- **AI-Powered**: Multi-agent AI system for intelligent data processing

## Authentication
All API endpoints (except `/health` and `/api/v1/auth/login`) require JWT authentication.

### Getting Started
1. Login to get JWT token: `POST /api/v1/auth/login`
2. Include token in Authorization header: `Bearer <token>`
3. Make API requests to protected endpoints

### Default Credentials
- **Admin**: username: `admin`, password: `admin123`
- **User**: username: `user`, password: `user123`

## Rate Limiting
API endpoints are rate-limited to prevent abuse:
- Connection management: 10 requests/minute
- Patient queries: 100 requests/minute
- Search operations: 50 requests/minute
- General endpoints: 30 requests/minute

## WebSocket Channels
Real-time updates are available through WebSocket connections:
- `default`: General updates
- `hl7`: HL7 message events
- `patients`: Patient data updates
- `observations`: New observations
- `medications`: Medication events
- `connections`: EMR connection status
- `alerts`: System alerts

## EMR Systems Supported
1. **Epic** - FHIR R4 API
2. **Cerner** - FHIR R4 API (Oracle Health)
3. **Meditech** - FHIR + HL7 v2.x
4. **Allscripts** - Unity API
5. **Generic HL7** - Any HL7 v2.x compliant system

## Data Types
- Patient Demographics
- Observations (Vitals, Labs)
- Medications
- Allergies
- Conditions/Problems
- Encounters/Visits
- Immunizations
- Documents

## Error Codes
- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Missing or invalid token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error

## Support
For support and documentation, visit: https://itechsmart.dev/docs
        """,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token obtained from /api/v1/auth/login"
        }
    }
    
    # Add security to all endpoints except public ones
    public_paths = ["/", "/health", "/api/v1/auth/login", "/docs", "/redoc", "/openapi.json"]
    
    for path in openapi_schema["paths"]:
        if path not in public_paths:
            for method in openapi_schema["paths"][path]:
                if method != "options":
                    openapi_schema["paths"][path][method]["security"] = [{"bearerAuth": []}]
    
    # Add tags metadata
    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "Authentication and authorization endpoints"
        },
        {
            "name": "api",
            "description": "Main API endpoints for EMR integration"
        },
        {
            "name": "websocket",
            "description": "WebSocket endpoints for real-time updates"
        }
    ]
    
    # Add examples
    openapi_schema["components"]["examples"] = {
        "LoginRequest": {
            "value": {
                "username": "admin",
                "password": "admin123"
            }
        },
        "ConnectionConfig": {
            "value": {
                "connection_id": "epic_main",
                "emr_type": "epic",
                "config": {
                    "base_url": "https://fhir.epic.com",
                    "client_id": "your_client_id",
                    "client_secret": "your_client_secret"
                }
            }
        },
        "PatientSearchRequest": {
            "value": {
                "criteria": {
                    "name": "Smith",
                    "birthdate": "1980-01-01",
                    "gender": "male"
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# API documentation metadata
api_metadata = {
    "title": "iTechSmart HL7 API",
    "version": "1.0.0",
    "description": "Healthcare Integration Platform API",
    "contact": {
        "name": "iTechSmart Support",
        "email": "support@itechsmart.dev",
        "url": "https://itechsmart.dev"
    },
    "license": {
        "name": "Proprietary",
        "url": "https://itechsmart.dev/license"
    }
}


# Example requests and responses
example_requests = {
    "login": {
        "username": "admin",
        "password": "admin123"
    },
    "create_connection": {
        "connection_id": "epic_main",
        "emr_type": "epic",
        "config": {
            "base_url": "https://fhir.epic.com",
            "client_id": "your_client_id",
            "client_secret": "your_client_secret"
        }
    },
    "search_patients": {
        "criteria": {
            "name": "Smith",
            "birthdate": "1980-01-01"
        }
    },
    "aggregate_data": {
        "patient_identifiers": {
            "epic_main": "epic_patient_123",
            "cerner_main": "cerner_patient_456"
        }
    }
}


example_responses = {
    "login_success": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {
            "username": "admin",
            "email": "admin@itechsmart.dev",
            "full_name": "Admin User",
            "disabled": False,
            "roles": ["admin", "user"]
        }
    },
    "patient": {
        "id": "patient_123",
        "mrn": "MRN123456",
        "name": "John Smith",
        "gender": "male",
        "birth_date": "1980-01-01",
        "phone": "555-1234",
        "email": "john.smith@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Boston",
            "state": "MA",
            "zip": "02101"
        }
    },
    "observation": {
        "id": "obs_123",
        "code": {
            "system": "http://loinc.org",
            "code": "8867-4",
            "display": "Heart rate"
        },
        "value": 72,
        "unit": "beats/minute",
        "date": "2024-01-15T10:30:00Z",
        "status": "final",
        "category": "vital-signs"
    }
}