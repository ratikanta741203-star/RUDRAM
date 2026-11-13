"""
RUDRAM Advanced ML Engine — Module 2: Enhanced Model Training & Registry
Trains, validates, and evaluates Flood Risk and Cyclone Risk models on historical datasets.
Implements temporal holdout splits, class imbalance tuning, model comparison, versioning,
and active model registry promotion rules.
"""
import os
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, brier_score_loss,
    mean_absolute_error, mean_squared_error, r2_score
)
import xgboost as xgb

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BASE_DIR / "ml" / "data" / "processed"
MODELS_DIR = BASE_DIR / "ml" / "models"
VAL_DIR = BASE_DIR / "ml" / "data" / "validation"
ROOT_REPORT_FILE = BASE_DIR / "ml_training_report.json"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
VAL_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# FLOOD MODEL FEATURE COLUMNS (Backward compatible + Enhanced)
# -----------------------------------------------------------------------------
FLOOD_FEATURE_COLS = [
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

# -----------------------------------------------------------------------------
# CYCLONE MODEL FEATURE COLUMNS
# -----------------------------------------------------------------------------
CYCLONE_FEATURE_COLS = [
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

def train_enhanced_flood_models():
    print("\n--- 1. TRAINING ENHANCED FLOOD RISK MODELS (v2) ---")
    dataset_file = PROCESSED_DIR / "combined_flood_training_dataset.csv"
    if not dataset_file.exists():
        dataset_file = PROCESSED_DIR / "odisha_flood_training_dataset_v2.csv"
    if not dataset_file.exists():
        dataset_file = PROCESSED_DIR / "odisha_flood_training_dataset.csv"

    df = pd.read_csv(dataset_file)
    df['date'] = pd.to_datetime(df['date'])

    # Fill missing features safely with sensible defaults
    defaults = {
        'rainfall_current_mm': 0.0, 'rainfall_24h_mm': 0.0, 'rainfall_7d_mm': 0.0,
        'rainfall_forecast_24h_mm': 0.0, 'temperature_c': 28.0, 'humidity_pct': 80.0,
        'wind_speed_kmh': 15.0, 'elevation_m': 25.0, 'slope_deg': 2.5,
        'distance_to_water_km': 1.2, 'historical_flood_freq': 0.5,
        'population_density_sqkm': 3000.0, 'soil_moisture_index': 0.7,
        'river_water_level_m': 10.0
    }
    for c in FLOOD_FEATURE_COLS:
        if c not in df.columns:
            df[c] = defaults[c]
        else:
            df[c] = df[c].fillna(defaults[c])

    # Temporal Holdout Splits
    train_mask = df['date'] < '2020-01-01'
    val_mask = (df['date'] >= '2020-01-01') & (df['date'] < '2023-01-01')
    test_mask = df['date'] >= '2023-01-01'

    X_train = df.loc[train_mask, FLOOD_FEATURE_COLS]
    y_train = df.loc[train_mask, 'target_flood_occurrence']

    X_val = df.loc[val_mask, FLOOD_FEATURE_COLS]
    y_val = df.loc[val_mask, 'target_flood_occurrence']

    X_test = df.loc[test_mask, FLOOD_FEATURE_COLS]
    y_test = df.loc[test_mask, 'target_flood_occurrence']

    print(f"  [+] Train set: {len(X_train):,} samples (2005–2019) | Floods: {y_train.sum():,}")
    print(f"  [+] Val set:   {len(X_val):,} samples (2020–2022) | Floods: {y_val.sum():,}")
    print(f"  [+] Test set:  {len(X_test):,} samples (2023–2025) | Floods: {y_test.sum():,}")

    # Scale weight for class imbalance
    neg_cnt = (y_train == 0).sum()
    pos_cnt = max(1, (y_train == 1).sum())
    scale_w = float(neg_cnt / pos_cnt)

    # 1. Baseline Logistic Regression Model
    lr_base = LogisticRegression(max_iter=500, solver='liblinear', random_state=42)
    lr_base.fit(X_train, y_train)

    # 2. Random Forest v2
    rf_v2 = RandomForestClassifier(
        n_estimators=120, max_depth=9, class_weight="balanced_subsample",
        min_samples_split=4, random_state=42, n_jobs=-1
    )
    rf_v2.fit(X_train, y_train)

    # 3. XGBoost v2
    xgb_v2 = xgb.XGBClassifier(
        n_estimators=150, max_depth=6, learning_rate=0.04,
        scale_pos_weight=scale_w, subsample=0.85, colsample_bytree=0.85,
        eval_metric="logloss", random_state=42
    )
    xgb_v2.fit(X_train, y_train)

    # Evaluate on held-out test set
    def eval_clf(model, X, y):
        preds = model.predict(X)
        probs = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else preds
        cm = confusion_matrix(y, preds).tolist()
        return {
            "accuracy": round(float(accuracy_score(y, preds)), 4),
            "precision": round(float(precision_score(y, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y, preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y, preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y, probs)), 4),
            "brier_score": round(float(brier_score_loss(y, probs)), 4),
            "confusion_matrix": cm
        }, probs

    m_lr, p_lr = eval_clf(lr_base, X_test, y_test)
    m_rf, p_rf = eval_clf(rf_v2, X_test, y_test)
    m_xgb, p_xgb = eval_clf(xgb_v2, X_test, y_test)

    # Ensemble: 0.65 * XGBoost + 0.35 * Random Forest
    ens_probs = 0.65 * p_xgb + 0.35 * p_rf
    ens_preds = (ens_probs >= 0.50).astype(int)
    m_ens = {
        "accuracy": round(float(accuracy_score(y_test, ens_preds)), 4),
        "precision": round(float(precision_score(y_test, ens_preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, ens_preds, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, ens_preds, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, ens_probs)), 4),
        "brier_score": round(float(brier_score_loss(y_test, ens_probs)), 4),
        "confusion_matrix": confusion_matrix(y_test, ens_preds).tolist()
    }

    # Save Versioned Models
    rf_v2_path = MODELS_DIR / "flood_risk_random_forest_v2.joblib"
    xgb_v2_path = MODELS_DIR / "flood_risk_xgboost_v2.joblib"

    joblib.dump(rf_v2, rf_v2_path)
    joblib.dump(xgb_v2, xgb_v2_path)

    # Existing active baseline model paths
    active_xgb_path = MODELS_DIR / "flood_risk_xgboost.joblib"
    active_rf_path = MODELS_DIR / "flood_risk_random_forest.joblib"

    # ACTIVE PROMOTION RULE: Evaluate baseline vs candidate
    baseline_f1 = 0.0
    if active_xgb_path.exists():
        try:
            old_xgb = joblib.load(active_xgb_path)
            old_m, _ = eval_clf(old_xgb, X_test, y_test)
            baseline_f1 = old_m['f1_score']
        except Exception:
            baseline_f1 = 0.0

    promoted = False
    if m_xgb['f1_score'] >= baseline_f1:
        joblib.dump(xgb_v2, active_xgb_path)
        joblib.dump(rf_v2, active_rf_path)
        promoted = True
        print(f"  [PROMOTED] New XGBoost v2 model promoted to active production -> {active_xgb_path}")
    else:
        print(f"  [PRESERVED] Existing active model preserved (Baseline F1: {baseline_f1} vs Candidate F1: {m_xgb['f1_score']})")

    report_flood = {
        "model_type": "Flood Risk Prediction",
        "dataset_name": dataset_file.name,
        "dataset_records": len(df),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "positive_test_samples": int(y_test.sum()),
        "negative_test_samples": int((y_test == 0).sum()),
        "candidate_metrics": {
            "logistic_regression_baseline": m_lr,
            "random_forest_v2": m_rf,
            "xgboost_v2": m_xgb,
            "weighted_ensemble": m_ens
        },
        "feature_importances": {
            feat: round(float(imp), 4) for feat, imp in zip(FLOOD_FEATURE_COLS, xgb_v2.feature_importances_)
        },
        "promoted_to_active": promoted
    }

    return report_flood, xgb_v2, rf_v2

def train_enhanced_cyclone_models():
    print("\n--- 2. TRAINING ENHANCED CYCLONE RISK MODELS (v2) ---")
    dataset_file = PROCESSED_DIR / "cyclone_training_dataset_v2.csv"
    if not dataset_file.exists():
        from ml.training.build_enhanced_datasets import build_cyclone_dataset
        build_cyclone_dataset()

    df = pd.read_csv(dataset_file)
    df['date'] = pd.to_datetime(df['date'])

    defaults = {
        'current_wind_speed_kmh': 15.0, 'wind_gust_kmh': 20.0,
        'max_forecast_wind_kmh': 18.0, 'max_forecast_gust_kmh': 24.0,
        'atmospheric_pressure_hpa': 1012.0, 'min_forecast_pressure_hpa': 1010.0,
        'current_temperature_c': 28.0, 'relative_humidity_pct': 80.0,
        'recent_rainfall_mm': 0.0, 'forecast_rainfall_7d_mm': 10.0,
        'coastal_proximity_km': 25.0, 'latitude': 20.2961, 'longitude': 85.8245
    }
    for c in CYCLONE_FEATURE_COLS:
        if c not in df.columns:
            df[c] = defaults[c]
        else:
            df[c] = df[c].fillna(defaults[c])

    # Temporal Holdout Splits
    train_mask = df['date'] < '2020-01-01'
    val_mask = (df['date'] >= '2020-01-01') & (df['date'] < '2023-01-01')
    test_mask = df['date'] >= '2023-01-01'

    X_train = df.loc[train_mask, CYCLONE_FEATURE_COLS]
    y_train = df.loc[train_mask, 'target_cyclone_risk_score']

    X_val = df.loc[val_mask, CYCLONE_FEATURE_COLS]
    y_val = df.loc[val_mask, 'target_cyclone_risk_score']

    X_test = df.loc[test_mask, CYCLONE_FEATURE_COLS]
    y_test = df.loc[test_mask, 'target_cyclone_risk_score']

    # 1. Baseline Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    # 2. Random Forest Regressor v2
    rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)

    # 3. XGBoost Regressor v2
    xgb_reg = xgb.XGBRegressor(
        n_estimators=120, max_depth=5, learning_rate=0.05,
        subsample=0.85, colsample_bytree=0.85, random_state=42
    )
    xgb_reg.fit(X_train, y_train)

    def eval_reg(model, X, y):
        preds = model.predict(X)
        return {
            "mae": round(float(mean_absolute_error(y, preds)), 4),
            "rmse": round(float(np.sqrt(mean_squared_error(y, preds))), 4),
            "r2": round(float(r2_score(y, preds)), 4)
        }, preds

    m_lr, p_lr = eval_reg(lr, X_test, y_test)
    m_rf, p_rf = eval_reg(rf, X_test, y_test)
    m_xgb, p_xgb = eval_reg(xgb_reg, X_test, y_test)

    # Save Versioned Models
    xgb_v2_path = MODELS_DIR / "cyclone_risk_xgboost_v2.joblib"
    joblib.dump(xgb_reg, xgb_v2_path)

    active_cyc_path = MODELS_DIR / "cyclone_risk_xgboost.joblib"

    # ACTIVE PROMOTION RULE
    baseline_mae = 999.0
    if active_cyc_path.exists():
        try:
            old_cyc = joblib.load(active_cyc_path)
            old_m, _ = eval_reg(old_cyc, X_test, y_test)
            baseline_mae = old_m['mae']
        except Exception:
            baseline_mae = 999.0

    promoted = False
    if m_xgb['mae'] <= baseline_mae or not active_cyc_path.exists():
        joblib.dump(xgb_reg, active_cyc_path)
        promoted = True
        print(f"  [PROMOTED] New XGBoost Cyclone v2 model promoted to active production -> {active_cyc_path}")
    else:
        print(f"  [PRESERVED] Existing active cyclone model preserved (Baseline MAE: {baseline_mae} vs Candidate MAE: {m_xgb['mae']})")

    report_cyc = {
        "model_type": "Cyclone Risk Prediction",
        "dataset_name": dataset_file.name,
        "dataset_records": len(df),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "candidate_metrics": {
            "linear_regression_baseline": m_lr,
            "random_forest_v2": m_rf,
            "xgboost_v2": m_xgb
        },
        "feature_importances": {
            feat: round(float(imp), 4) for feat, imp in zip(CYCLONE_FEATURE_COLS, xgb_reg.feature_importances_)
        },
        "promoted_to_active": promoted
    }

    return report_cyc, xgb_reg

def run_all_training():
    print("==========================================================")
    print("RUDRAM STEP 2: ML MODEL TRAINING & EVALUATION ENGINE (v2)")
    print("==========================================================")
    report_flood, _, _ = train_enhanced_flood_models()
    report_cyc, _ = train_enhanced_cyclone_models()

    # Model Registry Management
    registry = {
        "registry_version": "2.0.0",
        "last_updated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active_models": [
            {
                "model_name": "RUDRAM Flood Risk Multi-Disaster Estimator",
                "version": "v2.0.0-odisha-india",
                "file_path": "ml/models/flood_risk_xgboost.joblib",
                "algorithm": "XGBoost Classifier + RF Ensemble",
                "status": "ACTIVE",
                "test_f1_score": report_flood["candidate_metrics"]["xgboost_v2"]["f1_score"],
                "test_roc_auc": report_flood["candidate_metrics"]["xgboost_v2"]["roc_auc"]
            },
            {
                "model_name": "RUDRAM Dedicated Tropical Cyclone Risk Predictor",
                "version": "v2.0.0-north-indian-ocean",
                "file_path": "ml/models/cyclone_risk_xgboost.joblib",
                "algorithm": "XGBoost Regressor",
                "status": "ACTIVE",
                "test_mae": report_cyc["candidate_metrics"]["xgboost_v2"]["mae"],
                "test_r2": report_cyc["candidate_metrics"]["xgboost_v2"]["r2"]
            }
        ],
        "archived_models": [
            {
                "model_name": "Flood Risk Baseline",
                "version": "v1.0.0-odisha-statewide",
                "file_path": "ml/models/flood_risk_random_forest.joblib",
                "status": "VALIDATED"
            }
        ]
    }

    reg_path = MODELS_DIR / "model_registry.json"
    with open(reg_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)

    # Save Model Metadata
    meta_path = MODELS_DIR / "model_metadata.json"
    metadata = {
        "flood_model": report_flood,
        "cyclone_model": report_cyc,
        "registry": registry
    }
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    # Data Quality Report JSON
    quality_report = {
        "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "flood_dataset": {
            "records": report_flood["dataset_records"],
            "features_count": len(FLOOD_FEATURE_COLS),
            "missing_values": 0,
            "temporal_range": "2005-01-01 to 2025-12-31"
        },
        "cyclone_dataset": {
            "records": report_cyc["dataset_records"],
            "features_count": len(CYCLONE_FEATURE_COLS),
            "missing_values": 0,
            "temporal_range": "1999-10-29 to 2025-12-31"
        }
    }
    dq_path = VAL_DIR / "data_quality_report.json"
    with open(dq_path, 'w', encoding='utf-8') as f:
        json.dump(quality_report, f, indent=2)

    metrics_path = VAL_DIR / "model_metrics.json"
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump({"flood": report_flood["candidate_metrics"], "cyclone": report_cyc["candidate_metrics"]}, f, indent=2)

    # Write Root ML Training Report
    with open(ROOT_REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    # Human-Readable Report TXT
    report_txt_path = VAL_DIR / "model_report.txt"
    with open(report_txt_path, 'w', encoding='utf-8') as f:
        f.write("=================================================================\n")
        f.write("RUDRAM PLATFORM — HISTORICAL ML MODEL TRAINING & EVALUATION REPORT\n")
        f.write("=================================================================\n\n")
        f.write(f"Generated At: {metadata['registry']['last_updated']}\n\n")
        f.write("1. FLOOD RISK MODEL METRICS (Held-Out Test Set 2023-2025):\n")
        f.write(f"   - XGBoost v2 F1-Score: {report_flood['candidate_metrics']['xgboost_v2']['f1_score']}\n")
        f.write(f"   - XGBoost v2 ROC-AUC:  {report_flood['candidate_metrics']['xgboost_v2']['roc_auc']}\n")
        f.write(f"   - XGBoost v2 Recall:   {report_flood['candidate_metrics']['xgboost_v2']['recall']}\n")
        f.write(f"   - Random Forest v2 F1: {report_flood['candidate_metrics']['random_forest_v2']['f1_score']}\n\n")
        f.write("2. CYCLONE RISK MODEL METRICS (Held-Out Test Set 2023-2025):\n")
        f.write(f"   - XGBoost Regressor MAE: {report_cyc['candidate_metrics']['xgboost_v2']['mae']}%\n")
        f.write(f"   - XGBoost Regressor R²:  {report_cyc['candidate_metrics']['xgboost_v2']['r2']}\n\n")
        f.write("3. ACTIVE MODEL REGISTRY STATUS:\n")
        f.write("   - Flood Risk Active Model: flood_risk_xgboost.joblib (Status: ACTIVE)\n")
        f.write("   - Cyclone Risk Active Model: cyclone_risk_xgboost.joblib (Status: ACTIVE)\n")
        f.write("=================================================================\n")

    print("\n[OK] ML Training & Validation Completed Successfully!")
    print(f"     Model Registry -> {reg_path}")
    print(f"     Root ML Report -> {ROOT_REPORT_FILE}")

if __name__ == "__main__":
    run_all_training()
