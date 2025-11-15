#!/bin/bash

# ProofLink.AI Backup Script
# This script creates backups of the database and uploaded files

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Database backup
echo "Starting database backup..."
docker exec prooflink-postgres pg_dump -U prooflink prooflink | gzip > "${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz"
echo "Database backup completed: db_backup_${TIMESTAMP}.sql.gz"

# Uploads backup
echo "Starting uploads backup..."
docker run --rm -v prooflink_upload_data:/data -v ${BACKUP_DIR}:/backup alpine tar czf /backup/uploads_backup_${TIMESTAMP}.tar.gz -C /data .
echo "Uploads backup completed: uploads_backup_${TIMESTAMP}.tar.gz"

# Redis backup
echo "Starting Redis backup..."
docker exec prooflink-redis redis-cli --rdb /data/dump.rdb SAVE
docker cp prooflink-redis:/data/dump.rdb "${BACKUP_DIR}/redis_backup_${TIMESTAMP}.rdb"
echo "Redis backup completed: redis_backup_${TIMESTAMP}.rdb"

# Clean old backups
echo "Cleaning old backups (older than ${RETENTION_DAYS} days)..."
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "*.rdb" -mtime +${RETENTION_DAYS} -delete

echo "Backup completed successfully!"
echo "Backup location: ${BACKUP_DIR}"
ls -lh ${BACKUP_DIR}/*${TIMESTAMP}*