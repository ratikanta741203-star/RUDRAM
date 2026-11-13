"""
RUDRAM ML Training Pipeline - Module 7: Evaluation & Model Reporting
Evaluates trained models on the out-of-sample test set (2023-2024),
generates confusion matrices, feature importance rankings, model_metrics.json,
and human-readable model_report.txt.
"""
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, classification_report
)

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
    print("RUDRAM - STEP 5: EVALUATING TRAINED FLOOD MODELS")
    print("==================================================")
    VAL_DIR.mkdir(parents=True, exist_ok=True)

    xgb_path = MODELS_DIR / "flood_risk_xgboost.joblib"
    rf_path = MODELS_DIR / "flood_risk_random_forest.joblib"
    csv_path = PROCESSED_DIR / "odisha_flood_training_dataset.csv"

    if not xgb_path.exists() or not rf_path.exists():
        raise FileNotFoundError("Trained models not found. Run train.py first.")

    xgb_model = joblib.load(xgb_path)
    rf_model = joblib.load(rf_path)

    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])

    # Test set: 2023–2024
    test_mask = df['date'] >= '2023-01-01'
    X_test = df.loc[test_mask, FEATURE_COLS]
    y_test = df.loc[test_mask, 'target_flood_occurrence']

    xgb_probs = xgb_model.predict_proba(X_test)[:, 1]
    rf_probs = rf_model.predict_proba(X_test)[:, 1]
    ens_probs = 0.65 * xgb_probs + 0.35 * rf_probs

    xgb_preds = xgb_model.predict(X_test)
    rf_preds = rf_model.predict(X_test)
    ens_preds = (ens_probs >= 0.50).astype(int)

    cm = confusion_matrix(y_test, ens_preds)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "evaluation_dataset": {
            "test_period": "2023-01-01 to 2024-12-31",
            "total_test_samples": len(y_test),
            "actual_flood_samples": int(y_test.sum()),
            "actual_non_flood_samples": int((y_test == 0).sum())
        },
        "models": {
            "xgboost": {
                "accuracy": round(float(accuracy_score(y_test, xgb_preds)), 4),
                "precision": round(float(precision_score(y_test, xgb_preds, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, xgb_preds, zero_division=0)), 4),
                "f1_score": round(float(f1_score(y_test, xgb_preds, zero_division=0)), 4),
                "roc_auc": round(float(roc_auc_score(y_test, xgb_probs)), 4),
                "pr_auc": round(float(average_precision_score(y_test, xgb_probs)), 4)
            },
            "random_forest": {
                "accuracy": round(float(accuracy_score(y_test, rf_preds)), 4),
                "precision": round(float(precision_score(y_test, rf_preds, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, rf_preds, zero_division=0)), 4),
                "f1_score": round(float(f1_score(y_test, rf_preds, zero_division=0)), 4),
                "roc_auc": round(float(roc_auc_score(y_test, rf_probs)), 4),
                "pr_auc": round(float(average_precision_score(y_test, rf_probs)), 4)
            },
            "ensemble_xgboost_rf": {
                "accuracy": round(float(accuracy_score(y_test, ens_preds)), 4),
                "precision": round(float(precision_score(y_test, ens_preds, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, ens_preds, zero_division=0)), 4),
                "f1_score": round(float(f1_score(y_test, ens_preds, zero_division=0)), 4),
                "roc_auc": round(float(roc_auc_score(y_test, ens_probs)), 4),
                "pr_auc": round(float(average_precision_score(y_test, ens_probs)), 4),
                "confusion_matrix": {
                    "true_negatives": int(tn),
                    "false_positives": int(fp),
                    "false_negatives": int(fn),
                    "true_positives": int(tp)
                }
            }
        },
        "feature_importances_ranking": sorted(
            [{"feature": f, "importance": round(float(imp), 4)} for f, imp in zip(FEATURE_COLS, xgb_model.feature_importances_)],
            key=lambda x: x["importance"],
            reverse=True
        )
    }

    # Save JSON metrics
    metrics_json_path = VAL_DIR / "model_metrics.json"
    with open(metrics_json_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    # Save Text Report
    report_txt_path = VAL_DIR / "model_report.txt"
    with open(report_txt_path, 'w', encoding='utf-8') as f:
        f.write("======================================================================\n")
        f.write("RUDRAM AI FLOOD RISK PREDICTION - ODISHA STATEWIDE MODEL REPORT\n")
        f.write("======================================================================\n\n")
        f.write(f"Evaluation Period: 2023-01-01 to 2024-12-31 (Out-of-Sample Holdout)\n")
        f.write(f"Total Test Samples: {len(y_test):,} | Actual Flood Events: {y_test.sum():,}\n\n")
        f.write("MODEL PERFORMANCE SUMMARY:\n")
        f.write(f"  Ensemble Accuracy:  {metrics['models']['ensemble_xgboost_rf']['accuracy']*100:.2f}%\n")
        f.write(f"  Ensemble Recall:    {metrics['models']['ensemble_xgboost_rf']['recall']*100:.2f}% (Critical for early flood warning)\n")
        f.write(f"  Ensemble Precision: {metrics['models']['ensemble_xgboost_rf']['precision']*100:.2f}%\n")
        f.write(f"  Ensemble F1-Score:  {metrics['models']['ensemble_xgboost_rf']['f1_score']:.4f}\n")
        f.write(f"  Ensemble ROC-AUC:   {metrics['models']['ensemble_xgboost_rf']['roc_auc']:.4f}\n")
        f.write(f"  Ensemble PR-AUC:    {metrics['models']['ensemble_xgboost_rf']['pr_auc']:.4f}\n\n")
        f.write("CONFUSION MATRIX:\n")
        f.write(f"  True Negatives (No Flood):  {tn:,}\n")
        f.write(f"  False Positives (False Alarm): {fp:,}\n")
        f.write(f"  False Negatives (Missed Flood): {fn:,}\n")
        f.write(f"  True Positives (Detected Flood): {tp:,}\n\n")
        f.write("TOP CONTRIBUTING FEATURES:\n")
        for idx, feat in enumerate(metrics["feature_importances_ranking"][:7], 1):
            f.write(f"  {idx}. {feat['feature']:<28} : {feat['importance']:.4f}\n")

    print(f"  [OK] Evaluation complete. Metrics saved to {metrics_json_path}")
    print(f"  [OK] Detailed text report written to {report_txt_path}")
    return metrics

if __name__ == "__main__":
    run()
