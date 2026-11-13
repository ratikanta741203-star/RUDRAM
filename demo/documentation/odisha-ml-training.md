# RUDRAM: Odisha Statewide Historical Flood ML Training Pipeline

## 1. Executive Summary & Objective
RUDRAM is an AI-powered disaster management, flood-risk prediction, GIS monitoring, emergency response, evacuation, and satellite-analysis platform. This pipeline provides the real-data training, feature engineering, and model validation infrastructure covering all 30 districts of Odisha State, India across a 20-year continuous historical period (2005–2024).

---

## 2. Dataset Sources & Acquisition
| Data Domain | Provider / Source | Primary Variables | Coverage / Resolution | License |
| :--- | :--- | :--- | :--- | :--- |
| **Meteorology & Precipitation** | NASA POWER LARC / IMD | Daily rainfall (`PRECTOTCORR`), $2\text{m}$ temperature (`T2M`), relative humidity (`RH2M`), wind speed (`WS10M`) | Statewide Odisha (30 Districts), Daily (2005–2024) | Public Domain (NASA Open Data) |
| **Digital Elevation Model (DEM)** | NASA SRTM Global 1 Arc-Second | Elevation ($m$), slope gradient ($\text{deg}$), Topographic Wetness Index (TWI) | $30\text{m}$ Spatial Resolution | Open Topography / Public Domain |
| **Historical Flood Ground Truth** | OSDMA / Central Water Commission (CWC) / Dartmouth Flood Observatory | Verified flood dates, affected districts, river basin inundation extents, event severity | $15$ Documented Historical Flood Events (2005–2024) | Official Disaster Management Records |
| **Hydrographic Arteries** | OpenStreetMap / HydroSHEDS | Geodesic distance to nearest major river systems (Mahanadi, Brahmani, Baitarani, Subarnarekha, Rushikulya, Daya) | Vector Polyline Network | ODbL 1.0 |
| **Demographics** | Census of India / WorldPop | Population density per square kilometer ($\text{pop}/\text{km}^2$) | District / Grid Level | Official Open Census Data |

---

## 3. Spatial & Temporal Grid Structure
- **Target Region**: Entire State of Odisha, India ($17.78^\circ\text{N}$ to $22.57^\circ\text{N}$, $81.39^\circ\text{E}$ to $87.53^\circ\text{E}$).
- **Districts Covered ($30$)**: Angul, Balangir, Balasore, Bargarh, Bhadrak, Boudh, Cuttack, Deogarh, Dhenkanal, Gajapati, Ganjam, Jagatsinghpur, Jajpur, Jharsuguda, Kalahandi, Kandhamal, Kendrapara, Kendujhar, Khordha, Koraput, Malkangiri, Mayurbhanj, Nabarangpur, Nayagarh, Nuapada, Puri, Rayagada, Sambalpur, Subarnapur, Sundargarh.
- **Temporal Period**: 2005-01-01 to 2024-12-31 ($20$ Years = $7,305$ Days $\times 30$ Districts = $219,150$ total sample observations).

---

## 4. 14-Feature Input Vector
The machine learning pipeline consumes a structured 14-feature vector:
1. `rainfall_current_mm`: Estimated instantaneous hourly precipitation ($mm/h$).
2. `rainfall_24h_mm`: 24-hour accumulated rainfall ($mm$).
3. `rainfall_7d_mm`: 7-day rolling antecedent rainfall ($mm$).
4. `rainfall_forecast_24h_mm`: 24-hour forward forecast precipitation ($mm$).
5. `temperature_c`: Ambient surface temperature ($^\circ\text{C}$).
6. `humidity_pct`: Relative atmospheric humidity ($\%$).
7. `wind_speed_kmh`: 10-meter surface wind speed ($km/h$).
8. `elevation_m`: Terrain elevation above mean sea level ($m$).
9. `slope_deg`: Topographic slope gradient ($\text{degrees}$).
10. `distance_to_water_km`: Geodesic distance to nearest major river/canal ($km$).
11. `historical_flood_freq`: Expanding historical flood recurrence frequency (prior-only, preventing target leakage).
12. `population_density_sqkm`: Human population exposure density ($\text{people}/\text{km}^2$).
13. `soil_moisture_index`: Catchment soil moisture saturation fraction ($0.0 - 1.0$).
14. `river_water_level_m`: River gauge stage reading relative to danger level ($m$).

---

## 5. Leakage-Free Train / Validation / Test Splitting
To prevent temporal and spatial autocorrelation leakage:
- **Training Split**: $2005-01-01$ to $2019-12-31$ ($15$ years, $164,370$ samples).
- **Validation Split**: $2020-01-01$ to $2022-12-31$ ($3$ years, $32,880$ samples).
- **Out-of-Sample Test Split**: $2023-01-01$ to $2024-12-31$ ($2$ years, $21,900$ samples).

---

## 6. Model Architecture & Ensemble Formulation
1. **XGBoost Classifier** (`xgb.XGBClassifier`):
   - Tuned parameters: `n_estimators=100`, `max_depth=5`, `learning_rate=0.06`, `scale_pos_weight` calibrated to positive class ratio.
2. **Random Forest Classifier** (`RandomForestClassifier`):
   - Tuned parameters: `n_estimators=80`, `max_depth=7`, `class_weight='balanced_subsample'`.
3. **Probability Blend Ensemble**:
   $$P(\text{Flood}) = 0.65 \times P_{\text{XGBoost}} + 0.35 \times P_{\text{RandomForest}}$$
   $$\text{Risk Score} = \text{clip}(P(\text{Flood}) \times 100, 0, 100)$$

---

## 7. Execution Commands

### Local Workflow:
```bash
# 1. Download and compile raw historical datasets
python manage.py download_flood_data

# 2. Validate data quality and generate quality report
python manage.py validate_flood_data

# 3. Build engineered Parquet and CSV training datasets
python manage.py build_flood_dataset

# 4. Train real XGBoost and Random Forest models
python manage.py train_flood_model

# 5. Evaluate models on test set and write reports
python manage.py evaluate_flood_model
```

### Docker Execution:
```bash
docker compose exec backend python manage.py download_flood_data
docker compose exec backend python manage.py validate_flood_data
docker compose exec backend python manage.py build_flood_dataset
docker compose exec backend python manage.py train_flood_model
docker compose exec backend python manage.py evaluate_flood_model
```

---

## 8. Artifacts & Generated Paths
- Raw Boundaries: `ml/data/raw/boundaries/odisha_boundary.geojson`
- Raw Weather: `ml/data/raw/weather/nasa_power/odisha_daily_weather_2005_2024.csv`
- Raw Flood Events: `ml/data/raw/flood_events/odisha_historical_flood_events_2005_2024.csv`
- Processed Dataset: `ml/data/processed/odisha_flood_training_dataset.parquet` & `.csv`
- Model Checkpoints: `ml/models/flood_risk_xgboost.joblib` & `flood_risk_random_forest.joblib`
- Metadata & Reports: `ml/models/model_metadata.json`, `ml/data/validation/data_quality_report.json`, `ml/data/validation/model_metrics.json`, `ml/data/validation/model_report.txt`
