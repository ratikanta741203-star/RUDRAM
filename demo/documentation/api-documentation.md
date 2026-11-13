# RUDRAM REST API Specification

## Key Endpoints
- `GET /api/health/`: System and database connectivity health check.
- `GET /api/disasters/` & `POST /api/disasters/`: Disaster lifecycle management.
- `GET /api/risk/` & `POST /api/risk/predict/`: AI XGBoost/Random Forest flood inference.
- `GET /api/weather/current/` & `GET /api/weather/forecast/`: Open-Meteo meteorological data.
- `GET /api/rainfall/`: GPM IMERG and rainfall trend data.
- `GET /api/population/exposure/`: WorldPop exposure calculations.
- `GET /api/infrastructure/` & `GET /api/infrastructure/water-bodies/`: Infrastructure & river telemetry.
- `GET /api/shelters/` & `GET /api/shelters/recommend/`: Multi-criteria shelter ranking.
- `POST /api/evacuation/route/`: OSRM safe evacuation routing.
- `GET /api/resources/` & `POST /api/resources/allocate/`: Stockpile inventory management.
- `GET /api/rescue-teams/`: Rescue taskforce staging.
- `POST /api/assistant/analyze/` & `POST /api/assistant/chat/`: AI Copilot situation synthesis.
- `POST /api/satellite/flood-detection/`: Sentinel-1 SAR flood analysis.
- `POST /api/satellite/change-detection/`: Sentinel-2 optical change detection.
- `GET /api/fire/hotspots/`: NASA FIRMS thermal hotspots.
- `GET /api/alerts/` & `POST /api/alerts/`: Geo-fenced CAP notifications.
- `GET /api/reports/export-pdf/` & `GET /api/reports/export-csv/`: ReportLab PDF & CSV exports.
