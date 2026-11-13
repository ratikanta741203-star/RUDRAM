"""
Dedicated Cyclone Risk Prediction Engine for RUDRAM.
Loads trained XGBoost Cyclone classifier from MODEL_PATH/cyclone_risk_xgboost.joblib.
Executes inference on live Open-Meteo meteorological telemetry.
"""
import os
import joblib
import numpy as np
import logging
from pathlib import Path
from django.conf import settings
from ml.risk_prediction.cyclone_features import CYCLONE_FEATURE_NAMES, engineer_cyclone_features

logger = logging.getLogger(__name__)

class CycloneRiskPredictor:
    """
    Dedicated Cyclone Risk Prediction Engine.
    Loads real trained joblib model from MODEL_PATH directory.
    """
    def __init__(self):
        self.cyclone_model = None
        self.is_real_model = False
        self._load_cyclone_model()

    def _resolve_model_dir(self) -> Path:
        conf_path = getattr(settings, 'MODEL_PATH', '') or os.getenv('MODEL_PATH', '')
        base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent.parent))

        if conf_path:
            p = Path(conf_path)
            if not p.is_absolute():
                p = base_dir / p
            if p.is_file():
                return p.parent
            elif p.is_dir():
                return p

        return base_dir / "ml" / "models"

    def _load_cyclone_model(self):
        model_dir = self._resolve_model_dir()
        model_file = model_dir / "cyclone_risk_xgboost.joblib"

        if model_file.exists():
            try:
                loaded = joblib.load(model_file)
                if hasattr(loaded, "predict"):
                    self.cyclone_model = loaded
                    self.is_real_model = True
                    logger.info(f"[RUDRAM ML] Dedicated Cyclone Risk Model successfully loaded from {model_file}")
                    return
            except Exception as e:
                logger.error(f"[RUDRAM ML] Error loading cyclone model from {model_file}: {e}")

        logger.warning("[RUDRAM ML] Dedicated cyclone_risk_xgboost.joblib not found. Initializing fallback predictor.")
        self.cyclone_model = None
        self.is_real_model = False

    def predict(self, raw_features: dict) -> dict:
        """
        Predicts cyclone risk percentage using live meteorological inputs.
        """
        X = engineer_cyclone_features(raw_features)
        wind_curr = float(raw_features.get('wind_speed_kmh', raw_features.get('wind_speed', 15.0)))
        wind_gust = float(raw_features.get('wind_gust_kmh', raw_features.get('wind_gusts', wind_curr * 1.3)))
        press_curr = float(raw_features.get('atmospheric_pressure_hpa', raw_features.get('pressure', 1012.0)))
        rain_7d = float(raw_features.get('forecast_rainfall_7d_mm', raw_features.get('rainfall_7d_mm', 0.0)))

        if self.is_real_model and self.cyclone_model is not None:
            pred_val = float(self.cyclone_model.predict(X)[0])
            risk_score = round(float(np.clip(pred_val, 0.0, 100.0)), 1)
            model_mode = "REAL_CYCLONE_XGBOOST"
            confidence = 0.92
            available = True
        else:
            # Deterministic meteorological formula fallback
            score = (wind_curr / 120.0) * 60.0 + (wind_gust / 140.0) * 20.0 + max(0, 1013.0 - press_curr) * 1.2
            risk_score = round(float(np.clip(score, 0.0, 100.0)), 1)
            model_mode = "CYCLONE_DETERMINISTIC"
            confidence = 0.82
            available = True

        if risk_score <= 30.0:
            risk_level = "LOW"
            action = "Normal Operations. Monitor IMD/RSMC advisories."
        elif risk_score <= 60.0:
            risk_level = "MODERATE"
            action = "Pre-Alert State. Inspect coastal embankments and shelter readiness."
        elif risk_score <= 80.0:
            risk_level = "HIGH"
            action = "Cyclone Warning Active. Issue coastal alerts, stage ODRAF/NDRF units."
        else:
            risk_level = "CRITICAL"
            action = "EVACUATION MANDATORY. Immediate evacuation of coastal lowlands."

        return {
            'available': available,
            'risk_percentage': risk_score,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'model_mode': model_mode,
            'confidence': confidence,
            'recommended_action': action,
            'details': {
                'wind_speed_kmh': wind_curr,
                'wind_gust_kmh': wind_gust,
                'atmospheric_pressure_hpa': press_curr,
                'forecast_rainfall_7d_mm': rain_7d
            }
        }

# Global singleton cyclone predictor
cyclone_risk_predictor = CycloneRiskPredictor()
