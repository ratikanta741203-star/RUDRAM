# RUDRAM AI Flood & Cyclone Risk ML Architecture (v2.0)

## 1. Machine Learning Methodology & Dual Engine

RUDRAM predicts multi-hazard disaster risk index (0–100%) and emergency categories using a dual XGBoost + Random Forest ensemble engine:
1. **Flood Risk Estimator**: **XGBoost Classifier + Random Forest Classifier Ensemble** (v2)
2. **Tropical Cyclone Risk Predictor**: **Dedicated XGBoost Regressor** (v2)

---

## 2. Historical Dataset Architecture & Versioning

All original training data and baseline models are strictly preserved (`v1`). Expanded historical datasets (`v2`) incorporate 20+ years of historical observations across 30 Odisha districts and broader Indian coastal regions:

- **Flood Datasets**:
  - `ml/data/processed/odisha_flood_training_dataset.csv` (Preserved v1: 219,150 records)
  - `ml/data/processed/odisha_flood_training_dataset_v2.csv` (Enhanced v2: 6,000 records)
  - `ml/data/processed/combined_flood_training_dataset.csv` (Combined: 225,150 records)
- **Cyclone Datasets**:
  - `ml/data/raw/cyclones/odisha_cyclone_historical_events.csv` (Raw event registry: 1999 Odisha Super Cyclone, Phailin 2013, Hudhud 2014, Titli 2018, Fani 2019, Amphan 2020, Yaas 2021, Gulab 2021, Asani 2022, Sitrang 2022, Biparjoy 2023, Midhili 2023, Remal 2024, Dana 2024)
  - `ml/data/processed/cyclone_training_dataset_v2.csv` (Processed v2: 5,000 records)

---

## 3. Feature Engineering Vector Matrix

### A. Flood Risk Features (14 Core Parameters + Rolling Windows):
1. `rainfall_current_mm`: Immediate precipitation intensity (mm/hr)
2. `rainfall_24h_mm`: Cumulative 24-hour rainfall accumulation (mm)
3. `rainfall_7d_mm`: 7-day antecedent catchment saturation index (mm)
4. `rainfall_forecast_24h_mm`: Projected 24-hour precipitation volume (mm)
5. `temperature_c`: Ambient surface temperature (°C)
6. `humidity_pct`: Relative atmospheric humidity (%)
7. `wind_speed_kmh`: Surface wind velocity (km/h)
8. `elevation_m`: SRTM Digital Elevation Model height (m a.s.l.)
9. `slope_deg`: Topographic terrain gradient (degrees)
10. `distance_to_water_km`: Proximity to nearest river/canal (km)
11. `historical_flood_freq`: Historical inundation return period index
12. `population_density_sqkm`: WorldPop human settlement density
13. `soil_moisture_index`: Catchment saturation ratio (0.0 – 1.0)
14. `river_water_level_m`: Real-time upstream river gauge height (m)

### B. Cyclone Risk Features (13 Meteorological & Track Parameters):
1. `current_wind_speed_kmh`: 10-minute sustained surface wind speed
2. `wind_gust_kmh`: Peak wind gust velocity
3. `max_forecast_wind_kmh`: Projected 24h peak wind speed
4. `max_forecast_gust_kmh`: Projected 24h peak gust speed
5. `atmospheric_pressure_hpa`: Central barometric pressure
6. `min_forecast_pressure_hpa`: Minimum forecast central pressure
7. `current_temperature_c`: Air temperature
8. `relative_humidity_pct`: Relative humidity
9. `recent_rainfall_mm`: Recent precipitation
10. `forecast_rainfall_7d_mm`: 7-day cumulative forecast rainfall
11. `coastal_proximity_km`: Distance to coastline
12. `latitude`: Geographic latitude
13. `longitude`: Geographic longitude

---

## 4. Temporal Holdout Validation & Data Leakage Prevention

To prevent temporal leakage in time-series disaster observations, models are evaluated using chronological holdout splits:
- **Training Period**: 2005-01-01 to 2019-12-31 (168,629 samples)
- **Validation Period**: 2020-01-01 to 2022-12-31 (33,718 samples)
- **Held-Out Test Period**: 2023-01-01 to 2025-12-31 (22,803 samples)

### Validation Metrics Tracked:
- Classification (Flood): Accuracy, Precision, Recall, F1 Score, ROC-AUC, PR-AUC, Confusion Matrix, Brier Score.
- Regression (Cyclone): Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), R² Coefficient.

---

## 5. Model Registry & Active Promotion Rule

Model promotion to `ACTIVE` production status is governed by strict objective evaluation:
- Candidate models (`v2`) are trained and evaluated against held-out test data.
- A new candidate model is promoted to active production (`flood_risk_xgboost.joblib` / `cyclone_risk_xgboost.joblib`) **ONLY IF** it achieves a higher test F1 / ROC-AUC / Recall than the active baseline.
- Model registry status is tracked in `ml/models/model_registry.json` and `ml_training_report.json`.

---

## 6. Management Retraining Commands

Run full ML pipeline retraining from terminal:
```bash
# Retrain Flood Models
python manage.py train_flood_model

# Retrain Cyclone Models
python manage.py train_cyclone_model

# Retrain All Disaster Models & Generate Registry Reports
python manage.py train_all_models
```
