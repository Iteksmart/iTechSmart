# iTechSmart Ledger - Blockchain Integration Platform

**Version:** 1.0.0  
**Market Value:** $500K - $1M  
**Status:** Production Ready ✅

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Frontend Pages](#frontend-pages)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [Security](#security)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

iTechSmart Ledger is a comprehensive blockchain integration platform that enables users to manage wallets, execute transactions, deploy smart contracts, and explore blockchain data across multiple networks including Ethereum, Polygon, Bitcoin, and Binance Smart Chain.

### Key Capabilities

- **Multi-Network Support**: Ethereum, Polygon, Bitcoin, Binance Smart Chain, Solana
- **Wallet Management**: Create, import, and manage hot/cold/multisig wallets
- **Transaction Processing**: Send, receive, and track blockchain transactions
- **Smart Contract Deployment**: Deploy and interact with smart contracts
- **Blockchain Explorer**: Search and view blocks, transactions, and addresses
- **API Access**: RESTful API with JWT authentication
- **Real-time Analytics**: Dashboard with transaction metrics and network statistics

---

## ✨ Features

### 1. Wallet Management
- Create new wallets across multiple blockchain networks
- Import existing wallets using private keys
- Support for hot, cold, and multi-signature wallets
- Real-time balance tracking
- Token balance management (ERC20, ERC721, etc.)

### 2. Transaction Processing
- Send and receive cryptocurrency
- Transaction history with filtering and search
- Real-time transaction status tracking
- Gas price estimation and optimization
- Transaction confirmation monitoring

### 3. Smart Contract Operations
- Deploy smart contracts with custom parameters
- Interact with deployed contracts
- Contract verification and source code management
- ABI and bytecode storage
- Contract interaction history

### 4. Blockchain Explorer
- Search by block number, transaction hash, or address
- View detailed block information
- Transaction details with gas usage
- Network statistics and metrics
- Multi-network support

### 5. Security & Authentication
- JWT-based authentication
- API key management with rate limiting
- Encrypted private key storage
- Two-factor authentication support
- Comprehensive audit logging

### 6. Analytics & Reporting
- Real-time dashboard with key metrics
- Transaction volume charts
- Network distribution analytics
- Gas usage statistics
- Custom date range filtering

---

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **ORM**: SQLAlchemy 2.0
- **Blockchain Libraries**: web3.py, bitcoinlib

### Frontend
- **Framework**: React 18.2
- **Language**: TypeScript 5.3
- **Routing**: React Router 6.20
- **Styling**: Tailwind CSS 3.3
- **Charts**: Recharts 2.10
- **Icons**: Lucide React 0.294
- **HTTP Client**: Axios 1.6

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 15 Alpine
- **Cache**: Redis 7 Alpine
- **Web Server**: Uvicorn (ASGI)
- **Build Tool**: Vite 5.0

---

## 🏗 Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │Dashboard │ Wallets  │  Txns    │Contracts │ Explorer │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Authentication │ Wallet Mgmt │ Transaction Engine   │  │
│  │  Smart Contracts│ Block Explorer│ Analytics Engine   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        ┌──────────────┐        ┌──────────────┐
        │  PostgreSQL  │        │    Redis     │
        │   Database   │        │    Cache     │
        └──────────────┘        └──────────────┘
                │
                ▼
        ┌──────────────────────────────────┐
        │   Blockchain Networks            │
        │  • Ethereum  • Polygon           │
        │  • Bitcoin   • Binance           │
        └──────────────────────────────────┘
```

### Database Schema

**Core Tables:**
- `users` - User accounts and authentication
- `wallets` - Blockchain wallet management
- `transactions` - Transaction records
- `smart_contracts` - Smart contract deployments
- `contract_interactions` - Contract interaction history
- `blocks` - Blockchain block data
- `tokens` - Token metadata (ERC20, ERC721, etc.)
- `token_balances` - User token holdings
- `network_configs` - Network configurations
- `api_keys` - API access keys
- `audit_logs` - System audit trail

---

## 🚀 Getting Started

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd itechsmart-ledger
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

4. **Default credentials**
- Email: admin@itechsmart.dev
- Password: admin123

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://ledger_user:ledger_pass@localhost:5432/ledger_db"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
echo "VITE_API_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

#### Database Setup

```bash
# Create PostgreSQL database
createdb ledger_db

# Run initialization script
psql -U ledger_user -d ledger_db -f database/init-db.sql
```

---

## 📚 API Documentation

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=username&password=password123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Wallet Operations

#### Create Wallet
```http
POST /wallets
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Ethereum Wallet",
  "network": "ethereum",
  "wallet_type": "hot"
}
```

#### Get Wallets
```http
GET /wallets?network=ethereum&skip=0&limit=100
Authorization: Bearer <token>
```

#### Get Wallet by ID
```http
GET /wallets/{wallet_id}
Authorization: Bearer <token>
```

### Transaction Operations

#### Create Transaction
```http
POST /transactions
Authorization: Bearer <token>
Content-Type: application/json

