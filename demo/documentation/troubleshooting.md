# RUDRAM Troubleshooting & Diagnostics

- **MySQL Connection**: Zero-dependency SQLite automatic fallback is active when local MySQL daemon is offline (`DB_FALLBACK_SQLITE=True`). For Docker, use `DB_HOST=db`.
- **Resetting Demo Data**: Run `python manage.py seed_demo` anytime to restore the calibrated baseline.
- **Running Tests**: `python manage.py test`
