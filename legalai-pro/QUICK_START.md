# LegalAI Pro - Quick Start Guide

## 🚀 Get Started in 3 Easy Steps

### Step 1: Download the Project
The project is ready in your workspace at `/workspace/legalai-pro`

### Step 2: Run the Application

#### Option A: Using Startup Scripts (Easiest)

**On macOS/Linux:**
```bash
cd legalai-pro
./start.sh
```

**On Windows:**
```bash
cd legalai-pro
start.bat
```

#### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
cd legalai-pro/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd legalai-pro/frontend
npm install
npm run dev
```

#### Option C: Docker (Production-Ready)
```bash
cd legalai-pro
docker-compose up -d
```

### Step 3: Access the Application

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

**Demo Login:**
- Email: `demo@legalai.pro`
- Password: `demo123`

## 🎯 What to Explore

### 1. Dashboard
- View real-time statistics
- See revenue charts
- Check case distribution
- Review recent cases and events

### 2. AI Assistant (★ Revolutionary Feature)
- Click on "AI Assistant" in the sidebar
- Try asking: "Help me research case law on contract disputes"
- Explore quick actions: Legal Research, Draft Motion, Analyze Contract, Case Prediction
- Experience the chat interface with AI responses

### 3. Clients
- Add new clients
- View client list
- Access auto-fill data for documents

### 4. Cases
- Create new cases
- Track case progress
- Associate documents and time entries

### 5. Documents
- Upload documents
- Use AI summarization
- Auto-fill templates with case/client data

## 🤖 AI Features to Try

### Document Auto-Fill
```
1. Go to Documents
2. Select a template
3. Choose a case
4. Watch AI automatically fill all fields
```

### Legal Research
```
1. Go to AI Assistant
2. Ask: "Find cases about breach of contract in California"
3. Get instant results with citations
```

### Contract Analysis
```
1. Go to AI Assistant
2. Upload a contract
3. Get comprehensive risk analysis
```

### Case Prediction
```
1. Go to AI Assistant
2. Select a case
3. Get outcome predictions with confidence scores
```

## 📊 Sample Data

The application comes with demo data:
- **Clients**: 248 clients
- **Cases**: 89 active cases
- **Revenue**: $124,500 MTD
- **AI Queries**: 1,247 this month

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port already in use
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 3000)
lsof -ti:3000 | xargs kill -9
```

## 📚 Documentation

- **README.md** - Complete project overview
- **FEATURES.md** - Detailed feature list
- **DEPLOYMENT.md** - Production deployment guide
- **PROJECT_SUMMARY.md** - Technical summary
- **API Docs** - http://localhost:8000/docs (when running)

## 🎨 UI Preview

### Login Page
- Beautiful gradient background
- Clean, modern form
- Demo credentials displayed
- Responsive design

### Dashboard
- 4 statistics cards (Clients, Cases, Revenue, AI Queries)
- Revenue bar chart
- Case distribution pie chart
- Recent cases list
- Upcoming events list
- AI Assistant quick access

### AI Assistant
- Chat interface with message bubbles
- Quick action buttons
- Multiple tabs for different AI features
- Sidebar with capabilities
- Recent conversations

## 💡 Tips for Best Experience

1. **Start with AI Assistant** - It's the most impressive feature
2. **Try auto-fill** - Create a case and see how AI fills documents
3. **Explore the dashboard** - See all the analytics and charts
4. **Check API docs** - Visit /docs to see all available endpoints
5. **Test different features** - Each module is designed for efficiency

## 🆘 Need Help?

- **Documentation**: Check the docs folder
- **API Reference**: http://localhost:8000/docs
- **Issues**: Create an issue on GitHub
- **Email**: support@legalai.pro

## 🎉 Enjoy!

You now have the world's most advanced AI-powered attorney office software at your fingertips. Explore, experiment, and see how AI can revolutionize legal practice!

---

**LegalAI Pro - Making Legal Practice Smarter, Faster, and More Profitable**

*Built with ❤️ for attorneys by attorneys*