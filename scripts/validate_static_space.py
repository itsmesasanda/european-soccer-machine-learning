"""Validate browser inference against the saved Python clustering artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import warnings

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SPACE = ROOT / "static_space"
MODEL_DIR = ROOT / "models/team_profiling"
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
    "defenceTeamWidth",
]


def python_predictions(rows: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    scaler = joblib.load(MODEL_DIR / "team_profile_scaler.joblib")
    model = joblib.load(MODEL_DIR / "team_profile_kmeans.joblib")
    features = json.loads((MODEL_DIR / "final_features.json").read_text())
    profile_names = json.loads((MODEL_DIR / "profile_names.json").read_text())

    derived = rows.copy()
    derived["development_gap"] = (
        derived["avg_potential"] - derived["avg_overall_rating"]
    )
    derived["goalkeeper_relative_strength"] = (
        derived["goalkeeper_rating"] - derived["avg_overall_rating"]
    )
    derived["attack_defence_balance"] = (
        derived["avg_attack"] - derived["avg_defence"]
    )
    feature_matrix = derived.loc[:, features]

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        scaled = scaler.transform(feature_matrix)
        scaled_frame = pd.DataFrame(
            scaled,
            columns=features,
            index=feature_matrix.index,
        )
        clusters = model.predict(scaled_frame)
    warning_messages = [str(item.message) for item in caught]

    distances = np.linalg.norm(
        scaled - model.cluster_centers_[clusters],
        axis=1,
    )
    return (
        pd.DataFrame(
            {
                "team_name": rows["team_name"].fillna("Unnamed Team"),
                "cluster": clusters.astype(int),
                "team_profile": [profile_names[str(value)] for value in clusters],
                "distance_to_centroid": np.round(distances, 3),
            }
        ),
        warning_messages,
    )


def main() -> None:
    historical = pd.read_csv(
        ROOT / "data/processed/team_season_features_eda.csv"
    )
    indices = np.linspace(0, len(historical) - 1, 20, dtype=int)
    sample = historical.iloc[indices].copy()
    python_results, warning_messages = python_predictions(sample)
    feature_warnings = [
        message for message in warning_messages
        if "feature names" in message.lower()
    ]
    assert not feature_warnings, feature_warnings

    payload = {
        "rows": sample[["team_name", *REQUIRED_COLUMNS]].to_dict(orient="records"),
        "csv": (SPACE / "example_team_data.csv").read_text(encoding="utf-8"),
    }
    completed = subprocess.run(
        ["node", str(ROOT / "scripts/static_space_node_check.js"), str(SPACE)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    javascript = json.loads(completed.stdout)
    javascript_results = javascript["predictions"]

    cluster_mismatches = []
    distance_mismatches = []
    for position, (python_row, javascript_row) in enumerate(
        zip(python_results.to_dict(orient="records"), javascript_results)
    ):
        if int(python_row["cluster"]) != int(javascript_row["cluster"]):
            cluster_mismatches.append((position, python_row, javascript_row))
        difference = abs(
            float(python_row["distance_to_centroid"])
            - float(javascript_row["distance_to_centroid"])
        )
        if difference > 1e-12:
            distance_mismatches.append(
                (position, difference, python_row, javascript_row)
            )

    assert not cluster_mismatches, cluster_mismatches
    assert not distance_mismatches, distance_mismatches

    kv_python = python_results.iloc[0]
    kv_javascript = javascript_results[0]
    assert sample.iloc[0]["team_name"] == "KV Mechelen"
    assert int(kv_python["cluster"]) == int(kv_javascript["cluster"]) == 1
    assert float(kv_python["distance_to_centroid"]) == float(
        kv_javascript["distance_to_centroid"]
    ) == 3.446

    assert len(javascript["csvResults"]) == 3
    assert all(0 <= int(row["cluster"]) <= 4 for row in javascript["csvResults"])
    assert all(
        float(row["distance_to_centroid"]) >= 0
        for row in javascript["csvResults"]
    )
    assert all(javascript["validationErrors"].values())

    print(f"historical_rows={len(javascript_results)}")
    print(f"cluster_mismatches={len(cluster_mismatches)}")
    print(f"distance_mismatches={len(distance_mismatches)}")
    print("maximum_rounded_distance_difference=0.0")
    print("kv_mechelen=cluster_1,distance_3.446")
    print(f"csv_rows={len(javascript['csvResults'])}")
    print("csv_validation_cases=6")
    print("sklearn_feature_name_warnings=0")


if __name__ == "__main__":
    main()
