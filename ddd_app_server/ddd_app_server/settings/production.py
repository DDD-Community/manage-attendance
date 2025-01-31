from .base import *

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000/",
]

DATABASES = {
    'default': {
        'ENGINE': os.getenv("DJANGO_DB_ENGINE", "django.db.backends.sqlite3"),
        'NAME': os.getenv("DJANGO_DB_NAME", BASE_DIR / "db.sqlite3"),
        'USER': os.getenv("DJANGO_DB_USER", ""),
        'PASSWORD': os.getenv("DJANGO_DB_PASSWORD", ""),
        'HOST': os.getenv("DJANGO_DB_HOST", "localhost"),
        'PORT': os.getenv("DJANGO_DB_PORT", "5432"),
    }
}