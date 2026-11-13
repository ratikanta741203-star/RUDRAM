# RUDRAM Full System Architecture

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
                    │             MySQL 8.0 Database               │
                    │   (Disasters, Risk, Shelters, Telemetry)     │
                    └──────────────────────────────────────────────┘
```

## System Subsystems
1. **Frontend**: Bootstrap 5, Leaflet.js, Chart.js, Lucide Icons, responsive Dark Command Center UI.
2. **Backend**: Django 5.x, DRF REST APIs, RBAC authentication.
3. **ML Engine**: XGBoost & Random Forest flood risk regressors with SHAP factor contributions.
4. **GIS Layer**: GeoPandas, Shapely, Rasterio, OSRM routing, Overpass infrastructure.
5. **Remote Sensing**: Sentinel-1 SAR, Sentinel-2 Optical, PyTorch U-Net interface.
