import environ

from .base import *

# Initialize environ
env = environ.Env()

# Read .env.dev file
environ.Env.read_env(os.path.join(BASE_DIR, ".env.dev"))

# Apply environment variables
SECRET_KEY = env("DEV_SECRET_KEY")
DEBUG = env.bool("DEV_DEBUG", default=True)
ALLOWED_HOSTS = env.list(
    "DEV_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"]
)

# Database
DATABASES = {
    "default": {
        "ENGINE": env("DEV_DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env("DEV_DB_NAME", default=str(BASE_DIR / "db.sqlite3")),
    }
}

# Disable security settings for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Debug print statements
print(f"Secret Key: {SECRET_KEY}")
print(f"Debug: {DEBUG}")
print(f"Allowed Hosts: {ALLOWED_HOSTS}")
print(f"Database: {DATABASES}")
