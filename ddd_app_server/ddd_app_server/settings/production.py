import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
ALLOWED_HOSTS += [
    'localhost',
    '*.ufxpri.dev',
    'home.ufxpri.dev',
]

CSRF_TRUSTED_ORIGINS = [
    'https://ufxpri.dev',
    'https://*.ufxpri.dev',
    'https://home.ufxpri.dev',
]
# Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('POSTGRES_DB'),
#         'USER': os.getenv('POSTGRES_USER'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
#         'HOST': os.getenv('POSTGRES_HOST'),
#         'PORT': os.getenv('POSTGRES_PORT', '5432'),
#         'CONN_MAX_AGE': 60,
#         'OPTIONS': {
#             'sslmode': 'require',
#         },
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Security settings
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = 'DENY'
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# REST Framework settings for production
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)

# CORS settings for production
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django_errors.log',
            'formatter': 'verbose',
        },
        'file_general': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django_general.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_errors'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file_errors'],
            'level': 'ERROR',
            'propagate': False,
        },
        '': {  # Root logger
            'handlers': ['console', 'file_general', 'file_errors'],
            'level': 'INFO',
        },
    },
}

# # Cache settings
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# # Session settings
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'default'
# SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week