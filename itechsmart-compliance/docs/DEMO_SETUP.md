# Itechsmart Compliance - Demo Setup Guide

**Version**: 1.0.0  
**Last Updated**: November 17, 2025

---

## Demo Environment

### Quick Demo Access

**Demo URL**: https://itechsmart-compliance-demo.itechsmart.dev  
**Status**: Available 24/7

### Demo Credentials

**Admin Account**:
- Email: admin@demo.itechsmart.dev
- Password: Demo@2025!Admin

**User Account**:
- Email: user@demo.itechsmart.dev
- Password: Demo@2025!User

**API Key** (for testing):
```
demo_key_1234567890abcdef
```

---

## Demo Features

### Available Features

✅ All core features enabled  
✅ Sample data pre-loaded  
✅ Full API access  
✅ Admin panel access  
✅ Real-time updates  

### Limitations

⚠️ Demo resets every 24 hours  
⚠️ Rate limited to 100 requests/minute  
⚠️ File uploads limited to 10MB  
⚠️ No email notifications sent  

---

## Sample Data

### Pre-loaded Data

The demo environment includes:
- **10 sample users**
- **50 sample records**
- **Sample API data**
- **Test configurations**

### Test Scenarios

#### Scenario 1: Basic Usage
1. Log in with user credentials
2. Navigate to dashboard
3. Explore main features
4. View sample data

#### Scenario 2: Admin Functions
1. Log in with admin credentials
2. Access admin panel
3. Manage users
4. Configure settings

#### Scenario 3: API Testing
1. Use provided API key
2. Make API requests
3. View responses
4. Test different endpoints

---

## Local Demo Setup

### Run Demo Locally

```bash
# Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/itechsmart-compliance

# Use demo configuration
cp .env.demo .env

# Start demo environment
docker-compose -f docker-compose.demo.yml up -d

# Load sample data
docker-compose exec app python scripts/load_demo_data.py

# Access demo
open http://localhost:8000
```

### Demo Configuration

```env
# .env.demo
DEMO_MODE=true
RESET_INTERVAL=24h
RATE_LIMIT=100
MAX_UPLOAD_SIZE=10MB
ENABLE_EMAIL=false
```

---

## API Demo Examples

### Example 1: Authentication

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@demo.itechsmart.dev",
    "password": "Demo@2025!User"
  }'
```

### Example 2: List Resources

```bash
curl -X GET http://localhost:8000/api/resources \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example 3: Create Resource

```bash
curl -X POST http://localhost:8000/api/resources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Resource",
    "type": "test"
  }'
```

---

## Demo Videos

### Video Tutorials

1. **Getting Started** (5 min)
   - Overview of features
   - Basic navigation
   - Common tasks

2. **Advanced Features** (10 min)
   - Advanced functionality
   - Configuration options
   - Best practices

3. **API Walkthrough** (8 min)
   - API authentication
   - Common endpoints
   - Error handling

**Watch**: https://demo.itechsmart.dev/videos

---

## Feedback

### Report Issues

Found a bug in the demo?
- Email: demo-feedback@itechsmart.dev
- GitHub: https://github.com/Iteksmart/iTechSmart/issues

### Request Features

Want to see something in the demo?
- Email: demo-requests@itechsmart.dev

---

## Production Setup

Ready to move to production?

1. See **DEPLOYMENT_GUIDE.md** for production setup
2. Contact sales@itechsmart.dev for licensing
3. Schedule onboarding session

---

**End of Demo Setup Guide**
