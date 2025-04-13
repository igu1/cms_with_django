#!/bin/bash

# Script to backup PostgreSQL database from Docker container

# Configuration
BACKUP_DIR="./backups"
DATETIME=$(date +%Y-%m-%d_%H-%M-%S)
FILENAME="${BACKUP_DIR}/backup_${DATETIME}.sql"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "Starting database backup..."

# Create backup
docker-compose exec -T db pg_dump -U postgres customer_management > "${FILENAME}"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Database backup created successfully: ${FILENAME}"
    
    # Compress the backup
    echo "Compressing backup..."
    gzip "${FILENAME}"
    echo "Compressed backup: ${FILENAME}.gz"
    
    # Delete old backups
    echo "Cleaning up old backups (older than ${RETENTION_DAYS} days)..."
    find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
    
    echo "Backup process completed successfully!"
else
    echo "Error: Database backup failed!"
    exit 1
fi
