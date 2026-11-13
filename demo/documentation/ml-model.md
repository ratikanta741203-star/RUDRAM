# RUDRAM Machine Learning & Hydrological Risk Models

## ML Engine Details
- **Architecture**: XGBoost Regressor + Random Forest Regressor comparative ensemble.
- **Inputs**: 14 physical features (24h Rain, Elevation, Slope, Distance to Water, Soil Moisture, River Crest).
- **Outputs**: Risk score (0–100%), Risk Category (LOW, MODERATE, HIGH, CRITICAL), Confidence (0–1), and Explainable Contributing Factors.
- **Scientific Honesty**: Transparent fallback to deterministic hydrological rules when standalone uncalibrated.
