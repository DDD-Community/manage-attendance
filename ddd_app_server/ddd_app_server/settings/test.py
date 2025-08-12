from .base import *

# Disable Debug Toolbar for tests
INSTALLED_APPS = [
    app for app in INSTALLED_APPS if app != 'debug_toolbar'
]

MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE if not middleware.startswith('debug_toolbar')
]

# Ensure DEBUG is False for tests
DEBUG = False