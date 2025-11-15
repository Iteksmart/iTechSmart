#!/bin/bash

# ProofLink.AI Restore Script
# This script restores backups of the database and uploaded files

set -e

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <timestamp>"
    echo "Example: $0 20240115_120000"
    echo ""
    echo "Available backups:"
    ls -lh /backups/db_backup_*.sql.gz 2>/dev/null | awk '{print $9}' | sed 's/.*db_backup_//' | sed 's/.sql.gz//'
    exit 1
fi

TIMESTAMP=$1
BACKUP_DIR="/backups"

# Verify backups exist
if [ ! -f "${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz" ]; then
    echo "Error: Database backup not found: db_backup_${TIMESTAMP}.sql.gz"
    exit 1
fi

if [ ! -f "${BACKUP_DIR}/uploads_backup_${TIMESTAMP}.tar.gz" ]; then
    echo "Error: Uploads backup not found: uploads_backup_${TIMESTAMP}.tar.gz"
    exit 1
fi

# Confirm restore
echo "WARNING: This will overwrite current data!"
echo "Restoring from backup: ${TIMESTAMP}"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Stop services
echo "Stopping services..."
docker-compose stop backend frontend

# Restore database
echo "Restoring database..."
gunzip -c "${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz" | docker exec -i prooflink-postgres psql -U prooflink prooflink
echo "Database restored successfully!"

# Restore uploads
echo "Restoring uploads..."
docker run --rm -v prooflink_upload_data:/data -v ${BACKUP_DIR}:/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/uploads_backup_${TIMESTAMP}.tar.gz -C /data"
echo "Uploads restored successfully!"

# Restore Redis (optional)
if [ -f "${BACKUP_DIR}/redis_backup_${TIMESTAMP}.rdb" ]; then
    echo "Restoring Redis..."
    docker cp "${BACKUP_DIR}/redis_backup_${TIMESTAMP}.rdb" prooflink-redis:/data/dump.rdb
    docker restart prooflink-redis
    echo "Redis restored successfully!"
fi

# Start services
echo "Starting services..."
docker-compose start backend frontend

echo "Restore completed successfully!"
echo "Please verify the application is working correctly."