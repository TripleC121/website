#!/bin/bash

# Load environment variables
source /home/critter/projects/website/.env.dev

# Set variables
BACKUP_DIR="/media/critter/USB31FD/website_backups"
WEBSITE_DIR="/home/critter/projects/website"
DB_PATH="${WEBSITE_DIR}/db.sqlite3"
TIMESTAMP=$(date +"%Y%m%d")
LOG_DIR="/home/critter/projects/website/backend/logs"
LOG_FILE="$LOG_DIR/dev_backup.log"
LAST_BACKUP_FILE="$LOG_DIR/last_backup"

# Function for logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if it's been more than a week since the last backup
if [ -f "$LAST_BACKUP_FILE" ]; then
    last_backup=$(cat "$LAST_BACKUP_FILE")
    current_time=$(date +%s)
    if [ $((current_time - last_backup)) -lt 604800 ]; then  # 604800 seconds = 1 week
        log "Less than a week since last backup. Exiting."
        exit 0
    fi
fi

log "Starting development backup process"

# Backup website files (excluding the SQLite database)
log "Backing up website files"
tar --exclude='./db.sqlite3' -czf "$BACKUP_DIR/dev_website_files_$TIMESTAMP.tar.gz" -C "$WEBSITE_DIR" .
if [ $? -eq 0 ]; then
    log "Website files backup successful"
else
    log "Error: Website files backup failed"
    exit 1
fi

# Backup SQLite database
log "Backing up SQLite database"
if [ -f "$DB_PATH" ]; then
    sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/dev_db_backup_$TIMESTAMP.sqlite'"
    if [ $? -eq 0 ]; then
        log "SQLite database backup successful"
    else
        log "Error: SQLite database backup failed"
        exit 1
    fi
else
    log "Warning: SQLite database file not found at $DB_PATH"
fi

# Remove backups older than 14 days
log "Removing old backups"
find "$BACKUP_DIR" -name "dev_*" -type f -mtime +14 -delete

# Update last backup time
date +%s > "$LAST_BACKUP_FILE"
