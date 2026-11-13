# RUDRAM Database Architecture (MySQL 8)

## 1. Overview & Setup

RUDRAM uses **MySQL 8.x** as its primary relational and geospatial database.

### Connection Parameters (from `.env`):
- `DB_ENGINE`: `django.db.backends.mysql`
- `DB_NAME`: `rudram_db`
- `DB_USER`: `rudram_user`
- `DB_PASSWORD`: `secure-development-password`
- `DB_HOST`: `127.0.0.1` (or `db` within Docker)
- `DB_PORT`: `3306`

---

## 2. Core Relational Entities

- **UserProfile**: Extends `auth.User` with Role-Based Access (`ADMIN`, `EMERGENCY_OPERATOR`, `ANALYST`, `CITIZEN`).
- **Disaster**: Represents multi-hazard events (`FLOOD`, `WILDFIRE`, `CYCLONE`) with severity, location, and risk scores.
- **RiskZone & RiskPrediction**: Spatial flood risk zones and logged ML inferences with contributing factors.
- **Shelter**: Emergency relief facilities with live capacity tracking, medical stations, generators, and accessibility flags.
- **Resource & ResourceAllocation**: Supply stockpile inventory with audit-logged dispatch workflows.
- **RescueTeam**: Taskforce management for ODRAF, NDRF, and Fire Services.
- **Infrastructure, River, Dam, Bridge**: Physical assets and water basin telemetry.
- **Alert**: Geo-fenced CAP notifications.
- **DataSourceStatus & AuditLog**: System integrity monitoring and operator audit trail.

---

## 3. Database Management Commands

```bash
# Apply migrations
python manage.py migrate

# Seed calibrated Bhubaneswar baseline demo data
python manage.py seed_demo

# Create superuser
python manage.py createsuperuser
```
