# Itechsmart Forge - API Documentation

**Version**: 1.0.0  
**Last Updated**: November 17, 2025  
**Base URL**: http://localhost:8002

---

## 📚 Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Request/Response Format](#requestresponse-format)
4. [Error Codes](#error-codes)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)

---

## Authentication

### API Key Authentication

```bash
# Include API key in header
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8002/api/endpoint
```

### JWT Token Authentication

```bash
# Get token
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}

# Use token
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  http://localhost:8002/api/endpoint
```

---

## Endpoints

### Health Check

```
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-17T00:00:00Z"
}
```

### Resources

#### List Resources

```
GET /api/resources
```

**Parameters**:
- `param1` (string, required): Description
- `param2` (integer, optional): Description

**Request Body**:
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "123",
    "created_at": "2025-11-17T00:00:00Z"
  }
}
```

---

## Request/Response Format

### Request Headers

```
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN
Accept: application/json
```

### Response Format

**Success Response**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## Rate Limiting

- **Rate Limit**: 100 requests per minute
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

---

## Examples

### Example 1: Create Resource

```bash
curl -X POST http://localhost:8002/api/resources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Resource",
    "type": "example"
  }'
```

### Example 2: List Resources

```bash
curl -X GET "http://localhost:8002/api/resources?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example 3: Update Resource

```bash
curl -X PUT http://localhost:8002/api/resources/123 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name"
  }'
```

### Example 4: Delete Resource

```bash
curl -X DELETE http://localhost:8002/api/resources/123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## SDKs and Libraries

### Python

```python
from itechsmart import Itechsmart_ForgeClient

client = Itechsmart_ForgeClient(api_key="YOUR_API_KEY")
result = client.resources.create(name="My Resource")
```

### JavaScript

```javascript
const { Itechsmart_ForgeClient } = require('@itechsmart/itechsmart-forge');

const client = new Itechsmart_ForgeClient({ apiKey: 'YOUR_API_KEY' });
const result = await client.resources.create({ name: 'My Resource' });
```

---

## Webhooks

### Webhook Events

- `resource.created`
- `resource.updated`
- `resource.deleted`

### Webhook Payload

```json
{
  "event": "resource.created",
  "timestamp": "2025-11-17T00:00:00Z",
  "data": {
    "id": "123",
    "name": "My Resource"
  }
}
```

---

## Support

- **Documentation**: https://docs.itechsmart.com
- **API Status**: https://status.itechsmart.com
- **Support**: support@itechsmart.com

---

**End of API Documentation**