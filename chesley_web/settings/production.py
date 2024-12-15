import logging
import logging.config
import os
import sys

from .base import *

# Version tracking
VERSION = "0.2.4"

# Environment setup
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env.prod"))

# Core Django Settings
SECRET_KEY = env("PROD_SECRET_KEY")
DEBUG = env.bool("PROD_DEBUG", default=False)

# setting allowed hosts
ALLOWED_HOSTS = [
    "cchesley.com",
    "www.cchesley.com",
    "35.153.202.209",
    "ec2-35-153-202-209.compute-1.amazonaws.com",
]

# R2 settings
R2_ACCESS_KEY_ID = env("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = env("R2_SECRET_ACCESS_KEY")
R2_STORAGE_BUCKET_NAME = env("R2_STORAGE_BUCKET_NAME")
CLOUDFLARE_ACCOUNT_ID = env("CLOUDFLARE_ACCOUNT_ID")
R2_ENDPOINT_URL = (
    f"https://{CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com"  # noqa: E231
)

# AWS/R2 settings
AWS_S3_ACCESS_KEY_ID = R2_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = R2_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = R2_STORAGE_BUCKET_NAME
AWS_S3_ENDPOINT_URL = R2_ENDPOINT_URL
AWS_S3_REGION_NAME = "auto"
AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = True
AWS_IS_GZIPPED = True
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

# Custom domain configuration
AWS_S3_CUSTOM_DOMAIN = "static.cchesley.com"
AWS_S3_URL_PROTOCOL = "https:"

# Static files configuration
STATICFILES_STORAGE = "storages.backends.s3boto3.S3ManifestStaticStorage"
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"  # noqa: E231
STATIC_ROOT = env("STATIC_ROOT", default=os.path.join(BASE_DIR, "staticfiles"))

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Database Configuration
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

# Security Settings
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
SECURE_BROWSER_XSS_FILTER = env.bool("SECURE_BROWSER_XSS_FILTER", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF", default=True)
X_FRAME_OPTIONS = env("X_FRAME_OPTIONS", default="DENY")
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cloudflare Settings
CSRF_TRUSTED_ORIGINS = ["https://cchesley.com", "https://www.cchesley.com"]

# Email Configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
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
        "": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "environ.environ": {
            "handlers": ["console", "file"],
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
