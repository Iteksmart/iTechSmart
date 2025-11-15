# iTechSmart DataFlow - Deployment Guide

## Quick Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disk space

### Local Development Deployment

1. **Clone and Navigate**
```bash
cd itechsmart-dataflow
```

2. **Configure Environment**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Frontend (optional)
# Frontend uses environment variables from Vite
```

3. **Start All Services**
```bash
docker-compose up -d
```

4. **Verify Services**
```bash
docker-compose ps
```

5. **Access Applications**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (admin/minioadmin)

### Production Deployment

#### Using Docker Compose

1. **Update Environment Variables**
```bash
# Set production values in backend/.env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-db-url>
```

2. **Build Production Images**
```bash
docker-compose -f docker-compose.prod.yml build
```

3. **Deploy**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Using Kubernetes

1. **Create Namespace**
```bash
kubectl create namespace dataflow
```

2. **Apply Configurations**
```bash
kubectl apply -f k8s/
```

3. **Verify Deployment**
```bash
kubectl get pods -n dataflow
kubectl get services -n dataflow
```

### Cloud Deployment

#### AWS ECS

```bash
# Build and push images
docker build -t dataflow-backend:latest backend/
docker tag dataflow-backend:latest <ecr-repo>/dataflow-backend:latest
docker push <ecr-repo>/dataflow-backend:latest

# Deploy using ECS CLI or Console
```

#### Azure Container Instances

```bash
az container create \
  --resource-group dataflow-rg \
  --name dataflow-backend \
  --image <acr-repo>/dataflow-backend:latest \
  --cpu 2 --memory 4
```

#### Google Cloud Run

```bash
gcloud run deploy dataflow-backend \
  --image gcr.io/<project>/dataflow-backend:latest \
  --platform managed \
  --region us-central1
```

## Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Check all services
docker-compose ps
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Metrics
- Prometheus: http://localhost:9090
- Grafana: Configure to connect to Prometheus

## Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Clean restart
docker-compose down -v
docker-compose up -d
```

### Database Connection Issues
```bash
# Check PostgreSQL
docker-compose logs postgres

# Connect to database
docker exec -it dataflow-postgres psql -U dataflow
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Scale services
docker-compose up -d --scale backend=3
```

## Backup & Recovery

### Database Backup
```bash
# Backup PostgreSQL
docker exec dataflow-postgres pg_dump -U dataflow dataflow > backup.sql

# Restore
docker exec -i dataflow-postgres psql -U dataflow dataflow < backup.sql
```

### Data Backup
```bash
# Backup MinIO data
docker exec dataflow-minio mc mirror /data /backup
```

## Security

### SSL/TLS Configuration
```bash
# Use nginx or traefik as reverse proxy
# Configure SSL certificates
# Update CORS settings in backend/.env
```

### Secrets Management
```bash
# Use environment variables
# Or integrate with HashiCorp Vault
# Or use cloud provider secrets manager
```

## Scaling

### Horizontal Scaling
```bash
# Scale backend
docker-compose up -d --scale backend=3

# Use load balancer (nginx/traefik)
```

### Database Scaling
```bash
# Use read replicas
# Configure connection pooling
# Implement caching with Redis
```

## Maintenance

### Updates
```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose up -d
```

### Cleanup
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```

---

For more information, see the main [README.md](README.md)