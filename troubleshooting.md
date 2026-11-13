# RUDRAM Troubleshooting & Diagnostics Guide

## 1. Database Connectivity

### Problem: MySQL connection fails during local development
**Solution**:
RUDRAM includes an automatic SQLite fallback when running locally without a running MySQL daemon (`DB_FALLBACK_SQLITE=True`). For Docker or Production, ensure MySQL 8 is running and verify connection credentials in `.env`.

---

## 2. Port Conflicts

### Problem: Port 8000 or 3306 is already in use
**Solution**:
Run the server on an alternate port:
```bash
python manage.py runserver 127.0.0.1:8080
```

---

## 3. Resetting Demo State

If you wish to restore the pristine Bhubaneswar demo state:
```bash
python manage.py seed_demo
```
This command is completely idempotent and safe to run repeatedly.
