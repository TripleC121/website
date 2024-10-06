# Contributing to Chris Chesley's Personal Website

We welcome contributions to Chris Chesley's personal website! This document outlines the process for contributing to this project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes, committing them with clear, descriptive commit messages
5. Push your changes to your fork on GitHub
6. Submit a pull request to the main repository

## Development Environment

1. Install Python 3.11 or later
2. Install dependencies: `pip install -r requirements-dev.txt`
3. Copy `.env.example` to `.env` and fill in the required values
4. Run migrations: `python manage.py migrate`
5. Start the development server: `python manage.py runserver`

## Adding New Images

When adding new images to the project:

1. Place the images in the appropriate subdirectory of `static/images/`:
   - `general/` for website pictures
   - `trees/` for tree images
   - `succulents/` for succulent images
2. Run the image optimization script:
   ```
   docker compose run --rm web python scripts/optimize_images.py
   ```
3. Use the `<picture>` element in templates to provide WebP images with fallbacks:
   ```html
   <picture>
     <source srcset="path/to/image.webp" type="image/webp">
     <img src="path/to/image.jpg" alt="Description">
   </picture>
   ```
4. Commit your changes and push to GitHub
5. The CI/CD pipeline will automatically sync the new images to S3

## Image Optimization Script

The optimize_images.py script is located in the backend/scripts/ directory. If you need to modify this script:

1. Ensure any changes maintain the 500 KB file size limit for processed images
2. Update the error handling if adding new functionality
3. Add appropriate logging for any new features or error conditions
4. Run the script with a variety of test images to ensure it handles different formats and sizes correctly
5. Update the documentation in this file if the usage instructions change

## Code Style

We follow the PEP 8 style guide for Python code. Please ensure your code adheres to this standard.

## Running Tests

Before submitting a pull request, please run the test suite:

```
python manage.py test
```

Also, run the linter:

```
flake8 .
```

## Submitting Changes

1. Push your changes to a topic branch in your fork of the repository
2. Submit a pull request to the main repository
3. The maintainers will aim to respond to pull requests within a week

Thank you for contributing to Chris Chesley's personal website!
