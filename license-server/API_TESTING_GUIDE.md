# iTechSmart License Server - API Testing Guide

## Overview
This guide provides comprehensive testing procedures for all API endpoints of the iTechSmart License Server.

## Prerequisites

- License server running (locally or production)
- curl or Postman installed
- Admin credentials

## Base URL

**Local Development:**
```
http://localhost:3001
```

**Production:**
```
https://licenses.yourdomain.com
```

## Authentication Flow

### 1. Register Organization (First Time Setup)

**Endpoint:** `POST /api/auth/register`

**Request:**
```bash
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "domain": "acme.com",
    "email": "admin@acme.com",
    "password": "SecurePassword123!",
    "phone": "+1-555-0100",
    "address": "123 Main St, San Francisco, CA 94105",
    "country": "USA"
  }'
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "message": "Organization registered successfully",
  "data": {
    "organization": {
      "id": "org_123abc",
      "name": "Acme Corporation",
      "domain": "acme.com",
      "email": "admin@acme.com"
    },
    "user": {
      "id": "user_456def",
      "email": "admin@acme.com",
      "name": "Admin User",
      "role": "admin"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2. Login

**Endpoint:** `POST /api/auth/login`

**Request:**
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_456def",
      "email": "admin@acme.com",
      "name": "Admin User",
      "role": "admin",
      "organizationId": "org_123abc"
    }
  }
}
```

**Save the token for subsequent requests:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Refresh Token

**Endpoint:** `POST /api/auth/refresh`

**Request:**
```bash
curl -X POST http://localhost:3001/api/auth/refresh \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

## License Management

### 1. Create License

**Endpoint:** `POST /api/licenses`

**Request:**
```bash
curl -X POST http://localhost:3001/api/licenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "tier": "PROFESSIONAL",
    "maxUsers": 25,
    "maxProducts": 10,
    "maxApiCalls": 100000,
    "maxStorage": 107374182400,
    "allowedProducts": [
      "itechsmart-analytics",
      "itechsmart-copilot",
      "itechsmart-shield"
    ],
    "features": {
      "advancedAnalytics": true,
      "customBranding": true,
      "prioritySupport": true,
      "apiAccess": true
    },
    "expiresAt": "2025-12-31T23:59:59Z",
    "maxMachines": 5
  }'
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "message": "License created successfully",
  "data": {
    "id": "lic_789ghi",
    "licenseKey": "ITSM-PROF-XXXX-XXXX-XXXX-XXXX",
    "organizationId": "org_123abc",
    "tier": "PROFESSIONAL",
    "status": "ACTIVE",
    "maxUsers": 25,
    "maxProducts": 10,
    "maxApiCalls": 100000,
    "maxStorage": "107374182400",
    "allowedProducts": [
      "itechsmart-analytics",
      "itechsmart-copilot",
      "itechsmart-shield"
    ],
    "features": {
      "advancedAnalytics": true,
      "customBranding": true,
      "prioritySupport": true,
      "apiAccess": true
    },
    "startDate": "2024-11-16T16:30:00.000Z",
    "expiresAt": "2025-12-31T23:59:59.000Z",
    "maxMachines": 5,
    "createdAt": "2024-11-16T16:30:00.000Z"
  }
}
```

### 2. Validate License

**Endpoint:** `POST /api/licenses/validate`

**Request:**
```bash
curl -X POST http://localhost:3001/api/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{
    "licenseKey": "ITSM-PROF-XXXX-XXXX-XXXX-XXXX",
    "productId": "itechsmart-analytics",
    "machineId": "machine-abc-123",
    "version": "1.0.0"
  }'
```

**Expected Response (200 OK - Valid License):**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "license": {
      "id": "lic_789ghi",
      "tier": "PROFESSIONAL",
      "status": "ACTIVE",
      "expiresAt": "2025-12-31T23:59:59.000Z",
      "features": {
        "advancedAnalytics": true,
        "customBranding": true,
        "prioritySupport": true,
        "apiAccess": true
      }
    },
    "organization": {
      "id": "org_123abc",
      "name": "Acme Corporation",
      "domain": "acme.com"
    },
    "limits": {
      "maxUsers": 25,
      "maxProducts": 10,
      "maxApiCalls": 100000,
      "maxStorage": "107374182400"
    },
    "usage": {
      "currentUsers": 5,
      "currentProducts": 3,
      "apiCallsToday": 1250,
      "storageUsed": "5368709120"
    }
  }
}
```