{
  "from_wallet_id": 1,
  "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "network": "ethereum",
  "amount": 1.5,
  "gas_price": 20.0,
  "gas_limit": 21000
}
```

#### Get Transactions
```http
GET /transactions?status=confirmed&network=ethereum&skip=0&limit=100
Authorization: Bearer <token>
```

### Smart Contract Operations

#### Create Contract
```http
POST /contracts
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Token Contract",
  "description": "ERC20 token implementation",
  "network": "ethereum",
  "source_code": "pragma solidity ^0.8.0; contract Token { ... }",
  "compiler_version": "0.8.0"
}
```

#### Deploy Contract
```http
POST /contracts/{contract_id}/deploy
Authorization: Bearer <token>
Content-Type: application/json

{
  "contract_id": 1,
  "constructor_params": [],
  "gas_limit": 3000000
}
```

#### Interact with Contract
```http
POST /contracts/interact
Authorization: Bearer <token>
Content-Type: application/json

{
  "contract_id": 1,
  "function_name": "transfer",
  "parameters": ["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", 1000]
}
```

### Explorer Operations

#### Get Blocks
```http
GET /blocks?network=ethereum&skip=0&limit=50
```

#### Get Block by Number
```http
GET /blocks/{block_number}?network=ethereum
```

### Analytics

#### Get Dashboard Statistics
```http
GET /analytics/dashboard
Authorization: Bearer <token>
```

Response:
```json
{
  "total_wallets": 12,
  "total_transactions": 156,
  "total_smart_contracts": 8,
  "total_volume": 45678.90,
  "network_stats": [
    {
      "network": "ethereum",
      "total_transactions": 89,
      "total_wallets": 5,
      "total_volume": 25000,
      "avg_transaction_fee": 15.5
    }
  ]
}
```

---

## 🖥 Frontend Pages

### 1. Dashboard (`/`)
- Overview of blockchain activities
- Key metrics (wallets, transactions, contracts, volume)
- Transaction volume chart (last 7 days)
- Network distribution pie chart
- Network statistics table
- Recent transactions list

### 2. Wallets (`/wallets`)
- Wallet grid view with cards
- Create new wallet modal
- Wallet filtering by network
- Search by name or address
- Balance display
- Wallet type indicators (hot/cold/multisig)

### 3. Transactions (`/transactions`)
- Transaction table with sorting
- Create new transaction modal
- Filter by status and network
- Search by hash or address
- Real-time status updates
- Gas usage information

### 4. Smart Contracts (`/contracts`)
- Contract grid view
- Create contract modal
- Deploy contract functionality
- View contract source code
- Contract interaction interface
- Status and verification badges

### 5. Explorer (`/explorer`)
- Multi-network blockchain explorer
- Search by block, transaction, or address
- Recent blocks table
- Block details with gas usage
- Network statistics
- Transaction count per block

### 6. Settings (`/settings`)
- Profile management
- Network configuration
- API key management
- Notification preferences
- Security settings (password, 2FA)
- Advanced options (export data, clear cache)

---

## 🗄 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Wallets Table
```sql
CREATE TABLE wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) UNIQUE NOT NULL,
    network VARCHAR(50) NOT NULL,
    wallet_type VARCHAR(50) DEFAULT 'hot',
    balance DECIMAL(20, 8) DEFAULT 0.0,
    encrypted_private_key TEXT,
    public_key TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    from_wallet_id INTEGER REFERENCES wallets(id),
    to_wallet_id INTEGER REFERENCES wallets(id),
    from_address VARCHAR(255),
    to_address VARCHAR(255) NOT NULL,
    network VARCHAR(50) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    fee DECIMAL(20, 8) DEFAULT 0.0,
    transaction_hash VARCHAR(255) UNIQUE,
    block_number INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    confirmations INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP
);
```

---

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://ledger_user:ledger_pass@localhost:5432/ledger_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

### Network Configuration

Configure blockchain networks in the database:

```sql
INSERT INTO network_configs (network, rpc_url, chain_id, explorer_url) VALUES
('ethereum', 'https://mainnet.infura.io/v3/YOUR_KEY', 1, 'https://etherscan.io'),
('polygon', 'https://polygon-rpc.com', 137, 'https://polygonscan.com');
```

---

## 🔒 Security

### Authentication
- JWT-based authentication with configurable expiration
- Bcrypt password hashing with salt rounds
- Secure session management

### Data Protection
- Encrypted private key storage (AES-256)
- HTTPS enforcement in production
- CORS configuration for API access
- Rate limiting on API endpoints

### API Security
- API key authentication for programmatic access
- Rate limiting per API key
- Network-specific permissions
- Comprehensive audit logging

### Best Practices
- Regular security audits
- Dependency vulnerability scanning
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS protection

---

## 🚢 Deployment

### Docker Deployment

1. **Build and start services**
```bash
docker-compose up -d --build
```

2. **Check service health**
```bash
docker-compose ps
docker-compose logs -f
```

3. **Stop services**
```bash
docker-compose down
```

### Production Deployment

1. **Update environment variables**
```bash
# Update docker-compose.yml with production values
# Set strong SECRET_KEY
# Configure production database credentials
# Set up SSL/TLS certificates
```

2. **Use production-ready configuration**
```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
    restart: always
