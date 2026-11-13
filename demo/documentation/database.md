# RUDRAM Database Documentation (MySQL 8)

## 1. Database Configuration
- Engine: `django.db.backends.mysql`
- Name: `rudram_db`
- User: `rudram_user`
- Port: `3306`

## 2. Model Entities & Relationships
- **User & UserProfile**: RBAC with ADMIN, EMERGENCY_OPERATOR, ANALYST, CITIZEN roles.
- **Disaster & DisasterTimeline**: Event registry, severity, impacted zones, and action log.
- **RiskZone & RiskPrediction**: ML inferred risk zones with explainable factor contributions.
- **Shelter**: Emergency camps with capacity, occupancy, and medical readiness.
- **Resource, ResourceAllocation, RescueTeam**: Supply stockpile and battalion deployments.
- **Infrastructure, Road, Bridge, River, Dam, Canal, Hospital, PoliceStation, FireStation, School, CriticalInfrastructure**: Physical assets and water basin telemetry.
- **EvacuationRoute**: Safe routes with multi-route Safety Score ranking.
- **SatelliteAnalysis & DamageZone**: Sentinel-1 SAR and Sentinel-2 change detection results.
- **Alert & Notification**: Geo-fenced CAP notifications and broadcasts.
- **AuditLog & DataSourceStatus**: Operational audit log and data freshness indicators.
