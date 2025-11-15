#!/bin/bash

################################################################################
#                                                                              #
#           iTechSmart Enterprise - Automated Setup Script                    #
#                                                                              #
#     This script sets up the complete iTechSmart Enterprise platform          #
#     with integration management dashboard                                    #
#                                                                              #
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print banner
cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   ██╗████████╗███████╗ ██████╗██╗  ██╗███████╗███╗   ███╗ █████╗ ██████╗ ║
║   ██║╚══██╔══╝██╔════╝██╔════╝██║  ██║██╔════╝████╗ ████║██╔══██╗██╔══██╗║
║   ██║   ██║   █████╗  ██║     ███████║███████╗██╔████╔██║███████║██████╔╝║
║   ██║   ██║   ██╔══╝  ██║     ██╔══██║╚════██║██║╚██╔╝██║██╔══██║██╔══██╗║
║   ██║   ██║   ███████╗╚██████╗██║  ██║███████║██║ ╚═╝ ██║██║  ██║██║  ██║║
║   ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝║
║                                                                            ║
║                    Enterprise Integration Platform                         ║
║                          Automated Setup v1.0.0                            ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

EOF

echo -e "${CYAN}Starting iTechSmart Enterprise setup...${NC}\n"

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo -e "${YELLOW}Please install Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker found: $(docker --version)${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo -e "${YELLOW}Please install Docker Compose${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found: $(docker-compose --version)${NC}"

# Check system resources
echo -e "\n${BLUE}Checking system resources...${NC}"
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_MEM" -lt 4 ]; then
    echo -e "${YELLOW}⚠ Warning: Less than 4GB RAM available${NC}"
fi
echo -e "${GREEN}✓ Memory: ${TOTAL_MEM}GB${NC}"

# Create environment file
echo -e "\n${BLUE}Creating environment configuration...${NC}"
if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
# iTechSmart Enterprise Configuration

# Application
APP_NAME=iTechSmart Enterprise
APP_ENV=development
DEBUG=true
SECRET_KEY=change-this-to-a-random-secret-key-in-production

# Database
DATABASE_URL=postgresql://itechsmart:itechsmart@postgres:5432/itechsmart
POSTGRES_USER=itechsmart
POSTGRES_PASSWORD=itechsmart
POSTGRES_DB=itechsmart

# Redis
REDIS_URL=redis://redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000

# Admin User
ADMIN_EMAIL=admin@itechsmart.dev
ADMIN_PASSWORD=admin123

# Integration Credentials (Configure these in the dashboard)
# ServiceNow
SERVICENOW_INSTANCE_URL=
SERVICENOW_CLIENT_ID=
SERVICENOW_CLIENT_SECRET=
SERVICENOW_USERNAME=
SERVICENOW_PASSWORD=

# Zendesk
ZENDESK_SUBDOMAIN=
ZENDESK_EMAIL=
ZENDESK_API_TOKEN=

# IT Glue
ITGLUE_API_KEY=
ITGLUE_API_URL=https://api.itglue.com

# N-able
NABLE_SERVER_URL=
NABLE_JWT_TOKEN=

# ConnectWise
CONNECTWISE_COMPANY_ID=
CONNECTWISE_PUBLIC_KEY=
CONNECTWISE_PRIVATE_KEY=
CONNECTWISE_API_URL=

# Jira
JIRA_SITE_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=

# Slack
SLACK_WEBHOOK_URL=
SLACK_BOT_TOKEN=

# Prometheus
PROMETHEUS_URL=http://prometheus:9090

# Wazuh
WAZUH_API_URL=
WAZUH_API_KEY=
ENVEOF
    echo -e "${GREEN}✓ Environment file created (.env)${NC}"
else
    echo -e "${YELLOW}⚠ Environment file already exists${NC}"
fi

# Build Docker images
echo -e "\n${BLUE}Building Docker images...${NC}"
docker-compose build

# Start services
echo -e "\n${BLUE}Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "\n${BLUE}Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "\n${BLUE}Checking service health...${NC}"

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend API is running${NC}"
else
    echo -e "${RED}✗ Backend API is not responding${NC}"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠ Frontend may still be starting...${NC}"
fi

# Print success message
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║          🎉 Setup Complete! 🎉                                 ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${CYAN}Access your application:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Frontend Dashboard:${NC}  http://localhost:3000"
echo -e "${GREEN}Backend API:${NC}         http://localhost:8000"
echo -e "${GREEN}API Documentation:${NC}   http://localhost:8000/docs"
echo -e "${GREEN}Grafana:${NC}             http://localhost:3001"
echo -e "${GREEN}Prometheus:${NC}          http://localhost:9090"

echo -e "\n${CYAN}Default Login Credentials:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Email:${NC}     admin@itechsmart.dev"
echo -e "${GREEN}Password:${NC}  admin123"
echo -e "${RED}⚠ IMPORTANT: Change this password immediately!${NC}"

echo -e "\n${CYAN}Next Steps:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "1. Open ${GREEN}http://localhost:3000${NC} in your browser"
echo -e "2. Login with the default credentials"
echo -e "3. Change your password in Settings"
echo -e "4. Configure your integrations in the dashboard"
echo -e "5. Read the ${GREEN}IMPLEMENTATION_GUIDE.md${NC} for detailed setup"

echo -e "\n${CYAN}Useful Commands:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}View logs:${NC}           docker-compose logs -f"
echo -e "${GREEN}Stop services:${NC}       docker-compose down"
echo -e "${GREEN}Restart services:${NC}    docker-compose restart"
echo -e "${GREEN}Check status:${NC}        docker-compose ps"

echo -e "\n${CYAN}Documentation:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Implementation Guide:${NC}  IMPLEMENTATION_GUIDE.md"
echo -e "${GREEN}README:${NC}                README.md"
echo -e "${GREEN}API Docs:${NC}              http://localhost:8000/docs"

echo -e "\n${GREEN}Happy integrating! 🚀${NC}\n"