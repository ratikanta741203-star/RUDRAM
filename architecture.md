# RUDRAM Architecture Specification

## Architectural Overview

RUDRAM uses a modular, layered service-oriented architecture designed for high availability, sub-second GIS queries, and deterministic fallback resilience.

```
                    ┌──────────────────────────────────────────────┐
                    │               Web Browser Client             │
                    │  (Bootstrap 5, Leaflet.js, Chart.js, Lucide) │
                    └──────────────────────┬───────────────────────┘
                                           │ HTTP / REST / JSON
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │            Django 5 Application Core         │
                    │      (Django REST Framework, URL Routing)    │
                    └──────┬───────────────┬───────────────┬───────┘
                           │               │               │
            ┌──────────────▼─────┐  ┌──────▼──────┐  ┌─────▼───────────────┐
            │   ML & AI Engine   │  │ GIS Engine  │  │   Service Layer     │
            │  - XGBoost         │  │ - Leaflet   │  │  - Open-Meteo       │
            │  - Random Forest   │  │ - Shapely   │  │  - NASA POWER / GPM │
            │  - SHAP Breakdown  │  │ - GeoPandas │  │  - OSM Overpass     │
            │  - U-Net Interface │  │ - OSRM      │  │  - Sentinel-1 SAR   │
            └──────────────┬─────┘  └──────┬──────┘  └─────┬───────────────┘
                           │               │               │
                           └───────────────┼───────────────┘
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │             MySQL 8.x Database               │
                    │   (Disasters, Risk, Shelters, Telemetry)     │
                    └──────────────────────────────────────────────┘
```

## Core Subsystems

### 1. Presentation Layer
- **HTML5 & Vanilla CSS**: Custom command-center dark theme with high-contrast emergency status indicators.
- **Leaflet.js**: Vector GIS mapping engine rendering 21 distinct spatial layers.
- **Chart.js**: Real-time hydrological, meteorological, and demographic visualization.

### 2. Django REST API & Controller Layer
- Implements granular role-based access control (`ADMIN`, `EMERGENCY_OPERATOR`, `ANALYST`, `CITIZEN`).
- Exposes structured REST endpoints with validation, serialization, and error trapping.

### 3. Service Adapters & Fallback Architecture
External service calls never crash the application. Each adapter employs a try-catch circuit breaker:
- **Connected (Live)**: Calls public live APIs.
- **Simulation (Demo Mode)**: Returns realistic, physically calibrated baseline data when external credentials are unconfigured.

### 4. GIS & Hydrological Spatial Engine
- Implements Haversine proximity calculations, bounding box intersections, terrain slope penalties, and multi-criteria shelter matching.
