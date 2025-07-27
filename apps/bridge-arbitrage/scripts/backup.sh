#!/bin/bash
# Backup script for Bridge-Arbitrage database

# Check if we're in the correct directory
cd $(dirname "$0")/..

# Create backups directory if it doesn't exist
mkdir -p backups

# Get current date for backup file
date=$(date +%Y%m%d_%H%M%S)

# Create backup
docker-compose exec db pg_dump -U postgres bridge_arbitrage > backups/backup_${date}.sql

# Compress backup
gzip backups/backup_${date}.sql

# Remove backups older than 7 days
find backups -type f -name "backup_*.sql.gz" -mtime +7 -exec rm {} \;

echo "Backup created: backups/backup_${date}.sql.gz"
