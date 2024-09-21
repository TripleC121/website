## Image Processing

Before deployment, ensure all images are optimized:

1. Place new images in the input directory specified in your `.env.prod` file
2. Run the optimization script:
   ```
   docker compose -f docker-compose.prod.yml run --rm web python scripts/optimize_images.py
   ```
3. Verify that optimized images are in the output directory
4. Sync optimized images to S3 (this is handled by the CI/CD pipeline)

## Updating Dependencies

To update project dependencies in the production environment:

1. SSH into the EC2 instance
2. Navigate to the project directory
3. Run the update script:
   ```
   docker compose -f docker-compose.prod.yml run --rm web python scripts/update_requirements.py
   ```
4. Review the changes in the logs directory
5. Rebuild and restart the Docker containers:
   ```
   docker compose -f docker-compose.prod.yml up -d --build
   ```