**Expected Response (400 Bad Request - Invalid License):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_LICENSE",
    "message": "License key is invalid or expired",
    "details": {
      "reason": "expired",
      "expiredAt": "2024-10-31T23:59:59.000Z"
    }
  }
}
```

### 3. Get License Details

**Endpoint:** `GET /api/licenses/:id`

**Request:**
```bash
curl -X GET http://localhost:3001/api/licenses/lic_789ghi \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "lic_789ghi",
    "licenseKey": "ITSM-PROF-XXXX-XXXX-XXXX-XXXX",
    "organizationId": "org_123abc",
    "tier": "PROFESSIONAL",
    "status": "ACTIVE",
    "maxUsers": 25,
    "maxProducts": 10,
    "allowedProducts": [
      "itechsmart-analytics",
      "itechsmart-copilot",
      "itechsmart-shield"
    ],
    "features": {
      "advancedAnalytics": true,
      "customBranding": true,
      "prioritySupport": true
    },
    "startDate": "2024-11-16T16:30:00.000Z",
    "expiresAt": "2025-12-31T23:59:59.000Z",
    "machineIds": ["machine-abc-123"],
    "maxMachines": 5,
    "createdAt": "2024-11-16T16:30:00.000Z",
    "updatedAt": "2024-11-16T16:30:00.000Z",
    "lastValidated": "2024-11-16T16:35:00.000Z"
  }
}
```

### 4. Update License

**Endpoint:** `PUT /api/licenses/:id`

**Request:**
```bash
curl -X PUT http://localhost:3001/api/licenses/lic_789ghi \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "maxUsers": 50,
    "maxProducts": 15,
    "expiresAt": "2026-12-31T23:59:59Z",
    "features": {
      "advancedAnalytics": true,
      "customBranding": true,
      "prioritySupport": true,
      "apiAccess": true,
      "whiteLabeling": true
    }
  }'
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "License updated successfully",
  "data": {
    "id": "lic_789ghi",
    "maxUsers": 50,
    "maxProducts": 15,
    "expiresAt": "2026-12-31T23:59:59.000Z",
    "features": {
      "advancedAnalytics": true,
      "customBranding": true,
      "prioritySupport": true,
      "apiAccess": true,
      "whiteLabeling": true
    },
    "updatedAt": "2024-11-16T16:40:00.000Z"
  }
}
```

### 5. Revoke License

**Endpoint:** `DELETE /api/licenses/:id`

**Request:**
```bash
curl -X DELETE http://localhost:3001/api/licenses/lic_789ghi \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "License revoked successfully",
  "data": {
    "id": "lic_789ghi",
    "status": "CANCELLED",
    "revokedAt": "2024-11-16T16:45:00.000Z"
  }
}
```

## Organization Management

### 1. Get Organization Details

**Endpoint:** `GET /api/organizations/:id`

**Request:**
```bash
curl -X GET http://localhost:3001/api/organizations/org_123abc \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "org_123abc",
    "name": "Acme Corporation",
    "domain": "acme.com",
    "email": "admin@acme.com",
    "phone": "+1-555-0100",
    "address": "123 Main St, San Francisco, CA 94105",
    "country": "USA",
    "stripeCustomerId": "cus_xyz789",
    "createdAt": "2024-11-16T16:00:00.000Z",
    "updatedAt": "2024-11-16T16:00:00.000Z",
    "stats": {
      "totalLicenses": 3,
      "activeLicenses": 2,
      "totalUsers": 15,
      "totalApiCalls": 45000
    }
  }
}
```

### 2. Update Organization

**Endpoint:** `PUT /api/organizations/:id`

**Request:**
```bash
curl -X PUT http://localhost:3001/api/organizations/org_123abc \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Acme Corporation Inc.",
    "phone": "+1-555-0200",
    "address": "456 Market St, San Francisco, CA 94105"
  }'
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "Organization updated successfully",
  "data": {
    "id": "org_123abc",
    "name": "Acme Corporation Inc.",
    "phone": "+1-555-0200",
    "address": "456 Market St, San Francisco, CA 94105",
    "updatedAt": "2024-11-16T16:50:00.000Z"
  }
}
```

### 3. List Organization Licenses

**Endpoint:** `GET /api/organizations/:id/licenses`

**Request:**
```bash
curl -X GET "http://localhost:3001/api/organizations/org_123abc/licenses?status=ACTIVE&limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "licenses": [
      {
        "id": "lic_789ghi",
        "licenseKey": "ITSM-PROF-XXXX-XXXX-XXXX-XXXX",
        "tier": "PROFESSIONAL",
        "status": "ACTIVE",
        "expiresAt": "2025-12-31T23:59:59.000Z",
        "createdAt": "2024-11-16T16:30:00.000Z"
      },
      {
        "id": "lic_101jkl",
        "licenseKey": "ITSM-ENTP-YYYY-YYYY-YYYY-YYYY",
        "tier": "ENTERPRISE",
        "status": "ACTIVE",
        "expiresAt": "2026-06-30T23:59:59.000Z",
        "createdAt": "2024-11-16T15:00:00.000Z"
      }
    ],
    "pagination": {
      "total": 2,
      "limit": 10,
      "offset": 0,
      "hasMore": false
    }
  }
}
```

## Usage Tracking

### 1. Record Usage Event

**Endpoint:** `POST /api/usage`

**Request:**
```bash
curl -X POST http://localhost:3001/api/usage \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "licenseId": "lic_789ghi",
    "productId": "itechsmart-analytics",
    "eventType": "api_call",
    "quantity": 1,
    "metadata": {
      "endpoint": "/api/reports/generate",
      "duration": 1250,
      "statusCode": 200
    }
  }'
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "message": "Usage recorded successfully",
  "data": {
    "id": "usage_202mno",
    "licenseId": "lic_789ghi",
    "productId": "itechsmart-analytics",
    "eventType": "api_call",
    "quantity": 1,
    "recordedAt": "2024-11-16T16:55:00.000Z"
  }
}
```

### 2. Get Usage Statistics

**Endpoint:** `GET /api/usage/:licenseId`

**Request:**
```bash
curl -X GET "http://localhost:3001/api/usage/lic_789ghi?startDate=2024-11-01&endDate=2024-11-30&groupBy=day" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "licenseId": "lic_789ghi",
    "period": {
      "startDate": "2024-11-01T00:00:00.000Z",
      "endDate": "2024-11-30T23:59:59.000Z"
    },
    "summary": {
      "totalApiCalls": 45000,
      "totalStorageUsed": "5368709120",
      "totalUsers": 15,
      "averageDailyApiCalls": 1500
    },
    "breakdown": [
      {
        "date": "2024-11-16",
        "apiCalls": 1250,
        "storageUsed": "5368709120",
        "activeUsers": 15
      }
    ],
    "byProduct": {
      "itechsmart-analytics": {
        "apiCalls": 30000,
        "percentage": 66.7
      },
      "itechsmart-copilot": {
        "apiCalls": 10000,
        "percentage": 22.2
      },
      "itechsmart-shield": {
        "apiCalls": 5000,
        "percentage": 11.1
      }
    }
  }
}
```

## Webhook Management

### 1. Create Webhook

**Endpoint:** `POST /api/webhooks`

**Request:**
```bash
curl -X POST http://localhost:3001/api/webhooks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "url": "https://your-app.com/webhooks/license-events",
    "events": [
      "license.activated",
      "license.expired",
      "license.suspended",
      "license.renewed"
    ],
    "secret": "your-webhook-secret-key"
  }'
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "message": "Webhook created successfully",
  "data": {
    "id": "webhook_303pqr",
    "organizationId": "org_123abc",
    "url": "https://your-app.com/webhooks/license-events",
    "events": [
      "license.activated",
      "license.expired",
      "license.suspended",
      "license.renewed"
    ],
    "isActive": true,
    "createdAt": "2024-11-16T17:00:00.000Z"
  }
}
```

### 2. List Webhooks

**Endpoint:** `GET /api/webhooks`

**Request:**
```bash
curl -X GET http://localhost:3001/api/webhooks \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "webhooks": [
      {
        "id": "webhook_303pqr",
        "url": "https://your-app.com/webhooks/license-events",
        "events": [
          "license.activated",
          "license.expired",
          "license.suspended",
          "license.renewed"
        ],
        "isActive": true,
        "lastTriggered": "2024-11-16T16:45:00.000Z",
        "successCount": 125,
        "failureCount": 2,
        "createdAt": "2024-11-16T17:00:00.000Z"
      }
    ]
  }
}
```

### 3. Delete Webhook

**Endpoint:** `DELETE /api/webhooks/:id`

**Request:**
```bash
curl -X DELETE http://localhost:3001/api/webhooks/webhook_303pqr \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "Webhook deleted successfully"
}
```

## Health Check

**Endpoint:** `GET /health`

**Request:**
```bash
curl -X GET http://localhost:3001/health
```

**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-16T17:05:00.000Z",
  "uptime": 3600,
  "database": "connected",
  "version": "1.0.0"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions"
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

### 429 Too Many Requests
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retryAfter": 60
  }
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

## Postman Collection

Import this collection into Postman for easy testing:

```json
{
  "info": {
    "name": "iTechSmart License Server API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:3001"
    },
    {
      "key": "token",
      "value": ""
    }
  ]
}
```

## Automated Testing Script

```bash
#!/bin/bash

