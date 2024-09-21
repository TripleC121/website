## Adding New Images

When adding new images to the project:

1. Place the images in the input directory specified in your `.env.dev` file
2. Run the image optimization script:
   ```
   docker compose -f docker-compose.yml run --rm web python scripts/optimize_images.py
   ```
3. Use the `<picture>` element in templates to provide WebP images with JPEG fallbacks:
   ```html
   <picture>
     <source srcset="path/to/image.webp" type="image/webp">
     <img src="path/to/image.jpg" alt="Description">
   </picture>
   ```
4. Commit your changes and push to GitHub
5. The CI/CD pipeline will automatically sync the new images to S3 when merged to main

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
4. Test thoroughly to ensure no breaking changes were introduced

## Running Tests

Before submitting a pull request, please run the test suite:

```
docker compose -f docker-compose.yml run --rm web python manage.py test
```

Also, run the linter:

```
docker compose -f docker-compose.yml run --rm web flake8 .
```
