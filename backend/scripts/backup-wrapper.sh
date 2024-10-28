#!/bin/bash
# backup-wrapper.sh

# Set environment variables
export DJANGO_SETTINGS_MODULE="chesley_web.settings.production"
export PYTHONPATH="/opt/website"

# Function to display usage
usage() {
    echo "Usage: $0 [--test-mode] [--dry-run] [--db-only] [--files-only] [--env-only] [--verify-only] [--local-only]"
    exit 1
}

# Check if Docker container is running
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "web.*Up"; then
    echo "Error: Docker container is not running"
    exit 1
fi

# Pass arguments to backup-secure.py inside the container
docker-compose -f docker-compose.prod.yml exec -T web python3 /opt/website/backend/scripts/backup-secure.py "$@"

# Check exit status
if [ $? -eq 0 ]; then
    echo "Backup completed successfully"
else
    echo "Backup failed"
    exit 1
fi
