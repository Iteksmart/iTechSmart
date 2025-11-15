# iTechSmart Supreme - Quick Start Guide

Get up and running with iTechSmart Supreme in 5 minutes!

## 🚀 Installation

### Option 1: Docker (Recommended)

```bash
# 1. Clone and navigate
git clone https://github.com/yourusername/itechsmart-supreme.git
cd itechsmart-supreme

# 2. Configure
cp .env.example .env
nano .env  # Edit with your settings

# 3. Start
docker-compose up -d

# 4. Access
open http://localhost:5000
```

### Option 2: Python

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure
export OFFLINE_MODE=true
export MASTER_PASSWORD=your-secure-password

# 3. Run
python main.py

# 4. Access
open http://localhost:5000
```

## ⚙️ Basic Configuration

### Minimum Required Settings

```bash
# .env file
MASTER_PASSWORD=change_me_in_production
OFFLINE_MODE=true
AUTO_REMEDIATION=false
```

### Add Your First Host

```bash
curl -X POST http://localhost:5000/api/hosts \
  -H "Content-Type: application/json" \
  -d '{
    "host": "your-server.com",
    "username": "admin",
    "password": "your-password",
    "platform": "linux",
    "port": 22,
    "use_sudo": true
  }'
```

## 🎯 First Steps

### 1. Access Dashboard
Navigate to `http://localhost:5000`

### 2. Check System Status
```bash
curl http://localhost:5000/api/status
```

### 3. Configure Monitoring

**Prometheus:**
```bash
# Set in .env
PROMETHEUS_ENDPOINTS=http://your-prometheus:9090
```

**Wazuh:**
```bash
# Set in .env
WAZUH_ENDPOINTS=https://your-wazuh:55000:username:password
```

### 4. Test with Demo Scenario

```bash
# Create a high CPU scenario
cat > /tmp/test.sh << 'EOF'
#!/bin/bash
while true; do echo "test" > /dev/null; done
EOF
chmod +x /tmp/test.sh
/tmp/test.sh &

# Watch dashboard for alert
# iTechSmart Supreme will detect and offer to resolve
```

## 📊 Key Features to Try

1. **View Active Alerts**: Dashboard shows real-time alerts
2. **Approve Actions**: Click approve/reject on pending actions
3. **Check History**: View execution history in dashboard
4. **Test Kill Switch**: Emergency stop all automated actions

## 🔧 Common Commands

```bash
# Check health
curl http://localhost:5000/api/health

# View alerts
curl http://localhost:5000/api/alerts

# View pending actions
curl http://localhost:5000/api/actions/pending

# View execution history
curl http://localhost:5000/api/executions

# Enable kill switch
curl -X POST http://localhost:5000/api/killswitch/enable
```

## 🆘 Troubleshooting

### Can't connect to dashboard
```bash
# Check if running
docker-compose ps
# or
ps aux | grep python

# Check logs
docker-compose logs -f
```

### Alerts not appearing
```bash
# Verify monitoring endpoints
curl http://localhost:5000/api/status

# Check credentials
curl http://localhost:5000/api/hosts
```

### Actions not executing
```bash
# Test SSH connection manually
ssh admin@your-server

# Check kill switch status
curl http://localhost:5000/api/killswitch/status
```

## 📚 Next Steps

1. **Read Full Documentation**: See [README.md](README.md)
2. **Configure Production**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
3. **Try Demo Scenarios**: See [DEMO_SCENARIOS.md](DEMO_SCENARIOS.md)
4. **Set Up Monitoring**: Configure Prometheus and Wazuh
5. **Enable Auto-Remediation**: After testing, enable in .env

## 🎓 Learning Path

1. ✅ Install and access dashboard
2. ✅ Add first monitored host
3. ✅ Configure monitoring endpoints
4. ✅ Test with demo scenario
5. ✅ Review execution logs
6. ✅ Configure webhooks
7. ✅ Enable auto-remediation
8. ✅ Deploy to production

## 💡 Pro Tips

- Start with `AUTO_REMEDIATION=false` to review actions first
- Use `OFFLINE_MODE=true` initially (no OpenAI API needed)
- Test with non-critical systems first
- Keep kill switch easily accessible
- Review audit logs regularly

## 🔗 Useful Links

- Dashboard: http://localhost:5000
- API Docs: http://localhost:5000/api
- Health Check: http://localhost:5000/api/health
- Webhooks: http://localhost:5000/webhook

## 🎉 You're Ready!

iTechSmart Supreme is now monitoring your infrastructure and ready to eliminate downtime!

**Questions?** Check the full [README.md](README.md) or open an issue on GitHub.

---

**Welcome to the end of IT downtime! 🚀**