from .base import *
import sys

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"PROD_ALLOWED_HOSTS from env: {os.environ.get('PROD_ALLOWED_HOSTS')}")
print(f"Sys path: {sys.path}")


SECRET_KEY = env('PROD_SECRET_KEY')
DEBUG = env.bool('PROD_DEBUG', default=False)
ALLOWED_HOSTS = env.list('PROD_ALLOWED_HOSTS') + ['localhost']

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env('PROD_DB_NAME'),
        "USER": env('PROD_DB_USER'),
        "PASSWORD": env('PROD_DB_PASSWORD'),
        "HOST": env('PROD_DB_HOST'),
        "PORT": env('PROD_DB_PORT', default='5432'),
	'OPTIONS': {
            'sslmode': 'verify-full',
            'sslrootcert': env('DB_SSLROOTCERT'),
	}
    }
}

# logging
print(f"Database settings: {DATABASES}")
logger.debug(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")

# Security settings
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
SECURE_BROWSER_XSS_FILTER = env.bool('SECURE_BROWSER_XSS_FILTER', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool('SECURE_CONTENT_TYPE_NOSNIFF', default=True)
X_FRAME_OPTIONS = env('X_FRAME_OPTIONS', default='DENY')
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)

# Static files
STATIC_ROOT = env('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',  # Changed from ERROR to DEBUG
            'class': 'logging.FileHandler',
            'filename': env('DJANGO_ERROR_LOG', default='/var/log/chesley_web/django/errors.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',  # Changed from ERROR to DEBUG
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'chesley_web': {  # Add this logger for your application
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}