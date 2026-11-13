# RUDRAM REST API Documentation

Base URL: `http://localhost:8000/api/`

---

## 1. System Health & Telemetry

### `GET /api/health/`
Checks application, database, and third-party service connectivity.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "application": "RUDRAM",
  "version": "1.0.0-hackathon-release",
  "database": "connected",
  "demo_mode": true,
  "external_services": {
    "open_meteo": {"status": "CONNECTED", "is_live": true},
    "nasa_power": {"status": "CONNECTED", "is_live": true},
    "google_earth_engine": {"status": "DEMO", "is_live": false}
  }
}
```

---

## 2. AI Risk Prediction

### `POST /api/risk/predict/`
Calculates flood risk score and explainable feature contributions using XGBoost & Random Forest.

**Request Body:**
```json
{
  "location_name": "Bhubaneswar Rasulgarh Riverine Basin",
  "latitude": 20.2961,
  "longitude": 85.8245,
  "rainfall_current_mm": 24.5,
  "rainfall_24h_mm": 186.4,
  "rainfall_7d_mm": 380.0,
  "rainfall_forecast_24h_mm": 95.0,
  "elevation_m": 14.0,
  "distance_to_water_km": 0.8,
  "river_water_level_m": 14.35,
  "soil_moisture_index": 0.91
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "prediction": {
    "risk_score": 84.5,
    "risk_level": "CRITICAL",
    "model_mode": "XGBOOST_ENSEMBLE",
    "recommended_action": "Immediate evacuation of vulnerable riverine settlements."
  },
  "explanation": {
    "contributing_factors": [
      {
        "factor": "24-Hour Rainfall Volume",
        "value": "186.4 mm",
        "contribution": "HIGH"
      }
    ]
  }
}
```

---

## 3. Evacuation Routing

### `POST /api/evacuation/route/`
Computes safety-optimized evacuation corridors comparing flood-penalized routes.

**Request Body:**
```json
{
  "start_lat": 20.2961,
  "start_lon": 85.8245,
  "end_lat": 20.2545,
  "end_lon": 85.8390
}
```

---

## 4. Shelters Recommendation

### `GET /api/shelters/recommend/?lat=20.2961&lon=85.8245`
Returns ranked shelters using multi-criteria spatial suitability scoring.

---

## 5. AI Emergency Assistant

### `POST /api/assistant/chat/`
```json
{
  "message": "Which high-ground shelters have medical support?"
}
```

---

## 6. Satellite Analysis Lab

### `POST /api/satellite/flood-detection/`
Executes Sentinel-1 SAR backscatter thresholding workflow.
