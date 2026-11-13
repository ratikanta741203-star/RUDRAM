"""
RUDRAM ML Training Pipeline - Module 6: Model Training Engine
Trains real XGBoost and Random Forest classifiers on Odisha historical flood dataset
using strict temporal holdout validation (Train: 2005-2019, Val: 2020-2022, Test: 2023-2024).
Saves models to ml/models/ and generates model_metadata.json.
"""
import os
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BASE_DIR / "ml" / "data" / "processed"
MODELS_DIR = BASE_DIR / "ml" / "models"
VAL_DIR = BASE_DIR / "ml" / "data" / "validation"

FEATURE_COLS = [
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

def run():
    print("==================================================")
    print("RUDRAM - STEP 4: TRAINING REAL XGBOOST + RF MODELS")
    print("==================================================")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    VAL_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = PROCESSED_DIR / "odisha_flood_training_dataset.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Processed dataset not found at {csv_path}. Run build_training_dataset.py first.")

    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])

    # Temporal Holdout Splits to prevent temporal leakage
    train_mask = df['date'] < '2020-01-01'
    val_mask = (df['date'] >= '2020-01-01') & (df['date'] < '2023-01-01')
    test_mask = df['date'] >= '2023-01-01'

    X_train = df.loc[train_mask, FEATURE_COLS]
    y_train = df.loc[train_mask, 'target_flood_occurrence']

    X_val = df.loc[val_mask, FEATURE_COLS]
    y_val = df.loc[val_mask, 'target_flood_occurrence']

    X_test = df.loc[test_mask, FEATURE_COLS]
    y_test = df.loc[test_mask, 'target_flood_occurrence']

    print(f"  [+] Train set: {len(X_train):,} samples (2005–2019) | Floods: {y_train.sum():,}")
    print(f"  [+] Val set:   {len(X_val):,} samples (2020–2022) | Floods: {y_val.sum():,}")
    print(f"  [+] Test set:  {len(X_test):,} samples (2023–2024) | Floods: {y_test.sum():,}")

    # Calculate class imbalance weight for XGBoost
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_weight = max(1.0, float(neg_count / max(1, pos_count)))

    # 1. Train Real XGBoost Classifier
    print("  [1/2] Training XGBoost Classifier (scale_pos_weight tuned)...")
    xgb_clf = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.06,
        scale_pos_weight=scale_weight,
        subsample=0.85,
        colsample_bytree=0.85,
        eval_metric="logloss",
        random_state=42
    )
    xgb_clf.fit(X_train, y_train)

    # 2. Train Real Random Forest Classifier
    print("  [2/2] Training Random Forest Classifier (balanced subsamples)...")
    rf_clf = RandomForestClassifier(
        n_estimators=80,
        max_depth=7,
        class_weight="balanced_subsample",
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
    rf_clf.fit(X_train, y_train)

    # Save models using joblib
    xgb_path = MODELS_DIR / "flood_risk_xgboost.joblib"
    rf_path = MODELS_DIR / "flood_risk_random_forest.joblib"

    joblib.dump(xgb_clf, xgb_path)
    joblib.dump(rf_clf, rf_path)
    print(f"  [OK] Saved XGBoost Model -> {xgb_path}")
    print(f"  [OK] Saved Random Forest Model -> {rf_path}")

    # Evaluate on Test Set
    xgb_preds = xgb_clf.predict(X_test)
    xgb_probs = xgb_clf.predict_proba(X_test)[:, 1]

    rf_preds = rf_clf.predict(X_test)
    rf_probs = rf_clf.predict_proba(X_test)[:, 1]

    ens_probs = 0.65 * xgb_probs + 0.35 * rf_probs
    ens_preds = (ens_probs >= 0.50).astype(int)

    metrics = {
        "xgboost": {
            "accuracy": round(float(accuracy_score(y_test, xgb_preds)), 4),
            "precision": round(float(precision_score(y_test, xgb_preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, xgb_preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, xgb_preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, xgb_probs)), 4)
        },
        "random_forest": {
            "accuracy": round(float(accuracy_score(y_test, rf_preds)), 4),
            "precision": round(float(precision_score(y_test, rf_preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, rf_preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, rf_preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, rf_probs)), 4)
        },
        "ensemble": {
            "accuracy": round(float(accuracy_score(y_test, ens_preds)), 4),
            "precision": round(float(precision_score(y_test, ens_preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, ens_preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, ens_preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, ens_probs)), 4)
        }
    }

    # Model Metadata
    metadata = {
        "model_version": "v1.0.0-odisha-statewide",
        "training_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_name": "Odisha Historical Flood Training Dataset (2005-2024)",
        "features_count": len(FEATURE_COLS),
        "features_list": FEATURE_COLS,
        "geographic_area": "Odisha State, India (30 Districts)",
        "temporal_coverage": {
            "training_period": "2005-01-01 to 2019-12-31",
            "validation_period": "2020-01-01 to 2022-12-31",
            "test_period": "2023-01-01 to 2024-12-31",
            "total_years": 20
        },
        "dataset_split_samples": {
            "total_samples": len(df),
            "train_samples": len(X_train),
            "validation_samples": len(X_val),
            "test_samples": len(X_test),
            "test_flood_samples": int(y_test.sum()),
            "test_non_flood_samples": int((y_test == 0).sum())
        },
        "algorithms": {
            "xgboost": "XGBClassifier (n_estimators=100, max_depth=5, scale_pos_weight tuned)",
            "random_forest": "RandomForestClassifier (n_estimators=80, max_depth=7, class_weight=balanced_subsample)",
            "ensemble_strategy": "Weighted Probability Blend (0.65 * XGBoost + 0.35 * Random Forest)"
        },
        "test_metrics": metrics,
        "feature_importances": {
            feat: round(float(imp), 4) for feat, imp in zip(FEATURE_COLS, xgb_clf.feature_importances_)
        }
    }

    meta_path = MODELS_DIR / "model_metadata.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"  [OK] Saved Model Metadata -> {meta_path}")
    print(f"  [+] Test Metrics (Ensemble) -> Accuracy: {metrics['ensemble']['accuracy']}, Recall: {metrics['ensemble']['recall']}, Precision: {metrics['ensemble']['precision']}, F1: {metrics['ensemble']['f1_score']}, ROC-AUC: {metrics['ensemble']['roc_auc']}")

    return metadata

if __name__ == "__main__":
    run()
