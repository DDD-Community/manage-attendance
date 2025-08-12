# Project Overview: Django DDD Application (Specialized Context)

This project is a Django-based application with specific configurations and patterns.

## Unique Project Structure & Conventions:
- **Modular Apps:** Beyond standard Django apps, note the `common` app for shared utilities.
- **Authentication:** Uses `dj_rest_auth`, `rest_framework_simplejwt`, and `django-allauth` for JWT, session, and social (Google/Apple) authentication.
- **Configuration:** Settings are split into `base.py`, `local.py`, `production.py`, and a dedicated `test.py`.
- **Logging:** Custom logging to `ddd_app_server/logs/`.
- **Deployment:** Docker, Nginx, Gunicorn setup.

## Special "Know-How" for this Project:

### 1. Testing Environment Setup:
- **`debug_toolbar` Disablement:** The `debug_toolbar` *must* be explicitly disabled for tests.
    - **Method:** A dedicated `ddd_app_server/ddd_app_server/settings/test.py` file exists, which filters out `debug_toolbar` from `INSTALLED_APPS` and `MIDDLEWARE`.
    - **Execution:** `manage.py` is modified to use `ddd_app_server.settings.test` when the `test` command is run.
- **App Registration:** Ensure all custom apps (e.g., `'common'`) are listed in `INSTALLED_APPS` for test discovery.
- **Python Packages:** Directories like `common/` *require* an `__init__.py` file to be recognized as Python packages for test discovery.
- **`JsonResponse` Content:** Access JSON content from `JsonResponse` objects in tests via `json.loads(response.content.decode('utf-8'))`.
- **Circular Dependencies:** Custom exceptions (`APIException` and its subclasses) are moved to `common/exceptions.py` to resolve circular import issues between `common/mixins.py` and `common/middleware.py`.
- **Django Signals:** Be aware of Django signals (e.g., `User` creating `Profile`) that automatically create/modify objects, as this impacts test setup (avoid manual creation if a signal handles it).

### 2. `common` App Utilities:
- **`StandardizedErrorMiddleware`:** Centralizes API error handling, converting exceptions into consistent JSON responses.
- **`RequestLoggingMiddleware`:** Logs detailed HTTP request information.
- **Custom Exceptions:** Provides structured error types for API responses.

### 3. URL Reversal:
- `account_logout` URL in `accounts/templates/account/profile.html` is mapped to `rest_logout` from `dj_rest_auth.urls`.

## General Guidelines for Interaction:
- **Adhere to Existing Conventions:** Mimic current code style and patterns.
- **Verify Dependencies:** Check `requirements.txt` or existing imports.
- **Proactive Problem Solving:** Address test setup, logging, and dependency issues.