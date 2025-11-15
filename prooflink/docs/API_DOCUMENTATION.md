# ProofLink.AI API Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Error Handling](#error-handling)
5. [Rate Limits](#rate-limits)
6. [Code Examples](#code-examples)
7. [Webhooks](#webhooks)
8. [SDKs](#sdks)

---

## Introduction

### Base URL
```
https://api.prooflink.ai/v1
```

### API Version
Current version: `v1`

### Content Type
All requests and responses use JSON:
```
Content-Type: application/json
```

### HTTPS Required
All API requests must be made over HTTPS. HTTP requests will be rejected.

---

## Authentication

### API Keys

ProofLink uses API keys for authentication. Include your API key in the `Authorization` header:

```bash
Authorization: Bearer YOUR_API_KEY
```

### Getting Your API Key

1. Log in to your ProofLink dashboard
2. Navigate to Settings → API Keys
3. Click "Create New API Key"
4. Copy and securely store your key

### Security Best Practices

- Never commit API keys to version control
- Store keys in environment variables
- Rotate keys regularly
- Use different keys for different environments
- Revoke compromised keys immediately

---

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Refresh Token
```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### Proofs

#### Create Proof
```http
POST /proofs
```

**Headers:**
```
Authorization: Bearer YOUR_API_KEY
Content-Type: multipart/form-data
```

**Request Body:**
```
file: [binary file data]
filename: "document.pdf" (optional)
description: "Contract for Project X" (optional)
tags: ["contract", "2024"] (optional)
```

**Response:**
```json
{
  "id": "proof_abc123",
  "filename": "document.pdf",
  "file_hash": "a3d5e7f9...",
  "proof_link": "https://prooflink.ai/verify/abc123",
  "created_at": "2024-01-15T10:30:00Z",
  "file_size": 1048576,
  "mime_type": "application/pdf"
}
```

#### Get Proof
```http
GET /proofs/{proof_id}
```

**Response:**
```json
{
  "id": "proof_abc123",
  "filename": "document.pdf",
  "file_hash": "a3d5e7f9...",
  "proof_link": "https://prooflink.ai/verify/abc123",
  "verification_count": 42,
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": null,
  "is_active": true,
  "file_size": 1048576,
  "mime_type": "application/pdf",
  "metadata": {
    "description": "Contract for Project X",
    "tags": ["contract", "2024"]
  }
}
```

#### List Proofs
```http
GET /proofs
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20, max: 100)
- `status`: Filter by status (`active`, `expired`)
- `search`: Search by filename
- `sort`: Sort by (`created_at`, `filename`, `verifications`)
- `order`: Sort order (`asc`, `desc`)

**Response:**
```json
{
  "data": [
    {
      "id": "proof_abc123",
      "filename": "document.pdf",
      "file_hash": "a3d5e7f9...",
      "proof_link": "https://prooflink.ai/verify/abc123",
      "verification_count": 42,
      "created_at": "2024-01-15T10:30:00Z",
      "is_active": true
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### Delete Proof
```http
DELETE /proofs/{proof_id}
```

**Response:**
```json
{
  "message": "Proof deleted successfully"
}
```

#### Batch Create Proofs
```http
POST /proofs/batch
```

**Request Body:**
```json
{
  "files": [
    {
      "filename": "doc1.pdf",
      "file_data": "base64_encoded_data"
    },
    {
      "filename": "doc2.pdf",
      "file_data": "base64_encoded_data"
    }
  ]
}
```

**Response:**
```json
{
  "proofs": [
    {
      "id": "proof_abc123",
      "filename": "doc1.pdf",
      "proof_link": "https://prooflink.ai/verify/abc123"
    },
    {
      "id": "proof_def456",
      "filename": "doc2.pdf",
      "proof_link": "https://prooflink.ai/verify/def456"
    }
  ],
  "total": 2,
  "successful": 2,
  "failed": 0
}
```

---

### Verification

#### Verify File
```http
POST /verify/{proof_link}
```

**Headers:**
```
Content-Type: multipart/form-data
```

**Request Body:**
```
file: [binary file data]
```

**Response:**
```json
{
  "is_valid": true,
  "proof_id": "proof_abc123",
  "filename": "document.pdf",
  "file_hash": "a3d5e7f9...",
  "verified_at": "2024-01-15T11:00:00Z",
  "message": "File verification successful"
}
```

#### Get Verification History
```http
GET /proofs/{proof_id}/verifications
```

**Response:**
```json
{
  "data": [
    {
      "id": "ver_xyz789",
      "verified_at": "2024-01-15T11:00:00Z",
      "is_valid": true,
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "total": 42
}
```

---

### User Management

#### Get Current User
```http
GET /users/me
```

**Response:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "subscription": {
    "plan": "pro",
    "status": "active",
    "expires_at": "2024-02-01T00:00:00Z"
  },
  "stats": {
    "total_proofs": 150,
    "total_verifications": 1234,
    "api_calls_today": 45
  }
}
```

#### Update User
```http
PUT /users/me
```

**Request Body:**
```json
{
  "name": "John Smith",
  "timezone": "America/New_York",
  "notifications_enabled": true
}
```

**Response:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Smith",
  "timezone": "America/New_York",
  "notifications_enabled": true
}
```

---

### API Keys

#### List API Keys
```http
GET /users/api-keys
```

**Response:**
```json
{
  "data": [
    {
      "id": "key_abc123",
      "name": "Production Server",
      "key": "pk_live_...",
      "created_at": "2024-01-01T00:00:00Z",
      "last_used_at": "2024-01-15T10:00:00Z",
      "usage_count": 1234,
      "is_active": true
    }
  ]
}
```

#### Create API Key
```http
POST /users/api-keys
```

**Request Body:**
```json
{
  "name": "Development Server"
}
```

**Response:**
```json
{
  "id": "key_def456",
  "name": "Development Server",
  "key": "pk_test_...",
  "created_at": "2024-01-15T12:00:00Z"
}
```

#### Delete API Key
```http
DELETE /users/api-keys/{key_id}
```

**Response:**
```json
{
  "message": "API key deleted successfully"
}
```

---

### Analytics

#### Get Overview
```http
GET /analytics/overview
```

**Query Parameters:**
- `start_date`: Start date (ISO 8601)
- `end_date`: End date (ISO 8601)

**Response:**
```json
{
  "total_proofs": 150,
  "total_verifications": 1234,
  "active_proofs": 142,
  "verification_trend": [
    {
      "date": "2024-01-01",
      "count": 45
    }
  ],
  "proof_types": [
    {
      "type": "application/pdf",
      "count": 89
    }
  ],
  "top_proofs": [
    {
      "id": "proof_abc123",
      "filename": "document.pdf",
      "verifications": 234
    }
  ]
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "invalid_request",
    "message": "The request is missing required parameters",
    "details": {
      "missing_fields": ["email", "password"]
    }
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### Error Codes

| Code | Description |
|------|-------------|
| `invalid_request` | Request is malformed or missing required fields |
| `authentication_failed` | Invalid credentials or API key |
| `unauthorized` | Valid credentials but insufficient permissions |
| `not_found` | Resource does not exist |
| `rate_limit_exceeded` | Too many requests |
| `file_too_large` | File exceeds size limit |
| `invalid_file_type` | File type not supported |
| `verification_failed` | File verification failed |

---

## Rate Limits

### Limits by Plan

| Plan | Requests/Hour | Requests/Day |
|------|---------------|--------------|
| Free | 100 | 1,000 |
| Pro | 1,000 | 10,000 |
| Enterprise | Custom | Custom |

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642262400
```

### Handling Rate Limits

When rate limited, you'll receive a 429 status code:

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "retry_after": 3600
  }
}
```

---

## Code Examples

### Python

```python
import requests

API_KEY = "your_api_key_here"
BASE_URL = "https://api.prooflink.ai/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Create a proof
with open("document.pdf", "rb") as file:
    files = {"file": file}
    response = requests.post(
        f"{BASE_URL}/proofs",
        headers={"Authorization": f"Bearer {API_KEY}"},
        files=files
    )
    proof = response.json()
    print(f"Proof created: {proof['proof_link']}")

# Verify a file
with open("document.pdf", "rb") as file:
    files = {"file": file}
    response = requests.post(
        f"{BASE_URL}/verify/abc123",
        files=files
    )
    result = response.json()
    print(f"Valid: {result['is_valid']}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_KEY = 'your_api_key_here';
const BASE_URL = 'https://api.prooflink.ai/v1';

// Create a proof
async function createProof(filePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));

  const response = await axios.post(`${BASE_URL}/proofs`, form, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      ...form.getHeaders()
    }
  });

  console.log('Proof created:', response.data.proof_link);
  return response.data;
}

// Verify a file
async function verifyFile(proofLink, filePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));

  const response = await axios.post(
    `${BASE_URL}/verify/${proofLink}`,
    form,
    { headers: form.getHeaders() }
  );

  console.log('Valid:', response.data.is_valid);
  return response.data;
}
```

### cURL

```bash
# Create a proof
curl -X POST https://api.prooflink.ai/v1/proofs \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@document.pdf"

# Verify a file
curl -X POST https://api.prooflink.ai/v1/verify/abc123 \
  -F "file=@document.pdf"

# List proofs
curl -X GET https://api.prooflink.ai/v1/proofs \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## Webhooks

### Setting Up Webhooks

1. Navigate to Settings → Webhooks
2. Click "Add Webhook"
3. Enter your endpoint URL
4. Select events to subscribe to
5. Save webhook

### Webhook Events

- `proof.created`: New proof created
- `proof.deleted`: Proof deleted
- `verification.completed`: File verified
- `verification.failed`: Verification failed

### Webhook Payload

```json
{
  "event": "verification.completed",
  "timestamp": "2024-01-15T12:00:00Z",
  "data": {
    "proof_id": "proof_abc123",
    "verification_id": "ver_xyz789",
    "is_valid": true,
    "verified_at": "2024-01-15T12:00:00Z"
  }
}
```

### Webhook Security

Verify webhook signatures using the `X-ProofLink-Signature` header:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## SDKs

### Official SDKs

- **Python**: `pip install prooflink`
- **JavaScript**: `npm install @prooflink/sdk`
- **Ruby**: `gem install prooflink`
- **PHP**: `composer require prooflink/sdk`
- **Go**: `go get github.com/prooflink/go-sdk`

### Community SDKs

- **Java**: Available on Maven Central
- **.NET**: Available on NuGet
- **Rust**: Available on crates.io

---

## Support

**Email**: api@prooflink.ai
**Documentation**: https://docs.prooflink.ai
**Status Page**: https://status.prooflink.ai
**GitHub**: https://github.com/prooflink

---

*Last Updated: January 2024*
*API Version: v1*