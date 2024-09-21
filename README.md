## Image Handling

The project uses WebP and JPEG images for improved performance. An image optimization script is provided to convert and resize images as needed.

To use the image optimization script:

1. Place new images in the input directory specified in your `.env.dev` file.
2. Run the script using Docker:
   ```
   docker compose -f docker-compose.yml run --rm web python scripts/optimize_images.py
   ```
3. Optimized WebP and JPEG images will be placed in the output directory, and original images will be moved to the original directory.

## Updating Dependencies

To update project dependencies:

1. Run the update script:
   ```
   docker compose -f docker-compose.yml run --rm web python scripts/update_requirements.py
   ```
2. Review the changes in the logs directory
3. Rebuild the Docker image:
   ```
   docker compose build
   ```
