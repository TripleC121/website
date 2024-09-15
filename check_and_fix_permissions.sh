#!/bin/bash

# Script to check and fix permissions for a Django project

# Set the project root directory
PROJECT_ROOT="/home/critter/projects/website"
USER="critter"
GROUP="critter"

# Function to check and set permissions
check_and_set_permissions() {
    local path="$1"
    local type="$2"
    local owner=$(stat -c '%U' "$path")
    local group=$(stat -c '%G' "$path")
    local perms=$(stat -c '%a' "$path")
    
    if [ "$owner" != "$USER" ] || [ "$group" != "$GROUP" ]; then
        echo "Fixing ownership of $path"
        sudo chown $USER:$GROUP "$path"
    fi
    
    if [ "$type" = "dir" ] && [ "$perms" != "775" ]; then
        echo "Fixing permissions of directory $path"
        sudo chmod 775 "$path"
    elif [ "$type" = "file" ] && [ "$perms" != "664" ]; then
        echo "Fixing permissions of file $path"
        sudo chmod 664 "$path"
    fi
}

# Check and fix permissions for all directories
find "$PROJECT_ROOT" -type d -print0 | while IFS= read -r -d '' dir; do
    check_and_set_permissions "$dir" "dir"
done

# Check and fix permissions for all files
find "$PROJECT_ROOT" -type f -print0 | while IFS= read -r -d '' file; do
    check_and_set_permissions "$file" "file"
done

# Make manage.py executable
if [ ! -x "$PROJECT_ROOT/manage.py" ]; then
    echo "Making manage.py executable"
    sudo chmod +x "$PROJECT_ROOT/manage.py"
fi

echo "Permissions check and fix completed for the Django project at $PROJECT_ROOT"
