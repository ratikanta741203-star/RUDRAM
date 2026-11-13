"""
Cyclone Risk Feature Engineering Module for RUDRAM.
Defines features for trained XGBoost Cyclone Risk Predictor.
"""
import numpy as np

CYCLONE_FEATURE_NAMES = [
    'current_wind_speed_kmh',
    'wind_gust_kmh',
    'max_forecast_wind_kmh',
    'max_forecast_gust_kmh',
    'atmospheric_pressure_hpa',
    'min_forecast_pressure_hpa',
    'current_temperature_c',
    'relative_humidity_pct',
    'recent_rainfall_mm',
    'forecast_rainfall_7d_mm',
    'coastal_proximity_km',
    'latitude',
    'longitude'
]

def engineer_cyclone_features(raw_features: dict) -> np.ndarray:
    """
    Transforms raw telemetry dictionary into ordered float feature vector for XGBoost Cyclone Model.
    """
    wind_curr = float(raw_features.get('wind_speed_kmh', raw_features.get('wind_speed', 15.0)))
    wind_gust = float(raw_features.get('wind_gust_kmh', raw_features.get('wind_gusts', wind_curr * 1.35)))
    wind_fc = float(raw_features.get('max_forecast_wind_kmh', wind_curr * 1.2))
    gust_fc = float(raw_features.get('max_forecast_gust_kmh', wind_gust * 1.25))
    
    press_curr = float(raw_features.get('atmospheric_pressure_hpa', raw_features.get('pressure', 1012.0)))
    press_fc = float(raw_features.get('min_forecast_pressure_hpa', press_curr))
    
    temp_curr = float(raw_features.get('temperature_c', raw_features.get('temperature', 28.0)))
    humidity = float(raw_features.get('humidity_pct', raw_features.get('humidity', 80.0)))
    
    rain_recent = float(raw_features.get('rainfall_current_mm', raw_features.get('rainfall', 0.0)))
    rain_fc7d = float(raw_features.get('forecast_rainfall_7d_mm', raw_features.get('rainfall_7d_mm', 0.0)))
    
    lat = float(raw_features.get('latitude', raw_features.get('lat', 20.2961)))
    lon = float(raw_features.get('longitude', raw_features.get('lon', 85.8245)))
    
    # Calculate coastal proximity approximation for Odisha coast line
    coast_dist = max(0.5, abs(lon - 86.8) * 111.0 * 0.7)
    
    vec = [
        wind_curr,
        wind_gust,
        wind_fc,
        gust_fc,
        press_curr,
        press_fc,
        temp_curr,
        humidity,
        rain_recent,
        rain_fc7d,
        coast_dist,
        lat,
        lon
    ]
    return np.array([vec], dtype=np.float32)
