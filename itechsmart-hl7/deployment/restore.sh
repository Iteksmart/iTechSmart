#!/bin/bash
# Database Restore Script for iTechSmart HL7

set -e

# Configuration
BACKUP_DIR="/backups"

# Database Configuration
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-itechsmart_hl7}"
DB_USER="${POSTGRES_USER:-itechsmart}"
DB_PASSWORD="${POSTGRES_PASSWORD}"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Check if backup file is provided
if [ -z "$1" ]; then
    log "ERROR: No backup file specified"
    log "Usage: $0 <backup_file>"
    log ""
    log "Available backups:"
    ls -lh "${BACKUP_DIR}"/postgres_*.sql.gz 2>/dev/null || log "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    log "ERROR: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Confirmation prompt
log "WARNING: This will restore the database from backup and overwrite existing data!"
log "Backup file: ${BACKUP_FILE}"
log "Database: ${DB_NAME} on ${DB_HOST}:${DB_PORT}"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    log "Restore cancelled"
    exit 0
fi

# Create backup of current database before restore
log "Creating backup of current database before restore..."
CURRENT_BACKUP="${BACKUP_DIR}/pre_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
PGPASSWORD="${DB_PASSWORD}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --format=custom \
    --compress=9 \
    | gzip > "${CURRENT_BACKUP}"

log "Current database backed up to: ${CURRENT_BACKUP}"

# Terminate existing connections
log "Terminating existing database connections..."
PGPASSWORD="${DB_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();"

# Drop and recreate database
log "Dropping and recreating database..."
PGPASSWORD="${DB_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "DROP DATABASE IF EXISTS ${DB_NAME};"

PGPASSWORD="${DB_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "CREATE DATABASE ${DB_NAME};"

# Restore from backup
log "Restoring database from backup..."
gunzip -c "${BACKUP_FILE}" | PGPASSWORD="${DB_PASSWORD}" pg_restore \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --verbose \
    --no-owner \
    --no-acl

if [ $? -eq 0 ]; then
    log "Database restore completed successfully"
else
    log "ERROR: Database restore failed!"
    log "Attempting to restore from pre-restore backup..."
    gunzip -c "${CURRENT_BACKUP}" | PGPASSWORD="${DB_PASSWORD}" pg_restore \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --verbose \
        --no-owner \
        --no-acl
    exit 1
fi

# Verify restore
log "Verifying database restore..."
TABLE_COUNT=$(PGPASSWORD="${DB_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

log "Tables restored: ${TABLE_COUNT}"

if [ "${TABLE_COUNT}" -gt 0 ]; then
    log "Database restore verified successfully"
else
    log "WARNING: No tables found in restored database"
fi

log "Restore process completed"

# Send notification (optional)
if [ -n "${SLACK_WEBHOOK_URL}" ]; then
    curl -X POST "${SLACK_WEBHOOK_URL}" \
        -H 'Content-Type: application/json' \
        -d "{&quot;text&quot;:&quot;✅ iTechSmart HL7 database restored successfully\n• Backup: ${BACKUP_FILE}\n• Tables: ${TABLE_COUNT}&quot;}"
fi

exit 0