from pathlib import Path
import json
import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_DIR = PROJECT_ROOT / "models" / "team_profiling"

model = joblib.load(
    MODEL_DIR / "team_profile_kmeans.joblib"
)

scaler = joblib.load(
    MODEL_DIR / "team_profile_scaler.joblib"
)

with open(MODEL_DIR / "final_features.json") as f:
    final_features = json.load(f)

with open(MODEL_DIR / "profile_names.json") as f:
    profile_names = json.load(f)


print("Model loaded successfully.")
print("Expected features:", len(final_features))
print(final_features)
print("\nProfiles:")
print(profile_names)