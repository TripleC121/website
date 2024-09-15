# Deployment Guide

This document outlines the deployment process for Chris Chesley's personal website.

## Prerequisites

- AWS account with EC2 and S3 access
- Docker and Docker Compose installed on the EC2 instance
- GitHub account with access to the repository

## Deployment Steps

1. Set up an EC2 instance with Ubuntu
2. Install Docker and Docker Compose on the EC2 instance
3. Set up an S3 bucket for static files
4. Configure the EC2 security group to allow inbound traffic on ports 80 and 443
5. Set up Nginx on the EC2 instance as a reverse proxy
6. Clone the repository on the EC2 instance
7. Create a `.env.prod` file with production environment variables
8. Build and start the Docker containers:
   ```
   docker-compose -f docker-compose.prod.yml up -d
   ```
9. Run migrations:
   ```
   docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
   ```
10. Collect static files:
    ```
    docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic
    ```

## Continuous Deployment

The project uses GitHub Actions for continuous deployment. The workflow is defined in `.github/workflows/deploy-ssm.yml`.

To set up continuous deployment:

1. Add the following secrets to your GitHub repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `EC2_INSTANCE_ID`
   - `AWS_S3_BUCKET_NAME`
2. Ensure the EC2 instance has the AWS Systems Manager agent installed
3. Configure the EC2 instance's IAM role to allow Systems Manager access

Now, every push to the `main` branch will trigger a deployment to the EC2 instance and sync static files to S3.

## Troubleshooting

- Check the EC2 instance's system log for deployment errors
- Verify that the S3 bucket permissions are correctly set
- Ensure that the EC2 instance has the necessary permissions to pull from the Docker registry and access S3

For any persistent issues, please open an issue on the GitHub repository.
