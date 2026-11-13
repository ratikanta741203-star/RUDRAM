import numpy as np
import pandas as pd

FEATURE_NAMES = [
    'rainfall_current_mm',
    'rainfall_24h_mm',
    'rainfall_7d_mm',
    'rainfall_forecast_24h_mm',
    'temperature_c',
    'humidity_pct',
    'wind_speed_kmh',
    'elevation_m',
    'slope_deg',
    'distance_to_water_km',
    'historical_flood_freq',
    'population_density_sqkm',
    'soil_moisture_index',
    'river_water_level_m'
]

def engineer_features(raw_dict):
    """
    Extracts, normalizes and prepares named feature vectors for ML risk prediction.
    """
    features = {}
    defaults = {
        'rainfall_current_mm': 15.0,
        'rainfall_24h_mm': 65.0,
        'rainfall_7d_mm': 180.0,
        'rainfall_forecast_24h_mm': 40.0,
        'temperature_c': 28.0,
        'humidity_pct': 85.0,
        'wind_speed_kmh': 24.0,
        'elevation_m': 25.0,
        'slope_deg': 2.5,
        'distance_to_water_km': 1.2,
        'historical_flood_freq': 0.6,
        'population_density_sqkm': 3200.0,
        'soil_moisture_index': 0.78,
        'river_water_level_m': 13.5
    }
    for f in FEATURE_NAMES:
        val = raw_dict.get(f)
        if val is None or val == '':
            val = defaults.get(f, 0.0)
        try:
            features[f] = float(val)
        except (ValueError, TypeError):
            features[f] = defaults.get(f, 0.0)

    return pd.DataFrame([features], columns=FEATURE_NAMES)
