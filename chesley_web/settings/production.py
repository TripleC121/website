from .base import * # version 0.0.1
import sys
import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.prod'))

SECRET_KEY = env('PROD_SECRET_KEY')
DEBUG = env.bool('PROD_DEBUG', default=False)
ALLOWED_HOSTS = env.list('PROD_ALLOWED_HOSTS')

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
# print(f"Database settings: {DATABASES}")
# logger.debug(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")

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

# password reset
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
