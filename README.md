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

## Next Steps

- Review and update existing GitHub workflow files
- Fix or simplify verification phase of deploy-ssm.yml
- Test and verify deployment process using AWS Systems Manager Session Manager
- Integrate image optimization into the CI/CD pipeline

## Future Goals

- Learn and implement Ansible and Terraform for infrastructure management
- Automate image optimization as part of the deployment process

## Key Files

- docker-compose.prod.yml
- Dockerfile.prod
- requirements.prod.txt
- backend/scripts/optimize_images.py

## Challenges

- Previous deployment script using SSH was failing due to restricted access
- Some GitHub Actions workflows are currently failing and need attention

This project serves as a comprehensive learning exercise in modern web application deployment, incorporating various AWS services, containerization, CI/CD practices, and image optimization techniques.
