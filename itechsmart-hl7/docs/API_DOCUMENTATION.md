# iTechSmart HL7 API Documentation

## Overview

iTechSmart HL7 provides a comprehensive REST API for healthcare integration, clinical workflows, and decision support. This documentation covers all available endpoints, request/response formats, and authentication requirements.

**Base URL:** `https://api.itechsmart.example.com`  
**API Version:** v1  
**Authentication:** JWT Bearer Token

---

## Table of Contents

1. [Authentication](#authentication)
2. [Core API Endpoints](#core-api-endpoints)
3. [EMR Integration Endpoints](#emr-integration-endpoints)
4. [Clinical Workflows](#clinical-workflows)
5. [Drug Interaction Checker](#drug-interaction-checker)
6. [AI Clinical Insights](#ai-clinical-insights)
7. [Clinical Decision Support](#clinical-decision-support)
8. [Care Coordination](#care-coordination)
9. [WebSocket API](#websocket-api)
10. [Error Handling](#error-handling)
11. [Rate Limiting](#rate-limiting)

---

## Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "username": "john.doe",
    "email": "john.doe@example.com",
    "role": "physician"
  }
}
```

### Using the Token
Include the token in the Authorization header for all subsequent requests:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Core API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "emr_connections": "healthy"
  }
}
```

### Get System Statistics
```http
GET /api/statistics
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_patients": 1250,
  "active_connections": 5,
  "messages_processed_today": 3420,
  "workflows_active": 45,
  "drug_checks_today": 892
}
```

---

## EMR Integration Endpoints

### List EMR Connections
```http
GET /api/connections
Authorization: Bearer {token}
```

**Response:**
```json
{
  "connections": [
    {
      "id": "conn_123",
      "emr_system": "epic",
      "name": "Epic Production",
      "status": "active",
      "last_sync": "2025-01-15T10:25:00Z",
      "messages_processed": 1523
    }
  ],
  "total": 1
}
```

### Create EMR Connection
```http
POST /api/connections
Authorization: Bearer {token}
Content-Type: application/json

{
  "emr_system": "epic",
  "name": "Epic Production",
  "base_url": "https://fhir.epic.com",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

### Get Patient Data
```http
GET /api/patients/{patient_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "patient": {
    "id": "PAT123",
    "mrn": "MRN-001234",
    "name": "John Doe",
    "date_of_birth": "1980-05-15",
    "gender": "male",
    "contact": {
      "phone": "+1-555-0123",
      "email": "john.doe@example.com"
    }
  }
}
```

### Get Patient Observations
```http
GET /api/patients/{patient_id}/observations
Authorization: Bearer {token}
```

**Response:**
```json
{
  "observations": [
    {
      "id": "obs_123",
      "type": "vital_signs",
      "code": "85354-9",
      "display": "Blood Pressure",
      "value": "120/80",
      "unit": "mmHg",
      "timestamp": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

## Clinical Workflows

### Get Workflow Templates
```http
GET /api/clinicals/workflows/templates
Authorization: Bearer {token}
```

**Response:**
```json
{
  "templates": [
    {
      "workflow_id": "template_admission",
      "name": "Patient Admission",
      "description": "Standard patient admission workflow",
      "category": "admission",
      "total_steps": 5
    },
    {
      "workflow_id": "template_discharge",
      "name": "Patient Discharge",
      "description": "Standard patient discharge workflow",
      "category": "discharge",
      "total_steps": 5
    },
    {
      "workflow_id": "template_sepsis",
      "name": "Sepsis Protocol",
      "description": "Time-critical sepsis management protocol",
      "category": "emergency",
      "total_steps": 5
    }
  ]
}
```

### Create Workflow
```http
POST /api/clinicals/workflows
Authorization: Bearer {token}
Content-Type: application/json

{
  "template_id": "admission",
  "patient_id": "PAT123",
  "created_by": "Dr. Smith"
}
```

**Response:**
```json
{
  "workflow": {
    "workflow_id": "admission_PAT123_1705315200",
    "name": "Patient Admission",
    "status": "in_progress",
    "patient_id": "PAT123",
    "created_by": "Dr. Smith",
    "started_at": "2025-01-15T10:00:00Z",
    "steps": [
      {
        "step_id": "admission_001",
        "title": "Initial Assessment",
        "status": "pending",
        "required": true
      }
    ],
    "progress": {
      "total_steps": 5,
      "completed_steps": 0,
      "progress_percentage": 0
    }
  }
}
```

### Start Workflow Step
```http
POST /api/clinicals/workflows/{workflow_id}/steps/{step_id}/start
Authorization: Bearer {token}
Content-Type: application/json

{
  "assigned_to": "Nurse Johnson"
}
```

### Complete Workflow Step
```http
POST /api/clinicals/workflows/{workflow_id}/steps/{step_id}/complete
Authorization: Bearer {token}
Content-Type: application/json

{
  "result": {
    "vital_signs": {
      "blood_pressure": "120/80",
      "heart_rate": 72,
      "temperature": 37.0
    }
  },
  "notes": "Patient stable, vital signs within normal limits"
}
```

---

## Drug Interaction Checker

### Comprehensive Drug Check
```http
POST /api/clinicals/drug-check
Authorization: Bearer {token}
Content-Type: application/json

{
  "new_medication": "warfarin",
  "current_medications": ["aspirin", "lisinopril"],
  "allergies": ["penicillin"],
  "is_pregnant": false,
  "creatinine_clearance": 60.0
}
```

**Response:**
```json
{
  "medication": "warfarin",
  "safety_status": "MAJOR_CONCERNS",
  "recommendation": "CAUTION - Major interactions detected. Review carefully before prescribing.",
  "total_interactions": 1,
  "interactions_by_severity": {
    "contraindicated": 0,
    "major": 1,
    "moderate": 0,
    "minor": 0
  },
  "interactions": [
    {
      "interaction_id": "DDI_001",
      "interaction_type": "drug_drug",
      "severity": "major",
      "drug1": "warfarin",
      "drug2": "aspirin",
      "description": "Warfarin + Aspirin increases bleeding risk",
      "clinical_effects": "Increased risk of major bleeding, GI bleeding, intracranial hemorrhage",
      "management": "Monitor INR closely. Consider alternative antiplatelet if possible. Use lowest effective aspirin dose.",
      "references": ["Micromedex", "Lexicomp"]
    }
  ],
  "checked_at": "2025-01-15T10:00:00Z"
}
```

### Check Drug-Drug Interactions
```http
POST /api/clinicals/drug-check/drug-drug
Authorization: Bearer {token}
Content-Type: application/json

{
  "medications": ["warfarin", "aspirin", "lisinopril"]
}
```

---

## AI Clinical Insights

### Predict Sepsis Risk
```http
POST /api/clinicals/ai-insights/sepsis-risk
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": "PAT123",
  "vital_signs": {
    "respiratory_rate": 24,
    "heart_rate": 105,
    "systolic_bp": 95,
    "temperature": 38.5,
    "gcs": 15
  },
  "lab_results": {
    "wbc": 15.0,
    "lactate": 3.5
  }
}
```

**Response:**
```json
{
  "insight": {
    "insight_id": "SEPSIS_RISK_PAT123_1705315200",
    "insight_type": "risk_prediction",
    "title": "Sepsis Risk Assessment",
    "description": "qSOFA Score: 2/3, SIRS Score: 3/4",
    "risk_level": "high",
    "confidence": 0.85,
    "evidence": [
      "Elevated respiratory rate: 24 breaths/min (≥22)",
      "Hypotension: SBP 95 mmHg (≤100)",
      "Abnormal temperature: 38.5°C",
      "Tachycardia: 105 bpm (>90)",
      "Abnormal WBC: 15.0 K/μL",
      "Elevated lactate: 3.5 mmol/L (>2.0)"
    ],
    "recommendations": [
      "IMMEDIATE: Activate sepsis protocol",
      "Obtain blood cultures before antibiotics",
      "Administer broad-spectrum antibiotics within 1 hour",
      "Initiate fluid resuscitation (30 mL/kg crystalloid)",
      "Consider ICU admission",
      "Monitor lactate clearance"
    ],
    "references": ["Surviving Sepsis Campaign 2021", "qSOFA Validation Study"],
    "generated_at": "2025-01-15T10:00:00Z"
  }
}
```

### Predict Readmission Risk
```http
POST /api/clinicals/ai-insights/readmission-risk
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": "PAT123",
  "age": 72,
  "comorbidities": ["heart_failure", "diabetes", "copd"],
  "length_of_stay": 8,
  "previous_admissions": 3
}
```

**Response:**
```json
{
  "insight": {
    "insight_type": "readmission_risk",
    "title": "30-Day Readmission Risk",
    "description": "Risk Score: 7/10",
    "risk_level": "high",
    "confidence": 0.78,
    "evidence": [
      "Age 72 years (≥65 increases risk)",
      "3 high-risk comorbidities present",
      "Extended length of stay: 8 days",
      "Multiple recent admissions: 3 in past year"
    ],
    "recommendations": [
      "Schedule follow-up within 7 days of discharge",
      "Arrange home health services",
      "Medication reconciliation and education",
      "Provide written discharge instructions",
      "Consider transitional care program",
      "Ensure patient has primary care provider"
    ]
  }
}
```

### Detect Patient Deterioration
```http
POST /api/clinicals/ai-insights/deterioration
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": "PAT123",
  "vital_signs_history": [
    {
      "timestamp": "2025-01-15T08:00:00Z",
      "respiratory_rate": 18,
      "heart_rate": 75,
      "systolic_bp": 120,
      "temperature": 37.0,
      "avpu": "A"
    },
    {
      "timestamp": "2025-01-15T10:00:00Z",
      "respiratory_rate": 26,
      "heart_rate": 115,
      "systolic_bp": 95,
      "temperature": 38.5,
      "avpu": "V"
    }
  ]
}
```

---

## Clinical Decision Support

### Get Guideline Categories
```http
GET /api/clinicals/decision-support/categories
Authorization: Bearer {token}
```

**Response:**
```json
{
  "categories": [
    "antibiotic_stewardship",
    "venous_thromboembolism",
    "pain_management",
    "diabetes_management",
    "hypertension",
    "heart_failure",
    "sepsis"
  ]
}
```

### Get Guidelines by Category
```http
GET /api/clinicals/decision-support/guidelines/sepsis
Authorization: Bearer {token}
```

**Response:**
```json
{
  "category": "sepsis",
  "recommendations": [
    {
      "recommendation_id": "SEPSIS_001",
      "category": "sepsis",
      "title": "Sepsis and Septic Shock Management",
      "description": "Surviving Sepsis Campaign bundle",
      "strength": "strong",
      "evidence_level": "Grade A",
      "actions": [
        "Hour 1 Bundle:",
        "1. Measure lactate, remeasure if >2 mmol/L",
        "2. Obtain blood cultures before antibiotics",
        "3. Administer broad-spectrum antibiotics",
        "4. Fluid resuscitation: 30 mL/kg crystalloid for hypotension/lactate ≥4",
        "5. Vasopressors if hypotensive during/after fluid resuscitation (target MAP ≥65)"
      ],
      "contraindications": [
        "Adjust antibiotics based on source and local resistance",
        "De-escalate based on cultures and clinical improvement",
        "Avoid excessive fluid in ARDS or cardiogenic shock"
      ],
      "monitoring": [
        "Lactate clearance (repeat q2-4h until normalized)",
        "Urine output (target >0.5 mL/kg/hr)",
        "Mental status, vital signs q15-30min",
        "Reassess volume status frequently"
      ],
      "references": ["Surviving Sepsis Campaign 2021"]
    }
  ],
  "total": 1
}
```

### Search Guidelines
```http
GET /api/clinicals/decision-support/search?query=antibiotic
Authorization: Bearer {token}
```

---

## Care Coordination

### Create Care Task
```http
POST /api/clinicals/care-coordination/tasks
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Morning Assessment",
  "description": "Complete vital signs and physical exam",
  "priority": "high",
  "assigned_to": "Nurse Johnson",
  "assigned_role": "nurse",
  "due_hours": 2,
  "patient_id": "PAT123",
  "created_by": "Dr. Smith"
}
```

**Response:**
```json
{
  "task": {
    "task_id": "TASK_1705315200",
    "title": "Morning Assessment",
    "description": "Complete vital signs and physical exam",
    "priority": "high",
    "assigned_to": "Nurse Johnson",
    "assigned_role": "nurse",
    "due_date": "2025-01-15T12:00:00Z",
    "patient_id": "PAT123",
    "created_by": "Dr. Smith",
    "status": "pending",
    "is_overdue": false
  }
}
```

### Get Patient Tasks
```http
GET /api/clinicals/care-coordination/tasks/patient/{patient_id}
Authorization: Bearer {token}
```

### Complete Task
```http
POST /api/clinicals/care-coordination/tasks/{task_id}/complete
Authorization: Bearer {token}
Content-Type: application/json

{
  "notes": "Assessment completed. Patient stable."
}
```

### Create Handoff
```http
POST /api/clinicals/care-coordination/handoffs
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": "PAT123",
  "from_provider": "Dr. Smith",
  "to_provider": "Dr. Jones",
  "handoff_type": "shift_change",
  "summary": "72yo male, day 3 post-op, stable condition",
  "action_items": [
    "Monitor drain output",
    "Continue antibiotics",
    "Physical therapy consult"
  ],
  "concerns": [
    "Mild tachycardia this morning",
    "Pain control adequate"
  ]
}
```

### Generate Handoff Report
```http
GET /api/clinicals/care-coordination/handoffs/report/{patient_id}?provider=Dr.Smith
Authorization: Bearer {token}
```

**Response:**
```json
{
  "patient_id": "PAT123",
  "provider": "Dr. Smith",
  "generated_at": "2025-01-15T10:00:00Z",
  "sbar": {
    "situation": {
      "description": "Current patient status and reason for admission",
      "key_points": ["Primary diagnosis", "Current location", "Code status"]
    },
    "background": {
      "description": "Relevant medical history and hospital course",
      "key_points": ["Past medical history", "Medications", "Allergies", "Recent procedures"]
    },
    "assessment": {
      "description": "Current clinical assessment",
      "key_points": ["Vital signs trends", "Laboratory results", "Physical exam findings", "Response to treatment"]
    },
    "recommendation": {
      "description": "Plan and action items",
      "key_points": ["Pending tasks", "Anticipated issues", "Follow-up needed"]
    }
  },
  "pending_tasks": [],
  "care_team": [],
  "action_items": [
    "Review pending lab results",
    "Follow up on consults",
    "Reassess pain management",
    "Update family on progress"
  ]
}
```

---

## WebSocket API

### Connect to WebSocket
```javascript
const ws = new WebSocket('wss://api.itechsmart.example.com/ws?token=YOUR_JWT_TOKEN');

ws.onopen = () => {
  console.log('Connected to WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Subscribe to Channels
```javascript
// Subscribe to patient updates
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'patients',
  patient_id: 'PAT123'
}));

// Subscribe to HL7 messages
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'hl7'
}));

// Subscribe to alerts
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'alerts'
}));
```

### WebSocket Message Types
```json
{
  "type": "patient_update",
  "channel": "patients",
  "data": {
    "patient_id": "PAT123",
    "event": "observation_added",
    "observation": { }
  }
}
```

---

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "patient_id",
      "issue": "Patient ID is required"
    }
  }
}
```

### HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Common Error Codes
- `AUTHENTICATION_REQUIRED` - No authentication token provided
- `INVALID_TOKEN` - Authentication token is invalid or expired
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions
- `VALIDATION_ERROR` - Request validation failed
- `RESOURCE_NOT_FOUND` - Requested resource does not exist
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `EMR_CONNECTION_ERROR` - EMR system connection failed
- `DATABASE_ERROR` - Database operation failed

---

## Rate Limiting

### Rate Limits
- **Default:** 100 requests per minute per user
- **Burst:** 50 concurrent connections
- **WebSocket:** 1000 messages per minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705315260
```

### Rate Limit Exceeded Response
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 60
  }
}
```

---

## API Versioning

The API uses URL versioning. The current version is `v1`.

```http
GET /api/v1/patients
```

When a new version is released, the old version will be supported for at least 6 months.

---

## Support

For API support, please contact:
- **Email:** api-support@itechsmart.dev
- **Documentation:** https://docs.itechsmart.dev
- **Status Page:** https://status.itechsmart.dev

---

**Last Updated:** January 15, 2025  
**API Version:** 1.0.0