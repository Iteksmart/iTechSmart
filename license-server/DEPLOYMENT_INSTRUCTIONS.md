# License Server Deployment Instructions

## Prerequisites
- Docker and Docker Compose installed
- PostgreSQL 15+
- Redis 7+
- Node.js 20+ (for local development)

## Quick Deploy with Docker (Recommended)

### Step 1: Configure Environment
```bash
cd license-server
cp .env.example .env
# Edit .env with your settings
nano .env
```

### Step 2: Start Services
```bash
docker-compose up -d
```

### Step 3: Verify Deployment
```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs -f license-server

# Test health endpoint
curl http://localhost:3000/api/health
```

### Step 4: Initialize Database
```bash
# Run migrations
docker-compose exec license-server npx prisma migrate deploy

# (Optional) Seed initial data
docker-compose exec license-server npx prisma db seed
```

## Manual Deployment (Without Docker)

### Step 1: Install Dependencies
```bash
cd license-server
npm install
```

### Step 2: Setup Database
```bash
# Install PostgreSQL 15
# Create database
createdb itechsmart_licenses

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/itechsmart_licenses
```

### Step 3: Run Migrations
```bash
npx prisma generate
npx prisma migrate deploy
```

### Step 4: Start Server
```bash
# Development
npm run dev

# Production
npm run build
npm start
```

## Production Deployment

### Using Docker Compose (Recommended)
```bash
# Production docker-compose
docker-compose -f docker-compose.production.yml up -d
```

### Using PM2
```bash
npm install -g pm2
npm run build
pm2 start dist/index.js --name license-server
pm2 save
pm2 startup
```

### Using systemd
```bash
# Create service file
sudo nano /etc/systemd/system/license-server.service

[Unit]
Description=iTechSmart License Server
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/license-server
ExecStart=/usr/bin/node dist/index.js
Restart=always
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable license-server
sudo systemctl start license-server
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name license.itechsmart.dev;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name license.itechsmart.dev;

    ssl_certificate /etc/letsencrypt/live/license.itechsmart.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/license.itechsmart.dev/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## SSL/TLS Setup

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d license.itechsmart.dev

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring

### Health Check
```bash
curl http://localhost:3000/api/health
```

### Logs
```bash
# Docker
docker-compose logs -f license-server

# PM2
pm2 logs license-server

# systemd
sudo journalctl -u license-server -f
```

### Database Status
```bash
# Docker
docker-compose exec postgres psql -U postgres -d itechsmart_licenses -c "SELECT COUNT(*) FROM &quot;License&quot;;"

# Local
psql -U postgres -d itechsmart_licenses -c "SELECT COUNT(*) FROM &quot;License&quot;;"
```

## Testing

### Test API Endpoints
```bash
# Health check
curl http://localhost:3000/api/health

# Register organization
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "organizationName": "Test Corp",
    "domain": "test.com",
    "email": "admin@test.com",
    "password": "SecurePass123!",
    "name": "Test Admin"
  }'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "SecurePass123!"
  }'
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 3000
lsof -i :3000
# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres
# Or
sudo systemctl status postgresql

# Test connection
psql -U postgres -d itechsmart_licenses -c "SELECT 1"
```

### Migration Issues
```bash
# Reset database (WARNING: deletes all data)
npx prisma migrate reset

# Apply migrations
npx prisma migrate deploy
```

## Backup & Restore

### Backup Database
```bash
# Docker
docker-compose exec postgres pg_dump -U postgres itechsmart_licenses > backup.sql

# Local
pg_dump -U postgres itechsmart_licenses > backup.sql
```

### Restore Database
```bash
# Docker
docker-compose exec -T postgres psql -U postgres itechsmart_licenses < backup.sql

# Local
psql -U postgres itechsmart_licenses < backup.sql
```

## Security Checklist

- [ ] Change default passwords in .env
- [ ] Generate strong JWT_SECRET and ENCRYPTION_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (allow only 80, 443)
- [ ] Set up fail2ban
- [ ] Enable database backups
- [ ] Configure log rotation
- [ ] Set up monitoring alerts
- [ ] Review CORS settings
- [ ] Enable rate limiting
- [ ] Keep dependencies updated

## Support

For deployment issues:
- Email: support@itechsmart.dev
- Documentation: https://docs.itechsmart.dev
- GitHub Issues: https://github.com/Iteksmart/iTechSmart/issues