BASE_URL="http://localhost:3001"
EMAIL="test@example.com"
PASSWORD="TestPassword123!"

echo "=== iTechSmart License Server API Test Suite ==="

# 1. Register
echo -e "\n1. Testing Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    &quot;name&quot;: &quot;Test Company&quot;,
    &quot;domain&quot;: &quot;test.com&quot;,
    &quot;email&quot;: &quot;$EMAIL&quot;,
    &quot;password&quot;: &quot;$PASSWORD&quot;
  }")

echo "$REGISTER_RESPONSE" | jq .

# 2. Login
echo -e "\n2. Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    &quot;email&quot;: &quot;$EMAIL&quot;,
    &quot;password&quot;: &quot;$PASSWORD&quot;
  }")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.token')
echo "Token: $TOKEN"

# 3. Create License
echo -e "\n3. Testing License Creation..."
LICENSE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/licenses" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "tier": "PROFESSIONAL",
    "maxUsers": 10,
    "maxProducts": 5
  }')

LICENSE_KEY=$(echo "$LICENSE_RESPONSE" | jq -r '.data.licenseKey')
echo "License Key: $LICENSE_KEY"

# 4. Validate License
echo -e "\n4. Testing License Validation..."
VALIDATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/licenses/validate" \
  -H "Content-Type: application/json" \
  -d "{
    &quot;licenseKey&quot;: &quot;$LICENSE_KEY&quot;,
    &quot;productId&quot;: &quot;itechsmart-analytics&quot;,
    &quot;machineId&quot;: &quot;test-machine-123&quot;
  }")

