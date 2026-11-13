# RUDRAM Odisha Statewide Flood Risk ML Training Pipeline

## Overview
This directory contains the complete end-to-end data harvesting, preprocessing, validation, training, and evaluation pipeline for the Odisha Statewide Flood Risk Prediction Models.

## Architecture
- **Data Period**: 2005–2024 (20 years of continuous daily historical meteorological and hydrological records).
- **Geographic Coverage**: Entire State of Odisha, India (30 Districts statewide).
- **Primary Data Sources**:
  1. NASA POWER (Daily precipitation, temperature, humidity, wind).
  2. NASA SRTM 30m Global DEM (Topographic elevation and slope gradient).
  3. OSDMA / CWC / Dartmouth Flood Observatory (Documented historical flood events and disaster impact boundaries).
  4. OpenStreetMap / Hydrographic Arteries (Geodesic distance to major river systems).
  5. Census & WorldPop (Spatial population density distributions).
- **ML Estimators**:
  - `XGBClassifier` (Gradient Boosting with scale_pos_weight for flood class imbalance).
  - `RandomForestClassifier` (Balanced sub-sample ensemble).
  - `Weighted Probability Ensemble` ($0.65 \times \text{XGBoost} + 0.35 \times \text{Random Forest}$).

## Pipeline Execution
Run through Django management commands or directly:
```bash
python manage.py download_flood_data
python manage.py validate_flood_data
python manage.py build_flood_dataset
python manage.py train_flood_model
python manage.py evaluate_flood_model
```
