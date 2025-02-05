from .base import *

CORS_ALLOWED_ORIGINS = [
    "https://*.ufxpri.dev:8000/",
]

ALLOWED_HOSTS += [
    "localhost",
    "*.ufxpri.dev",
    "home.ufxpri.dev",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv("DJANGO_DB_ENGINE", "django.db.backends.sqlite3"),
#         'NAME': os.getenv("DJANGO_DB_NAME", BASE_DIR / "db.sqlite3"),
#         'USER': os.getenv("DJANGO_DB_USER", ""),
#         'PASSWORD': os.getenv("DJANGO_DB_PASSWORD", ""),
#         'HOST': os.getenv("DJANGO_DB_HOST", "localhost"),
#         'PORT': os.getenv("DJANGO_DB_PORT", "5432"),
#     }
# }