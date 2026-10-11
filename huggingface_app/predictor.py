from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "models" / "team_profiling"

model = joblib.load(MODEL_DIR / "team_profile_kmeans.joblib")
scaler = joblib.load(MODEL_DIR / "team_profile_scaler.joblib")

with open(MODEL_DIR / "final_features.json", encoding="utf-8") as f:
    final_features = json.load(f)

with open(MODEL_DIR / "profile_names.json", encoding="utf-8") as f:
    profile_names = json.load(f)


REQUIRED_COLUMNS = [
    "avg_overall_rating",
    "avg_potential",
    "goalkeeper_rating",
    "avg_pace",
    "avg_physical",
    "avg_defence",
    "avg_attack",
    "buildUpPlaySpeed",
    "buildUpPlayPassing",
    "chanceCreationPassing",
    "chanceCreationCrossing",
    "chanceCreationShooting",
    "defencePressure",
    "defenceAggression",
    "defenceTeamWidth"
]


def predict_team_profiles(data: pd.DataFrame) -> pd.DataFrame:
    """Assign each team to its nearest saved K-Means profile."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Prediction input must be a pandas DataFrame.")

    if data.empty:
        raise ValueError("No team data rows were provided.")

    data = data.copy()

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    # Ensure required attributes are finite numeric values in the expected range.
    for column in REQUIRED_COLUMNS:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    numeric_data = data[REQUIRED_COLUMNS]
    invalid_numeric = numeric_data.isna() | ~np.isfinite(numeric_data)

    if invalid_numeric.any().any():
        bad_columns = data[
            REQUIRED_COLUMNS
        ].columns[
            invalid_numeric.any()
        ].tolist()

        raise ValueError(
            "Missing or invalid numeric values in: "
            + ", ".join(bad_columns)
        )

    outside_range = (numeric_data < 0) | (numeric_data > 100)

    if outside_range.any().any():
        bad_columns = numeric_data.columns[
            outside_range.any()
        ].tolist()

        raise ValueError(
            "Values must be between 0 and 100 in: "
            + ", ".join(bad_columns)
        )

    # Reproduce the feature engineering used during training
    data["development_gap"] = (
        data["avg_potential"]
        - data["avg_overall_rating"]
    )

    data["goalkeeper_relative_strength"] = (
        data["goalkeeper_rating"]
        - data["avg_overall_rating"]
    )

    data["attack_defence_balance"] = (
        data["avg_attack"]
        - data["avg_defence"]
    )

    X = data[final_features]

    X_scaled = scaler.transform(X)

    X_scaled = pd.DataFrame(
        X_scaled,
        columns=final_features,
        index=X.index
    )

    clusters = model.predict(X_scaled)

    distances = model.transform(X_scaled)

    closest_distance = distances[
        np.arange(len(data)),
        clusters
    ]

    results = pd.DataFrame()

    default_names = [
        f"Team {i + 1}"
        for i in range(len(data))
    ]

    if "team_name" in data.columns:
        results["team_name"] = [
            str(name).strip()
            if pd.notna(name) and str(name).strip()
            else default_names[position]
            for position, name in enumerate(data["team_name"])
        ]
    else:
        results["team_name"] = default_names

    results["cluster"] = clusters

    results["team_profile"] = [
        profile_names[str(cluster)]
        for cluster in clusters
    ]

    results["distance_to_centroid"] = (
        closest_distance.round(3)
    )

    return results
