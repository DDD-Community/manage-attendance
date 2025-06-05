import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    '2001:4860:7:50e::f',
    '106.242.190.114',
    '192.168.0.13'
]
def show_toolbar(request):
    return True
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    'INSERT_BEFORE': '</head>',
    'HIDE_DJANGO_SQL': True,
    'HIDE_TEMPLATE_CONTEXT': True,
}

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
# REST Framework settings for development
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
            'level': 'DEBUG',
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
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django_general.log',
            'formatter': 'verbose',
        },
        'file_access': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django_access.log',
            'formatter': 'verbose',
        },
        'file_errors_detail': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django_errors_detail.log',
            'formatter': 'verbose',
        }
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
        'standardized_error': {
            'handlers': ['console', 'file_errors_detail'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'common.request_logging': {
            'handlers': ['console', 'file_access'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {  # Root logger
            'handlers': ['console', 'file_general', 'file_errors'],
            'level': 'INFO',
        },
    },
}
