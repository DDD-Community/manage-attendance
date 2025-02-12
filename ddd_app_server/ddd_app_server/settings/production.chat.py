"""
Production settings for mysite project.
"""

import os
from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "*.ufxpri.dev",
    "home.ufxpri.dev",
]

CSRF_TRUSTED_ORIGINS = [
    "ufxpri.dev",
    "*.ufxpri.dev",
    "home.ufxpri.dev",
    "https://home.ufxpri.dev/",
]

# Database Configuration (PostgreSQL Example)
DATABASES = {
    'default': {
        'ENGINE': os.getenv("DJANGO_DB_ENGINE", "django.db.backends.postgresql"),
        'NAME': os.getenv("DJANGO_DB_NAME"),
        'USER': os.getenv("DJANGO_DB_USER"),
        'PASSWORD': os.getenv("DJANGO_DB_PASSWORD"),
        'HOST': os.getenv("DJANGO_DB_HOST", "localhost"),
        'PORT': os.getenv("DJANGO_DB_PORT", "5432"),
    }
}

# Security Settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

X_FRAME_OPTIONS = "DENY"

# CORS Headers
CORS_ALLOWED_ORIGINS = [
    "https://*.ufxpri.dev",
]

# Static & Media Files (Production)
STATIC_ROOT = "/var/www/mysite/static"
MEDIA_ROOT = "/var/www/mysite/media"

# Logging (Example)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "/var/log/django/error.log",
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "ERROR",
    },
}

# Ensure `production.py` is not loaded in local development
if DEBUG:
    raise ValueError("Production settings loaded while DEBUG is True!")
