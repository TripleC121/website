# Personal Website Project

## Overview
Personal Django-based website hosted on AWS, featuring a blog system and portfolio sections. Built with modern DevOps practices and security in mind.

## Tech Stack
- **Backend:** Django 5.0.7, Python 3.11
- **Server:** Nginx, Gunicorn
- **Database:** PostgreSQL (RDS)
- **Infrastructure:** AWS EC2, Cloudflare R2
- **CI/CD:** GitHub Actions
- **Containerization:** Docker

## Getting Started

### Development Setup
1. Clone the repository:
```bash
git clone [repository-url]
cd website
```

2. Create a `.env.dev` file with required environment variables (see `.env.prod-redacted` for template)

3. Build and start the development container:
```bash
docker compose up --build
```

The application will be available at http://localhost:8000

### Development Commands
Common commands through Docker:
```bash
# Run migrations
docker compose exec web python manage.py migrate

# Create a superuser
docker compose exec web python manage.py createsuperuser

# Run tests
docker compose exec web python manage.py test

# View logs
docker compose logs -f
```

## Project Structure
```
.
├── backend/          # Backend utilities and scripts
├── chesley_web/      # Django project settings
├── main/            # Main Django application
├── static/          # Static files
├── templates/       # HTML templates
└── workout_tracker/ # Future workout tracking app
```

## Code Quality
This project uses several tools to maintain code quality:
- Black for code formatting
- Flake8 for linting
- isort for import sorting
- Pre-commit hooks for automated checks

To set up pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation
For detailed documentation about deployment, configuration, and maintenance, see:
- [Full Documentation](docs/README.md)
- [Deployment Guide](deployment.md)
- [Contributing Guide](contributing.md)
