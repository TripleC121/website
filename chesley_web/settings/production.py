import logging
import logging.config
import sys

from .base import *

# version 0.2.3

# Set Django's default logging level to WARNING
logging.getLogger("environ.environ").setLevel(logging.WARNING)
logging.getLogger("django.environ").setLevel(logging.WARNING)

# Updated logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,  # Changed from False to True
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": env(
                "DJANGO_LOG_FILE", default="/var/log/chesley_web/django/django.log"
            ),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console"],
            "level": "WARNING",
        },
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "environ": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.environ": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "chesley_web": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# Core Django Settings
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env.prod"))

SECRET_KEY = env("PROD_SECRET_KEY")
DEBUG = env.bool("PROD_DEBUG", default=False)
ALLOWED_HOSTS = env.list("PROD_ALLOWED_HOSTS")

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env.prod"))

SECRET_KEY = env("PROD_SECRET_KEY")
DEBUG = env.bool("PROD_DEBUG", default=False)
ALLOWED_HOSTS = env.list("PROD_ALLOWED_HOSTS")

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("PROD_DB_NAME"),
        "USER": env("PROD_DB_USER"),
        "PASSWORD": env("PROD_DB_PASSWORD"),
        "HOST": env("PROD_DB_HOST"),
        "PORT": env("PROD_DB_PORT", default="5432"),
        "OPTIONS": {
            "sslmode": "verify-full",
            "sslrootcert": env("DB_SSLROOTCERT"),
        },
    }
}

# Static Files and S3 Configuration
STATIC_ROOT = env("STATIC_ROOT", default=os.path.join(BASE_DIR, "staticfiles"))
STATIC_URL = "/static/"

# S3 Configuration (using env instead of os.environ for consistency)
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_LOCATION = "static"

# Storage Configuration
# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
DEFAULT_FILE_STORAGE = "main.storage.S3ImageStorage"

# Security settings
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
SECURE_BROWSER_XSS_FILTER = env.bool("SECURE_BROWSER_XSS_FILTER", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF", default=True)
X_FRAME_OPTIONS = env("X_FRAME_OPTIONS", default="DENY")
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)

# cloudflare settings
CSRF_TRUSTED_ORIGINS = ["https://cchesley.com", "https://www.cchesley.com"]

# password reset
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
