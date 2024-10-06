# Django AWS Deployment Project Summary

## Project Overview

- Personal Django website hosted on AWS EC2
- Utilizes Docker, Nginx, and Gunicorn
- Main goal: Implement secure CI/CD using GitHub Actions and AWS Systems Manager
- Learning exercise for the developer

## Current Setup

- EC2 instance running Ubuntu
- RDS Postgres database for production
- CloudFlare for DNS management and HTTPS
- Docker for containerization
- GitHub for version control
- Two existing GitHub workflow files

## Recent Updates

- Created IAM role for EC2 instance with AmazonSSMManagedInstanceCore policy
- Updated IAM user permissions to include necessary Systems Manager actions
- Implemented image optimization script

## Image Optimization

The project now includes an image optimization script with the following features:
- Processes images to create both JPEG and WebP versions
- Resizes large images to a maximum dimension of 1200x1200 pixels
- Ensures all processed images are under 500 KB
- Preserves original images in a separate directory
- Utilizes multi-threading for efficient processing

To run the image optimization script:
```
python backend/scripts/optimize_images.py
```

## Development vs Production Differences

- Development uses venv, SQLite, and localhost
- Production uses Docker, RDS Postgres, and is publicly accessible
- Separate configuration files for dev and prod environments

## Key Files

- docker-compose.prod.yml
- Dockerfile.prod
- requirements.prod.txt
- backend/scripts/optimize_images.py

## Backup Strategy

This project uses automated backup scripts for both development and production environments.

### Development Backups
- Location: `/home/critter/backups/website`
- Frequency: Weekly (every Sunday at 1 AM)
- Retention: 14 days
- What's backed up: All website files and database
- Script location: `/home/critter/projects/website/backend/scripts/dev_backup.sh`

### Production Backups
- Location: Private S3 bucket
- Frequency: Weekly (every Sunday at 1 AM)
- Retention: 30 days
- What's backed up: All website files and database
- Script location: `/opt/website/backend/scripts/prod_backup.sh`

To restore from a backup:
1. For files: Extract the `.tar.gz` file to the appropriate directory.
2. For database: Use `psql` or `pg_restore` to restore the `.sql.gz` file.

Note: Always test restores in a safe, non-production environment first.

This project serves as a comprehensive learning exercise in modern web application deployment, incorporating various AWS services, containerization, CI/CD practices, and image optimization techniques.
