"""
RUDRAM ML Training Pipeline - Module 3: Feature Engineering
Calculates rolling meteorological lags, terrain indicators, and historical
flood frequencies while strictly preventing temporal target leakage.
"""
import pandas as pd
import numpy as np

def compute_historical_flood_frequencies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes expanding historical flood frequency per district to eliminate target leakage.
    Each sample's historical_flood_freq is computed solely from past observations up to that year.
    """
    df = df.sort_values(by=['district', 'date']).reset_index(drop=True)
    df['year'] = pd.to_datetime(df['date']).dt.year

    # Calculate cumulative past flood events per district
    # Prior mean baseline is 0.05 to avoid zero-division in initial periods
    df['cum_floods'] = df.groupby('district')['target_flood_occurrence'].cumsum() - df['target_flood_occurrence']
    df['cum_days'] = df.groupby('district').cumcount() + 1

    df['historical_flood_freq'] = np.clip(
        (df['cum_floods'] / df['cum_days']) * 10.0 + 0.15,
        0.05,
        1.0
    ).round(3)

    df.drop(columns=['cum_floods', 'cum_days', 'year'], inplace=True)
    return df

def engineer_training_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares standard 14-feature vector for RUDRAM XGBoost & Random Forest models.
    """
    df = compute_historical_flood_frequencies(df)
    
    # Ensure all required features are present and float typed
    feature_cols = [
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

    for col in feature_cols:
        df[col] = df[col].astype(float)

    return df
