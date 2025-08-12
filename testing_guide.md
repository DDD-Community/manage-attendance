### How to Test This Django Project

This project uses Django's built-in testing framework, which is based on Python's `unittest` module. Tests are organized within each Django app in `tests.py` files.

#### 1. Prerequisites

Before running tests, ensure you have:
*   **Python Environment:** A Python environment (preferably a virtual environment) with all project dependencies installed.
*   **Project Dependencies:** All packages listed in `requirements.txt` installed. You can install them using `pip install -r requirements.txt` after activating your virtual environment.
*   **Virtual Environment Activated:** Always activate your project's virtual environment before running any Django commands.

#### 2. Understanding the Test Setup

This project has a specific test setup to handle the Django Debug Toolbar and ensure proper test discovery:

*   **Dedicated Test Settings:** There's a special settings file at `ddd_app_server/ddd_app_server/settings/test.py`. This file is configured to:
    *   Disable the Django Debug Toolbar (`debug_toolbar`) during tests, which prevents `NoReverseMatch` and `TypeError` issues.
    *   Set `DEBUG = False`, which is standard for testing environments.
*   **`manage.py` Modification:** The project's `manage.py` script is modified to automatically use `ddd_app_server.settings.test` when the `test` command is executed. This means you don't need to manually set `DJANGO_SETTINGS_MODULE` for every test run.
*   **App Registration:** All custom Django apps (like `accounts`, `profiles`, `qrcodes`, `schedules`, `attendances`, `invites`, and `common`) must be listed in `INSTALLED_APPS` in `base.py` for their tests to be discovered.
*   **Python Packages (`__init__.py`):** Each app directory (e.g., `ddd_app_server/common/`) must contain an empty `__init__.py` file to be recognized as a Python package. Without it, test discovery will fail.

#### 3. Running Tests

You can run tests for the entire project, for a specific app, or even for a specific test case or method.

**a. Running All Tests in the Project:**

To run all tests across all installed Django apps in your project, use the following command:

```bash
source venv/bin/activate # Activate your virtual environment
python3 ddd_app_server/manage.py test
```

**b. Running Tests for a Specific App:**

To run tests only for a particular Django app (e.g., `qrcodes`), specify the app name:

```bash
source venv/bin/activate # Activate your virtual environment
python3 ddd_app_server/manage.py test qrcodes
```

You can replace `qrcodes` with any other app name like `profiles`, `invites`, `attendances`, `schedules`, `accounts`, or `common`.

**c. Running a Specific Test Case or Method:**

You can target a specific test class or even a single test method within a `tests.py` file.

*   **Specific Test Class:**
    ```bash
    source venv/bin/activate
    python3 ddd_app_server/manage.py test qrcodes.tests.QRLogModelTest
    ```
    (This would run all tests within the `QRLogModelTest` class in `qrcodes/tests.py`)

*   **Specific Test Method:**
    ```bash
    source venv/bin/activate
    python3 ddd_app_server/manage.py test qrcodes.tests.QRLogModelTest.test_qr_log_creation
    ```
    (This would run only the `test_qr_log_creation` method within `QRLogModelTest`)

#### 4. Interpreting Test Results

After running tests, you'll see output indicating the number of tests run, the time taken, and a summary of results:

*   **`OK`**: All tests passed successfully.
*   **`FAIL`**: One or more tests failed due to an assertion error (e.g., `assertEqual` returned `False` when `True` was expected). The traceback will show where the failure occurred.
*   **`ERROR`**: An unexpected exception occurred during a test. This usually indicates a problem in the test code itself or the setup, rather than a logical failure of the code being tested. The traceback will provide details.
*   **`SKIP`**: Tests that were explicitly skipped (e.g., using `@unittest.skip` decorator).

#### 5. Troubleshooting Common Test Issues

*   **`ModuleNotFoundError: No module named 'django'`**:
    *   **Cause:** Virtual environment not activated or Django not installed in the active environment.
    *   **Solution:** Run `source venv/bin/activate` and `pip install -r requirements.txt`.
*   **`SystemCheckError: The Django Debug Toolbar can't be used with tests`**:
    *   **Cause:** `debug_toolbar` is still active during test runs.
    *   **Solution:** Ensure `ddd_app_server/ddd_app_server/settings/test.py` correctly excludes `debug_toolbar` and that `manage.py` is using this settings file for tests.
*   **`TypeError: expected str, bytes or os.PathLike object, not NoneType` (related to `unittest/loader.py`)**:
    *   **Cause:** A directory is not recognized as a Python package.
    *   **Solution:** Ensure an empty `__init__.py` file exists in the problematic app's directory (e.g., `ddd_app_server/common/__init__.py`).
*   **`NoReverseMatch`**:
    *   **Cause:** A URL pattern name is incorrect or missing in `urls.py`, or a template is trying to reverse a non-existent URL.
    *   **Solution:** Verify URL names in `urls.py` and template tags (e.g., `{% url 'my_url_name' %}`).
*   **`IntegrityError: UNIQUE constraint failed`**:
    *   **Cause:** Often due to Django signals automatically creating related objects (e.g., a `Profile` being created when a `User` is saved).
    *   **Solution:** Adjust your test setup to account for these signals. Instead of manually creating the related object, check if it was created automatically after the primary object is saved.

By following these steps and understanding the project's specific test setup, you should be well-equipped to test this Django project effectively.
