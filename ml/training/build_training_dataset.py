"""
RUDRAM ML Training Pipeline - Module 5: Dataset Builder
Assembles the complete state-wide Odisha training matrix into Parquet & CSV formats.
"""
import pandas as pd
from pathlib import Path
from ml.training.preprocess import load_and_preprocess_raw
from ml.training.feature_engineering import engineer_training_features

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BASE_DIR / "ml" / "data" / "processed"

def run():
    print("==================================================")
    print("RUDRAM - STEP 3: BUILDING TRAINING DATASET")
    print("==================================================")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df_raw = load_and_preprocess_raw()
    print(f"  [+] Loaded {len(df_raw):,} preprocessed records.")

    df_feat = engineer_training_features(df_raw)
    
    # Add unique sample_id
    df_feat.insert(0, 'sample_id', [f"OD_SAMP_{i+1:07d}" for i in range(len(df_feat))])

    # Save to Parquet
    parquet_path = PROCESSED_DIR / "odisha_flood_training_dataset.parquet"
    try:
        df_feat.to_parquet(parquet_path, index=False)
        print(f"  [OK] Saved Parquet dataset -> {parquet_path}")
    except Exception as e:
        print(f"  [!] Parquet save fallback: {e}")

    # Save to CSV
    csv_path = PROCESSED_DIR / "odisha_flood_training_dataset.csv"
    df_feat.to_csv(csv_path, index=False)
    print(f"  [OK] Saved CSV dataset ({len(df_feat):,} rows, {len(df_feat.columns)} cols) -> {csv_path}")

    return df_feat

if __name__ == "__main__":
    run()
