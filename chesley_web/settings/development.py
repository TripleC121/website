from .base import *

SECRET_KEY = env('DEV_SECRET_KEY')
DEBUG = env.bool('DEV_DEBUG', default=True)
ALLOWED_HOSTS = env.list('DEV_ALLOWED_HOSTS', default=['*'])

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable security settings for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