echo "$VALIDATE_RESPONSE" | jq .

# 5. Health Check
echo -e "\n5. Testing Health Check..."
HEALTH_RESPONSE=$(curl -s -X GET "$BASE_URL/health")
echo "$HEALTH_RESPONSE" | jq .

echo -e "\n=== Test Suite Complete ==="
```

Save as `test-api.sh` and run:
```bash
chmod +x test-api.sh
./test-api.sh
```

## Performance Testing

Use Apache Bench for load testing:

```bash
# Test license validation endpoint
ab -n 1000 -c 10 -p license-validate.json -T application/json \
  http://localhost:3001/api/licenses/validate

# Test health endpoint
ab -n 10000 -c 100 http://localhost:3001/health
```

## Security Testing

### Test Rate Limiting
```bash
# Should return 429 after 100 requests in 15 minutes
for i in {1..150}; do
  curl -X GET http://localhost:3001/health
  echo "Request $i"
done
```

### Test JWT Expiration
```bash
# Use an expired token
curl -X GET http://localhost:3001/api/licenses \
  -H "Authorization: Bearer expired_token_here"
```

### Test SQL Injection
```bash
# Should be properly sanitized
curl -X POST http://localhost:3001/api/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{
    "licenseKey": "ITSM-TEST&quot;; DROP TABLE licenses; --",
    "productId": "test"
  }'
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/Iteksmart/iTechSmart/issues
- Email: support@itechsmart.com