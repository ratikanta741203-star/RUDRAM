# RUDRAM Production Deployment Guide

## Production Topology

- **Web Server**: Nginx (Reverse Proxy, SSL Termination, Static file cache)
- **Application Server**: Gunicorn WSGI (`gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000`)
- **Database**: MySQL 8.x
- **Containerization**: Docker & Docker Compose

---

## 1. Environment Configuration

Set in `.env`:
```env
DEBUG=False
SECRET_KEY=<generate-strong-64-character-random-key>
ALLOWED_HOSTS=rudram.yourdomain.gov.in,127.0.0.1

DB_ENGINE=django.db.backends.mysql
DB_NAME=rudram_db
DB_USER=rudram_user
DB_PASSWORD=<secure-production-password>
DB_HOST=db
DB_PORT=3306
DB_FALLBACK_SQLITE=False
```

---

## 2. Docker Deployment

```bash
docker compose up -d --build
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py migrate
```
