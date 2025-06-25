from .settings import *
import os

# Production overrides

DEBUG = False

# Secret key from environment variable set in .env provided to container
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", SECRET_KEY)

# Allow all hosts (since we will serve via IP / Nginx)
ALLOWED_HOSTS = ["*"]

# Database: use a persistent SQLite file inside the Docker volume
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/app/db/db.sqlite3",
    }
}

# Static files will be collected to this directory at build/deploy time
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

# Security headers (basic hardening)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging to both file and console
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/app/logs/django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO",
    },
} 
