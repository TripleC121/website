# Chris Chesley's Personal Website

This repository contains the source code for Chris Chesley's personal website, which includes a Django-based web application deployed on AWS EC2 with static files served from S3.

## Project Structure

```
.
├── .github/
│   └── workflows/
│       ├── deploy-ssm.yml
│       ├── test-lint.yml
│       └── s3-sync.yml
├── chesley_web/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── main/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── scripts/
│   ├── sync_images_to_s3.py
│   └── validate_images.py
├── static/
│   ├── css/
│   └── images/
├── templates/
├── .gitignore
├── docker-compose.prod.yml
├── docker-compose.yml
├── Dockerfile.dev
├── Dockerfile.prod
├── manage.py
├── requirements-dev.txt
└── requirements-prod.txt
```

## Setup

1. Clone the repository
2. Install dependencies:
   - For development: `pip install -r requirements-dev.txt`
   - For production: `pip install -r requirements-prod.txt`
3. Set up environment variables (see `.env.example`)
4. Run migrations: `python manage.py migrate`
5. Start the development server: `python manage.py runserver`

## Deployment

This project is deployed on AWS EC2 using Docker and served behind Nginx. Static files are stored in an S3 bucket.

See `DEPLOYMENT.md` for detailed deployment instructions.

## Contributing

Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
