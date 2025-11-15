#!/bin/bash
# Automated Backup Script for iTechSmart HL7

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Database Configuration
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-itechsmart_hl7}"
DB_USER="${POSTGRES_USER:-itechsmart}"
DB_PASSWORD="${POSTGRES_PASSWORD}"

# S3 Configuration (optional)
S3_BUCKET="${S3_BACKUP_BUCKET:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Database Backup
log "Starting database backup..."
BACKUP_FILE="${BACKUP_DIR}/postgres_${TIMESTAMP}.sql.gz"

PGPASSWORD="${DB_PASSWORD}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --format=custom \
    --compress=9 \
    --verbose \
    | gzip > "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    log "Database backup completed: ${BACKUP_FILE}"
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    log "Backup size: ${BACKUP_SIZE}"
else
    log "ERROR: Database backup failed!"
    exit 1
fi

# Verify backup integrity
log "Verifying backup integrity..."
gunzip -t "${BACKUP_FILE}"
if [ $? -eq 0 ]; then
    log "Backup integrity verified successfully"
else
    log "ERROR: Backup integrity check failed!"
    exit 1
fi

# Upload to S3 (if configured)
if [ -n "${S3_BUCKET}" ]; then
    log "Uploading backup to S3..."
    aws s3 cp "${BACKUP_FILE}" "s3://${S3_BUCKET}/backups/postgres_${TIMESTAMP}.sql.gz" \
        --region "${AWS_REGION}" \
        --storage-class STANDARD_IA
    
    if [ $? -eq 0 ]; then
        log "Backup uploaded to S3 successfully"
    else
        log "WARNING: S3 upload failed, backup retained locally"
    fi
fi

# Cleanup old backups
log "Cleaning up old backups (older than ${RETENTION_DAYS} days)..."
find "${BACKUP_DIR}" -name "postgres_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
log "Cleanup completed"

# Backup statistics
TOTAL_BACKUPS=$(find "${BACKUP_DIR}" -name "postgres_*.sql.gz" -type f | wc -l)
TOTAL_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)
log "Total backups: ${TOTAL_BACKUPS}"
log "Total backup size: ${TOTAL_SIZE}"

log "Backup process completed successfully"

# Send notification (optional)
if [ -n "${SLACK_WEBHOOK_URL}" ]; then
    curl -X POST "${SLACK_WEBHOOK_URL}" \
        -H 'Content-Type: application/json' \
        -d "{&quot;text&quot;:&quot;✅ iTechSmart HL7 backup completed successfully\n• Backup: ${BACKUP_FILE}\n• Size: ${BACKUP_SIZE}\n• Total backups: ${TOTAL_BACKUPS}&quot;}"
fi

exit 0