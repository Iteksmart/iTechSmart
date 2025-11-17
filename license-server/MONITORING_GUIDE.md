# iTechSmart License Server - Monitoring & Maintenance Guide

## Overview
This guide provides comprehensive monitoring, logging, and maintenance procedures for the iTechSmart License Server.

## Table of Contents
1. [Health Monitoring](#health-monitoring)
2. [Performance Monitoring](#performance-monitoring)
3. [Log Management](#log-management)
4. [Database Monitoring](#database-monitoring)
5. [Security Monitoring](#security-monitoring)
6. [Alerting](#alerting)
7. [Backup & Recovery](#backup--recovery)
8. [Maintenance Tasks](#maintenance-tasks)

## Health Monitoring

### Built-in Health Check

The license server provides a health check endpoint at `/health`:

```bash
curl http://localhost:3001/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-16T17:10:00.000Z",
  "uptime": 3600,
  "database": "connected",
  "version": "1.0.0"
}
```

### Uptime Monitoring Services

#### UptimeRobot Setup
1. Sign up at https://uptimerobot.com
2. Create new monitor:
   - Monitor Type: HTTP(s)
   - URL: https://licenses.yourdomain.com/health
   - Monitoring Interval: 5 minutes
   - Alert Contacts: Your email/SMS

#### Pingdom Setup
1. Sign up at https://www.pingdom.com
2. Add new check:
   - Check Type: HTTP
   - URL: https://licenses.yourdomain.com/health
   - Check Interval: 1 minute
   - Alert Policy: Email + SMS

#### StatusCake Setup
1. Sign up at https://www.statuscake.com
2. Create uptime test:
   - Test Type: HTTP
   - Website URL: https://licenses.yourdomain.com/health
   - Check Rate: 5 minutes

### Docker Health Checks

The Docker container includes built-in health checks:

```bash
# Check container health status
docker compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' itechsmart-license-server | jq
```

### Kubernetes Health Probes

If deploying to Kubernetes, use these probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3001
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 3001
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

## Performance Monitoring

### Application Metrics

#### Response Time Monitoring

Create a monitoring script:

```bash
#!/bin/bash
# monitor-response-time.sh

ENDPOINT="http://localhost:3001/health"
THRESHOLD=1000  # milliseconds

while true; do
  START=$(date +%s%3N)
  curl -s "$ENDPOINT" > /dev/null
  END=$(date +%s%3N)
  DURATION=$((END - START))
  
  echo "$(date): Response time: ${DURATION}ms"
  
  if [ $DURATION -gt $THRESHOLD ]; then
    echo "WARNING: Response time exceeded threshold!"
    # Send alert here
  fi
  
  sleep 60
done
```

#### Request Rate Monitoring

Monitor API request rates:

```bash
# View request logs
docker compose logs license-server | grep "POST\|GET\|PUT\|DELETE" | tail -100

# Count requests per minute
docker compose logs --since 1m license-server | grep -c "HTTP"
```

### Resource Monitoring

#### CPU and Memory Usage

```bash
# Monitor container resources
docker stats itechsmart-license-server

# Get detailed metrics
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

#### Disk Usage

```bash
# Check disk usage
df -h

# Check Docker volumes
docker system df -v

# Check PostgreSQL data size
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT pg_size_pretty(pg_database_size('itechsmart_licenses')) as size;
"
```

### Prometheus Integration

#### Install Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'license-server'
    static_configs:
      - targets: ['license-server:3001']
    metrics_path: '/metrics'
```

#### Add to Docker Compose

```yaml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
```

### Grafana Dashboards

#### Install Grafana

```yaml
grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
  depends_on:
    - prometheus
```

#### Dashboard Metrics
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (%)
- Active connections
- Database query time
- License validations/minute
- API calls/day per organization

## Log Management

### Log Levels

The server supports these log levels:
- `error`: Critical errors
- `warn`: Warning messages
- `info`: Informational messages (default)
- `debug`: Debug information
- `verbose`: Detailed logs

Set via environment variable:
```bash
LOG_LEVEL=info
```

### Viewing Logs

#### Real-time Logs
```bash
# Follow all logs
docker compose logs -f license-server

# Follow with timestamp
docker compose logs -f -t license-server

# Last 100 lines
docker compose logs --tail=100 license-server
```

#### Filtered Logs
```bash
# Error logs only
docker compose logs license-server | grep ERROR

# Specific time range
docker compose logs --since 2025-11-16T10:00:00 --until 2025-11-16T12:00:00 license-server

# Search for specific pattern
docker compose logs license-server | grep "license validation"
```

### Log Rotation

#### Configure Logrotate

Create `/etc/logrotate.d/docker-containers`:

```
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=10M
    missingok
    delaycompress
    copytruncate
}
```

Test configuration:
```bash
sudo logrotate -d /etc/logrotate.d/docker-containers
```

### Centralized Logging

#### ELK Stack (Elasticsearch, Logstash, Kibana)

Add to docker-compose.yml:

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  environment:
    - discovery.type=single-node
    - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
  ports:
    - "9200:9200"
  volumes:
    - elasticsearch_data:/usr/share/elasticsearch/data

logstash:
  image: docker.elastic.co/logstash/logstash:8.11.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  depends_on:
    - elasticsearch

kibana:
  image: docker.elastic.co/kibana/kibana:8.11.0
  ports:
    - "5601:5601"
  environment:
    - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
  depends_on:
    - elasticsearch
```

#### Loki + Grafana

```yaml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"
  volumes:
    - loki_data:/loki

promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/log:/var/log
    - ./promtail-config.yml:/etc/promtail/config.yml
  command: -config.file=/etc/promtail/config.yml
```

## Database Monitoring

### Connection Pool Monitoring

```bash
# Check active connections
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT count(*) as active_connections 
  FROM pg_stat_activity 
  WHERE state = 'active';
"

# Check connection details
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT pid, usename, application_name, client_addr, state, query_start, query
  FROM pg_stat_activity
  WHERE datname = 'itechsmart_licenses';
"
```

### Query Performance

```bash
# Slow queries
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT query, calls, total_time, mean_time, max_time
  FROM pg_stat_statements
  ORDER BY mean_time DESC
  LIMIT 10;
"

# Table sizes
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables
  WHERE schemaname = 'public'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### Index Usage

```bash
# Check index usage
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
  FROM pg_stat_user_indexes
  ORDER BY idx_scan DESC;
"

# Unused indexes
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
  FROM pg_stat_user_indexes
  WHERE idx_scan = 0
  ORDER BY pg_relation_size(indexrelid) DESC;
"
```

### Database Health

```bash
# Database size
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT pg_size_pretty(pg_database_size('itechsmart_licenses'));
"

# Table bloat
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as indexes_size
  FROM pg_tables
  WHERE schemaname = 'public'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

## Security Monitoring

### Failed Login Attempts

```bash
# Monitor failed logins
docker compose logs license-server | grep "Failed login attempt"

# Count failed logins by IP
docker compose logs license-server | grep "Failed login" | awk '{print $NF}' | sort | uniq -c | sort -rn
```

### Rate Limit Violations

```bash
# Monitor rate limit hits
docker compose logs license-server | grep "Rate limit exceeded"

# Count by IP
docker compose logs license-server | grep "Rate limit" | awk '{print $NF}' | sort | uniq -c | sort -rn
```

### Suspicious Activity

```bash
# Monitor for SQL injection attempts
docker compose logs license-server | grep -i "drop\|delete\|truncate\|insert"

# Monitor for unusual license validation patterns
docker compose logs license-server | grep "License validation" | awk '{print $NF}' | sort | uniq -c | sort -rn
```

### SSL Certificate Monitoring

```bash
# Check certificate expiration
echo | openssl s_client -servername licenses.yourdomain.com -connect licenses.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

# Days until expiration
echo | openssl s_client -servername licenses.yourdomain.com -connect licenses.yourdomain.com:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2 | xargs -I {} date -d {} +%s | awk '{print int(($1 - systime()) / 86400)}'
```

## Alerting

### Email Alerts

Create alert script:

```bash
#!/bin/bash
# alert.sh

RECIPIENT="admin@yourdomain.com"
SUBJECT="License Server Alert"
MESSAGE=$1

echo "$MESSAGE" | mail -s "$SUBJECT" "$RECIPIENT"
```

### Slack Alerts

```bash
#!/bin/bash
# slack-alert.sh

WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
MESSAGE=$1

curl -X POST "$WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d "{&quot;text&quot;: &quot;$MESSAGE&quot;}"
```

### PagerDuty Integration

```bash
#!/bin/bash
# pagerduty-alert.sh

INTEGRATION_KEY="your-integration-key"
MESSAGE=$1

curl -X POST https://events.pagerduty.com/v2/enqueue \
  -H 'Content-Type: application/json' \
  -d "{
    &quot;routing_key&quot;: &quot;$INTEGRATION_KEY&quot;,
    &quot;event_action&quot;: &quot;trigger&quot;,
    &quot;payload&quot;: {
      &quot;summary&quot;: &quot;$MESSAGE&quot;,
      &quot;severity&quot;: &quot;error&quot;,
      &quot;source&quot;: &quot;license-server&quot;
    }
  }"
```

### Alert Conditions

Monitor and alert on:

1. **Service Down**
   - Health check fails for 3 consecutive checks
   - Container restarts

2. **High Error Rate**
   - Error rate > 5% over 5 minutes
   - 500 errors > 10 in 1 minute

3. **Performance Degradation**
   - Response time > 2 seconds (p95)
   - Database query time > 1 second

4. **Resource Exhaustion**
   - CPU usage > 80% for 5 minutes
   - Memory usage > 90%
   - Disk usage > 85%

5. **Security Issues**
   - Failed login attempts > 10 in 1 minute
   - Rate limit violations > 100 in 1 minute
   - SSL certificate expires in < 30 days

6. **Database Issues**
   - Connection pool exhausted
   - Slow queries > 5 seconds
   - Database size > 80% of allocated space

## Backup & Recovery

### Database Backups

#### Automated Backup Script

```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/itechsmart_licenses_$DATE.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Perform backup
docker compose exec -T postgres pg_dump -U postgres itechsmart_licenses > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

#### Schedule Backups

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup-database.sh

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /path/to/backup-database.sh
```

#### Backup to S3

```bash
#!/bin/bash
# backup-to-s3.sh

BACKUP_DIR="/backups/postgres"
S3_BUCKET="s3://your-bucket/license-server-backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
docker compose exec -T postgres pg_dump -U postgres itechsmart_licenses | gzip > "/tmp/backup_$DATE.sql.gz"

# Upload to S3
aws s3 cp "/tmp/backup_$DATE.sql.gz" "$S3_BUCKET/"

# Cleanup
rm "/tmp/backup_$DATE.sql.gz"
```

### Database Restore

```bash
#!/bin/bash
# restore-database.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file.sql.gz>"
  exit 1
fi

# Stop license server
docker compose stop license-server

# Decompress backup
gunzip -c "$BACKUP_FILE" > /tmp/restore.sql

# Drop and recreate database
docker compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS itechsmart_licenses;"
docker compose exec postgres psql -U postgres -c "CREATE DATABASE itechsmart_licenses;"

# Restore backup
docker compose exec -T postgres psql -U postgres itechsmart_licenses < /tmp/restore.sql

# Cleanup
rm /tmp/restore.sql

# Start license server
docker compose start license-server

echo "Database restored successfully"
```

### Configuration Backups

```bash
#!/bin/bash
# backup-config.sh

BACKUP_DIR="/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup configuration files
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
  .env \
  docker-compose.yml \
  Dockerfile \
  prisma/schema.prisma

echo "Configuration backup completed: $BACKUP_DIR/config_$DATE.tar.gz"
```

## Maintenance Tasks

### Daily Tasks

1. **Check Health Status**
```bash
curl http://localhost:3001/health
```

2. **Review Error Logs**
```bash
docker compose logs --since 24h license-server | grep ERROR
```

3. **Monitor Resource Usage**
```bash
docker stats --no-stream itechsmart-license-server
```

### Weekly Tasks

1. **Database Vacuum**
```bash
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "VACUUM ANALYZE;"
```

2. **Review Slow Queries**
```bash
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  ORDER BY mean_time DESC
  LIMIT 10;
"
```

3. **Check Disk Usage**
```bash
df -h
docker system df
```

4. **Review Security Logs**
```bash
docker compose logs --since 7d license-server | grep -i "failed\|unauthorized\|forbidden"
```

### Monthly Tasks

1. **Update Dependencies**
```bash
cd license-server
npm update
npm audit fix
```

2. **Review and Archive Old Logs**
```bash
find /var/log -name "*.log" -mtime +90 -delete
```

3. **Database Optimization**
```bash
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "REINDEX DATABASE itechsmart_licenses;"
```

4. **SSL Certificate Check**
```bash
echo | openssl s_client -servername licenses.yourdomain.com -connect licenses.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

5. **Backup Verification**
```bash
# Test restore on a separate instance
./restore-database.sh /backups/postgres/latest_backup.sql.gz
```

### Quarterly Tasks

1. **Security Audit**
   - Review access logs
   - Update passwords
   - Review API key usage
   - Check for unused accounts

2. **Performance Review**
   - Analyze response times
   - Review database query performance
   - Optimize slow endpoints
   - Review and update indexes

3. **Capacity Planning**
   - Review growth trends
   - Plan for scaling
   - Review resource allocation
   - Update infrastructure if needed

4. **Disaster Recovery Test**
   - Test backup restoration
   - Verify failover procedures
   - Update documentation
   - Train team on recovery procedures

## Monitoring Dashboard

### Create Custom Dashboard

```bash
#!/bin/bash
# dashboard.sh

while true; do
  clear
  echo "=== iTechSmart License Server Dashboard ==="
  echo "Time: $(date)"
  echo ""
  
  # Health Status
  echo "=== Health Status ==="
  curl -s http://localhost:3001/health | jq .
  echo ""
  
  # Container Status
  echo "=== Container Status ==="
  docker compose ps
  echo ""
  
  # Resource Usage
  echo "=== Resource Usage ==="
  docker stats --no-stream itechsmart-license-server
  echo ""
  
  # Database Connections
  echo "=== Database Connections ==="
  docker compose exec postgres psql -U postgres -d itechsmart_licenses -t -c "
    SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
  "
  echo ""
  
  # Recent Errors
  echo "=== Recent Errors (Last 10) ==="
  docker compose logs --tail=100 license-server | grep ERROR | tail -10
  echo ""
  
  sleep 30
done
```

Run the dashboard:
```bash
chmod +x dashboard.sh
./dashboard.sh
```

## Support

For monitoring and maintenance support:
- GitHub Issues: https://github.com/Iteksmart/iTechSmart/issues
- Email: support@itechsmart.com
- Documentation: https://docs.itechsmart.com