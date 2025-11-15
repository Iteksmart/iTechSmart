# iTechSmart Supreme - Healthcare Management System

## Overview

iTechSmart Supreme is a comprehensive healthcare management system designed for hospitals, clinics, and medical facilities. It provides complete patient care management, appointment scheduling, medical records, billing, and more.

## Features

### Patient Management
- Complete patient records with demographics
- Medical history tracking
- Insurance information management
- Emergency contact management
- Patient search and filtering

### Appointment Scheduling
- Provider-based scheduling
- Conflict detection
- Multiple appointment statuses
- Room assignment
- Automated reminders

### Medical Records
- Visit documentation
- Diagnosis tracking
- Treatment plans
- Vital signs recording
- Lab results integration
- Imaging results

### Prescription Management
- Electronic prescriptions
- Dosage and frequency tracking
- Refill management
- Drug interaction checking
- Prescription history

### Billing & Insurance
- Automated billing generation
- Insurance claim processing
- Payment tracking
- Outstanding balance management
- Revenue reporting

### Lab Tests
- Test ordering
- Result tracking
- Normal range comparison
- Status monitoring

### Inventory Management
- Medical supplies tracking
- Reorder level alerts
- Expiry date monitoring
- Supplier management

### Analytics & Reporting
- Dashboard with key metrics
- Appointment analytics
- Revenue reports
- Patient demographics
- Custom report generation

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **API**: RESTful with automatic OpenAPI documentation

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts
- **State Management**: React Hooks

## Installation

### Using Docker (Recommended)

```bash
cd itechsmart_supreme
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

- **Frontend**: http://localhost:3004
- **Backend API**: http://localhost:8004
- **API Documentation**: http://localhost:8004/docs
- **Health Check**: http://localhost:8004/health

## API Endpoints

### Patients
- `POST /api/patients` - Create patient
- `GET /api/patients/{id}` - Get patient
- `GET /api/patients` - Search patients
- `PUT /api/patients/{id}` - Update patient

### Appointments
- `POST /api/appointments` - Schedule appointment
- `GET /api/appointments` - Get appointments (with filters)
- `PUT /api/appointments/{id}/status` - Update status
- `GET /api/appointments/analytics` - Get analytics

### Billing
- `POST /api/billing` - Create bill
- `GET /api/billing/patient/{id}` - Get patient bills
- `POST /api/billing/{id}/payment` - Process payment

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## Database Models

### Core Models
- **Patient** - Patient demographics and information
- **Provider** - Healthcare providers (doctors, nurses)
- **Appointment** - Scheduled appointments
- **MedicalRecord** - Patient visit records
- **Prescription** - Medication prescriptions
- **Bill** - Billing and payments
- **LabTest** - Laboratory tests
- **Inventory** - Medical supplies
- **Facility** - Healthcare facilities
- **Department** - Hospital departments

## Configuration

### Environment Variables

```env
DATABASE_URL=sqlite:///./supreme.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/supreme

PORT=8004
```

## Integration with iTechSmart Suite

iTechSmart Supreme integrates with:

- **Enterprise Hub** - Service registration and coordination
- **Ninja** - Self-healing and monitoring
- **HL7** - Medical data exchange
- **Analytics** - Advanced analytics and reporting

## Security Features

- Patient data encryption
- HIPAA compliance ready
- Role-based access control
- Audit logging
- Secure authentication

## Compliance

- **HIPAA** - Health Insurance Portability and Accountability Act
- **HL7** - Health Level 7 standards
- **ICD-10** - International Classification of Diseases
- **CPT** - Current Procedural Terminology

## Support

For support and documentation:
- API Documentation: http://localhost:8004/docs
- GitHub Issues: [Report issues]
- Email: support@itechsmart.dev

## License

Copyright © 2025 iTechSmart. All rights reserved.

---

**Part of the iTechSmart Suite** - The world's most comprehensive enterprise software ecosystem.