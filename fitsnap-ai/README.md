# 🎨 FitSnap.AI - Your Personal Style Scanner

<div align="center">

![FitSnap.AI Logo](https://via.placeholder.com/200x200?text=FitSnap.AI)

**"Snap a selfie. Get outfit tips, matching accessories, and deals — instantly."**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](package.json)
[![Status](https://img.shields.io/badge/status-production--ready-success.svg)]()

[Features](#features) • [Tech Stack](#tech-stack) • [Getting Started](#getting-started) • [API Docs](#api-documentation) • [Deployment](#deployment)

</div>

---

## 🚀 Overview

**FitSnap.AI** is an AI-powered fashion feedback SaaS that analyzes outfit selfies and provides instant style ratings, color harmony analysis, and personalized shopping recommendations for just **$1/month**.

### 💡 The Problem We Solve

- 😰 People struggle with outfit coordination
- 💸 Personal stylists cost $100-$500/session
- 🤔 Fashion advice is subjective and inconsistent
- 🛍️ Finding matching items is time-consuming
- 📱 No instant, affordable fashion feedback exists

### ✨ Our Solution

- 📸 **Snap a selfie** → Get instant AI analysis
- 🤖 **AI-powered feedback** → Style score, color harmony, trend match
- 🛍️ **Smart recommendations** → Matching items with affiliate links
- 💬 **AI Stylist Chat** → Ask follow-up questions
- 💰 **$1/month** → 50x cheaper than competitors

---

## 🎯 Key Features

### ✅ Core Features

#### 1. 📸 Selfie Capture & Upload
- One-tap camera capture
- Photo upload from gallery
- Auto-crop and optimization
- Privacy-first (60-second auto-delete)

#### 2. 🤖 AI Outfit Analysis
- **Style Score** (1-10): Overall outfit rating
- **Color Harmony** (1-10): Color combination analysis
- **Trend Match** (1-10): Fashion trend alignment
- **Detected Items**: Automatic clothing detection
- **Style Category**: Casual, formal, trendy, sporty, chic

#### 3. 💄 Hair & Makeup Analysis
- Hair style compatibility
- Makeup tone harmony
- Grooming suggestions
- Overall presentation score

#### 4. 🛍️ Smart Shopping Recommendations
- AI-matched product suggestions
- Affiliate links (Amazon, ASOS, Zara)
- Price comparison
- Discount alerts
- Complementary items

#### 5. 💬 AI Stylist Chat
- Ask follow-up questions
- Get personalized advice
- Context-aware responses
- "Find me shoes to match this dress"

#### 6. 💾 My Looks / Closet
- Save favorite outfits
- Track style scores over time
- Add notes and tags
- Weekly outfit suggestions

#### 7. 💰 Subscription Management
- **Free**: 1 scan/day
- **Basic ($1/month)**: Unlimited scans
- **Pro ($3/month)**: Advanced features + exclusive deals

---

## 🏗️ Tech Stack

### Backend
```
FastAPI (Python 3.11)
├── PostgreSQL (Database)
├── Redis (Caching)
├── OpenAI Vision API (AI Analysis)
├── Stripe (Payments)
├── Fashion APIs (Product Recommendations)
└── JWT Authentication
```

### Frontend
```
React Native (Expo)
├── React Navigation
├── Expo Camera
├── TypeScript
├── Axios (API Client)
├── AsyncStorage (Local Data)
└── Lottie (Animations)
```

### AI & Vision
- **OpenAI GPT-4 Vision**: Outfit analysis
- **Color Thief**: Color extraction
- **Custom ML Models**: Style scoring

### APIs & Integrations
- Amazon Affiliate API
- ShopStyle API
- ASOS API
- Pinterest Trends API
- Stripe Payments

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Expo CLI
- OpenAI API Key
- Stripe Account

### Backend Setup

```bash
# Navigate to backend
cd fitsnap-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# Access API
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Frontend Setup

```bash
# Navigate to frontend
cd fitsnap-ai/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API URL

# Start Expo
npm start

# Run on device
# iOS: npm run ios
# Android: npm run android
# Web: npm run web
```

### Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# Access
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

---

## 📊 Database Schema

### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE,
    full_name VARCHAR,
    hashed_password VARCHAR NOT NULL,
    subscription_tier VARCHAR DEFAULT 'free',
    stripe_customer_id VARCHAR,
    stripe_subscription_id VARCHAR,
    subscription_active BOOLEAN DEFAULT false,
    style_preferences TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Outfit Scans
```sql
CREATE TABLE outfit_scans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    image_path VARCHAR NOT NULL,
    style_score FLOAT NOT NULL,
    color_harmony FLOAT NOT NULL,
    trend_match FLOAT NOT NULL,
    overall_rating FLOAT NOT NULL,
    detected_items TEXT,
    colors TEXT,
    style_category VARCHAR,
    feedback TEXT,
    suggestions TEXT,
    auto_delete_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Saved Looks
```sql
CREATE TABLE saved_looks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    scan_id INTEGER REFERENCES outfit_scans(id),
    title VARCHAR,
    notes TEXT,
    tags TEXT,
    is_favorite BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Scan Endpoints

#### Create Scan
```http
POST /api/v1/scans/analyze
Authorization: Bearer {token}
Content-Type: multipart/form-data

{
  "image": <file>,
  "include_hair_makeup": true
}
```

#### Get Scan Results
```http
GET /api/v1/scans/{scan_id}
Authorization: Bearer {token}
```

#### List User Scans
```http
GET /api/v1/scans?limit=20&offset=0
Authorization: Bearer {token}
```

### Product Endpoints

#### Get Recommendations
```http
POST /api/v1/products/recommendations
Authorization: Bearer {token}
Content-Type: application/json

{
  "scan_id": 123,
  "max_results": 10
}
```

#### Get Trending Items
```http
GET /api/v1/products/trending?category=casual&limit=10
Authorization: Bearer {token}
```

### Chat Endpoints

#### Send Message
```http
POST /api/v1/chat/message
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "Find me shoes to match this dress",
  "scan_id": 123
}
```

---

## 💰 Business Model

### Pricing Tiers

| Feature | Free | Basic ($1/mo) | Pro ($3/mo) |
|---------|------|---------------|-------------|
| Scans per day | 1 | Unlimited | Unlimited |
| Style Score | ✅ | ✅ | ✅ |
| Color Harmony | ✅ | ✅ | ✅ |
| Trend Match | ✅ | ✅ | ✅ |
| Product Recommendations | Limited | ✅ | ✅ |
| AI Stylist Chat | ❌ | ❌ | ✅ |
| Saved Looks | 5 | 50 | Unlimited |
| Exclusive Deals | ❌ | ❌ | ✅ |
| Priority Support | ❌ | ❌ | ✅ |

### Revenue Streams
1. **Subscriptions**: $1-$3/month recurring
2. **Affiliate Commissions**: 5-10% on purchases
3. **Brand Partnerships**: Sponsored styles
4. **Premium Features**: AR try-on, virtual closet

---

## 📈 Market Opportunity

### Target Market
- **Primary**: Women 18-45 (fashion-conscious)
- **Secondary**: Men 18-35 (style-aware)
- **Tertiary**: Fashion students, influencers

### Market Size
- **TAM**: $42 Billion (password managers + fashion tech)
- **SAM**: $8 Billion (mobile fashion apps)
- **SOM**: $200 Million (Year 3 target)

### Competitive Advantage
- **50x cheaper** than personal stylists
- **Instant feedback** vs days of waiting
- **AI-powered** vs human subjectivity
- **Privacy-first** vs data harvesting
- **Affiliate revenue** vs pure subscription

---

## 🎨 UI/UX Design

### Color Palette
```
Primary:    #FF6B9D (Pink)
Secondary:  #C06C84 (Rose)
Accent:     #F67280 (Coral)
Success:    #2ECC71 (Green)
Warning:    #FFD700 (Gold)
Background: #F8F9FA (Light Gray)
Text:       #2C3E50 (Dark Gray)
```

### Typography
- **Headings**: SF Pro Display (Bold)
- **Body**: SF Pro Text (Regular)
- **Buttons**: SF Pro Text (Semibold)

### Key Screens
1. **Onboarding** - 3-step intro with benefits
2. **Home** - Quick stats + recent scans
3. **Camera** - Full-screen capture with tips
4. **Analysis** - Beautiful results display
5. **Recommendations** - Product grid with filters
6. **My Looks** - Saved outfits gallery
7. **Chat** - AI stylist conversation
8. **Profile** - Settings + subscription

---

## 🔒 Privacy & Security

### Data Protection
- ✅ End-to-end photo encryption
- ✅ Auto-delete after 60 seconds
- ✅ No photo storage without consent
- ✅ GDPR compliant
- ✅ CCPA compliant

### Security Features
- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting
- ✅ SQL injection protection
- ✅ XSS protection
- ✅ HTTPS only

---

## 📱 Deployment

### Backend Deployment

#### Docker (Recommended)
```bash
docker-compose up -d
```

#### Manual
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment

#### Expo Build
```bash
# Android
eas build --platform android

# iOS
eas build --platform ios

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

#### Web Deployment
```bash
npm run build
npm run export
# Deploy to Vercel/Netlify
```

---

## 📊 Success Metrics

### User Metrics
- **DAU/MAU**: Daily/Monthly Active Users
- **Retention**: 7-day, 30-day retention
- **Engagement**: Scans per user per week

### Business Metrics
- **MRR**: Monthly Recurring Revenue
- **ARPU**: Average Revenue Per User ($1-$3)
- **CAC**: Customer Acquisition Cost (<$5)
- **LTV**: Lifetime Value ($50-$100)
- **Churn Rate**: <5% monthly

### Product Metrics
- **Scan Success Rate**: >95%
- **AI Accuracy**: >85% user satisfaction
- **Conversion Rate**: 20% free → paid
- **Affiliate Revenue**: $0.50-$2 per user/month

---

## 🎯 Roadmap

### Phase 1: MVP Launch (Weeks 1-6) ✅
- [x] Backend API
- [x] AI Vision Integration
- [x] Mobile App (iOS/Android)
- [x] Basic subscription
- [x] Product recommendations

### Phase 2: Growth (Months 2-3)
- [ ] TikTok integration
- [ ] Influencer partnerships
- [ ] Referral program
- [ ] App Store optimization
- [ ] Social sharing

### Phase 3: Monetization (Months 4-6)
- [ ] Pro tier launch
- [ ] Brand partnerships
- [ ] Exclusive deals
- [ ] Conversion optimization
- [ ] A/B testing

### Phase 4: Scale (Months 7-12)
- [ ] AR try-on feature
- [ ] Virtual closet
- [ ] Social features
- [ ] International expansion
- [ ] Celebrity partnerships

---

## 💻 Development

### Project Structure
```
fitsnap-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config & security
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   ├── alembic/          # Database migrations
│   ├── tests/            # Test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── screens/      # App screens
│   │   ├── components/   # Reusable components
│   │   ├── services/     # API client
│   │   └── utils/        # Utilities
│   ├── App.tsx           # Main app
│   └── package.json
├── docs/                 # Documentation
└── docker-compose.yml    # Docker setup
```

### Running Tests

#### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/
```

#### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

---

## 🌟 Why FitSnap.AI Will Win

### 1. Revolutionary Pricing
- **$1/month** vs $50+/year competitors
- **50x cheaper** than personal stylists
- **No commitment** - cancel anytime

### 2. Instant Gratification
- **3-second analysis** vs days of waiting
- **Dopamine hit** from instant feedback
- **Shareable results** for social media

### 3. AI-Powered Accuracy
- **GPT-4 Vision** for outfit analysis
- **Color theory algorithms** for harmony
- **Trend database** for fashion alignment

### 4. Privacy-First
- **60-second auto-delete** by default
- **No photo storage** without consent
- **End-to-end encryption**

### 5. Viral Potential
- **TikTok-ready** - "AI rated my outfit 8.7/10 😍"
- **Instagram stories** - Style score stickers
- **Referral incentives** - Free month for friends

---

## 📞 Support & Contact

**Company**: iTechSmart Inc.
**Product**: FitSnap.AI
**Website**: https://fitsnap.ai
**Email**: support@fitsnap.ai
**Twitter**: @FitSnapAI
**Instagram**: @fitsnap.ai

---

## 📄 License

Copyright © 2025 iTechSmart Inc. All rights reserved.

---

## 🙏 Acknowledgments

Built with ❤️ by the iTechSmart team.

Special thanks to:
- OpenAI for GPT-4 Vision API
- Expo team for amazing mobile framework
- Fashion API providers
- Our beta testers

---

<div align="center">

**🎨 FitSnap.AI - Look Good. Match Better. Spend Smarter. 🎨**

Made with 💖 by [iTechSmart Inc.](https://itechsmart.dev)

</div>