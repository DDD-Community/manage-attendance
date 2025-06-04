import multiprocessing
import os

# Default bind address can be overridden via environment variable
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")

# Calculate workers based on CPU count if not provided
workers = int(os.getenv("GUNICORN_WORKERS", (multiprocessing.cpu_count() * 2) + 1))

# Use gevent worker class for async processing by default
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gevent")
worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", 512))

# Limit requests and set timeout values
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1024))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 180))

# Logging
log_level = os.getenv("GUNICORN_LOG_LEVEL", "info")

# WSGI application path
wsgi_app = os.getenv("GUNICORN_WSGI_APP", "ddd_app_server.wsgi:application")
