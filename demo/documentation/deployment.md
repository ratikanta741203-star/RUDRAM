# RUDRAM Deployment & Docker Guide

## Docker Setup
```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo
docker compose exec web python manage.py createsuperuser
```

## Local Development
```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```
