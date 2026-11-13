"""
RUDRAM ML Training Pipeline - Module 4: Preprocessing
Cleans raw meteorological, hydrological, and geospatial tables.
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "ml" / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "ml" / "data" / "processed"

def load_and_preprocess_raw():
    weather_csv = RAW_DIR / "weather" / "nasa_power" / "odisha_daily_weather_2005_2024.csv"
    if not weather_csv.exists():
        raise FileNotFoundError(f"Missing raw weather file: {weather_csv}")

    df = pd.read_csv(weather_csv)
    df['date'] = pd.to_datetime(df['date'])

    # Drop any potential NaN rows or fill with sensible median
    df = df.dropna().reset_index(drop=True)
    return df