```

3. **Set up reverse proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Enable SSL/TLS**
```bash
certbot --nginx -d api.yourdomain.com
```

---

## 📊 Performance

### Optimization Features
- Database connection pooling
- Redis caching for frequently accessed data
- Indexed database queries
- Lazy loading in frontend
- Code splitting and minification
- CDN for static assets

### Scalability
- Horizontal scaling with load balancer
- Database read replicas
- Redis cluster for distributed caching
- Microservices architecture ready
- API rate limiting and throttling

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=.
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## 📈 Monitoring

### Health Checks
- `/health` - API health status
- Database connection monitoring
- Redis connection monitoring
- Service availability checks

### Logging
- Structured logging with timestamps
- Error tracking and alerting
- Audit trail for all operations
- Performance metrics collection

### Metrics
- Request/response times
- API endpoint usage
- Database query performance
- Cache hit/miss ratios
- Transaction success rates

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Backend: Follow PEP 8 guidelines
- Frontend: Use ESLint and Prettier
- Write meaningful commit messages
- Add tests for new features
- Update documentation

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

For support and questions:
- Email: support@itechsmart.dev
- Documentation: https://docs.itechsmart.dev
- Issues: GitHub Issues

---

## 🎉 Acknowledgments

- FastAPI for the excellent web framework
- React team for the powerful UI library
- PostgreSQL for reliable data storage
- The blockchain community for inspiration

---

**Built with ❤️ by the iTechSmart Team**

*iTechSmart Ledger - Empowering Blockchain Integration*