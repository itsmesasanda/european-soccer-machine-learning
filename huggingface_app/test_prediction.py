from pathlib import Path
import pandas as pd

from predictor import predict_team_profiles


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "team_season_features_eda.csv"
)

data = pd.read_csv(DATA_PATH)

sample = data.head(5)

results = predict_team_profiles(sample)

print(results)