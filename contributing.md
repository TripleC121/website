# Contributing Guide

## Development Workflow

### 1. Setting Up Development Environment
- Follow Docker setup instructions in README.md
- Install pre-commit hooks locally for code quality checks
- Development environment uses chesley_web.settings.development

### 2. Code Quality Standards
This project follows these standards:
- PEP 8 style guide
- Black code formatting
- Sorted imports using isort
- Maximum line length of 88 characters (Black default)

### 3. Pre-commit Hooks
The following checks run automatically before commits:
```yaml
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- check-added-large-files
- black
- flake8
- isort
```

### 4. Git Workflow
1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes

3. Run tests in Docker:
```bash
docker compose exec web python manage.py test
```

4. Commit your changes:
```bash
git add .
git commit -m "feat: your descriptive commit message"
```

5. Push to your branch:
```bash
git push origin feature/your-feature-name
```

### 5. Development Best Practices
- Use Docker for all development work
- Keep containers ephemeral
- Use docker compose for service orchestration
- Regularly rebuild images to test Dockerfile changes

### 6. Image Guidelines
- Place new images in static/images/
- Images must be under 500KB
- Use WebP format when possible
- Original images are preserved in a separate directory

### 7. Template Guidelines
- Extend base.html for new templates
- Use Django template inheritance
- Include meta descriptions for SEO
- Follow the established directory structure

### 8. Security Considerations
- Never commit sensitive information
- Use environment variables for secrets
- Follow the principle of least privilege
- Keep dependencies updated

### 9. Documentation
- Update documentation for significant changes
- Document new environment variables
- Update deployment notes if necessary
- Add comments for complex logic

## Testing
```bash
docker compose exec web python manage.py test
```

## Versioning
This project uses semantic versioning:
- MAJOR.MINOR.PATCH
- Current version: 0.2.4
