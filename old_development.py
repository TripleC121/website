from .base import *
import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.dev'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DEV_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# For development, we don't need STATIC_ROOT
# Django's runserver will serve static files from STATICFILES_DIRS
STATIC_ROOT = BASE_DIR / 'staticfiles_dev'

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# password reset
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
