import json
from pathlib import Path
import warnings

from fastapi.testclient import TestClient

from huggingface_app.app import app


PROJECT_ROOT = Path(__file__).resolve().parents[2]
with open(
    PROJECT_ROOT / "models" / "team_profiling" / "profile_names.json",
    encoding="utf-8",
) as profile_file:
    PROFILE_NAMES = json.load(profile_file)

client = TestClient(app)

VALID_TEAM = {
    "team_name": "Example FC",
    "avg_overall_rating": 70,
    "avg_potential": 75,
    "goalkeeper_rating": 70,
    "avg_pace": 72,
    "avg_physical": 70,
    "avg_defence": 68,
    "avg_attack": 72,
    "buildUpPlaySpeed": 55,
    "buildUpPlayPassing": 55,
    "chanceCreationPassing": 55,
    "chanceCreationCrossing": 55,
    "chanceCreationShooting": 55,
    "defencePressure": 55,
    "defenceAggression": 55,
    "defenceTeamWidth": 55,
}


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model": "K-Means Team Profiler",
        "profiles": 5,
    }


def test_profiles_match_saved_mapping() -> None:
    response = client.get("/profiles")

    assert response.status_code == 200
    profiles = response.json()
    assert len(profiles) == 5
    assert {str(item["cluster"]): item["name"] for item in profiles} == PROFILE_NAMES
    assert all(item["description"] for item in profiles)


def test_predict_valid_input() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        response = client.post("/predict", json=VALID_TEAM)

    assert response.status_code == 200
    result = response.json()
    assert result["team_name"] == "Example FC"
    assert result["cluster"] in range(5)
    assert result["team_profile"] == PROFILE_NAMES[str(result["cluster"])]
    assert isinstance(result["distance_to_centroid"], (int, float))
    assert result["distance_to_centroid"] >= 0
    assert not any("feature names" in str(item.message).lower() for item in caught)


def test_predict_missing_field() -> None:
    payload = VALID_TEAM.copy()
    payload.pop("avg_attack")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
    assert any(error["field"] == "avg_attack" for error in response.json()["errors"])


def test_predict_invalid_range() -> None:
    payload = {**VALID_TEAM, "avg_pace": 101}

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
    assert any(error["field"] == "avg_pace" for error in response.json()["errors"])


def test_predict_csv_valid() -> None:
    example_path = (
        PROJECT_ROOT / "huggingface_app" / "examples" / "example_team_data.csv"
    )

    with example_path.open("rb") as csv_file:
        response = client.post(
            "/predict-csv",
            files={"file": ("teams.csv", csv_file, "text/csv")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 3
    assert len(body["results"]) == 3
    for result in body["results"]:
        assert result["cluster"] in range(5)
        assert result["team_profile"] == PROFILE_NAMES[str(result["cluster"])]
        assert result["distance_to_centroid"] >= 0


def test_predict_csv_missing_required_columns() -> None:
    csv_data = b"team_name,avg_overall_rating\nIncomplete FC,70\n"

    response = client.post(
        "/predict-csv",
        files={"file": ("incomplete.csv", csv_data, "text/csv")},
    )

    assert response.status_code == 422
    assert "Missing required columns" in response.json()["detail"]
    assert "avg_potential" in response.json()["detail"]


def test_known_historical_team_consistency() -> None:
    # KV Mechelen, 2010/2011 from team_season_features_eda.csv.
    payload = {
        "team_name": "KV Mechelen",
        "avg_overall_rating": 65.23131313131313,
        "avg_potential": 70.08316498316498,
        "goalkeeper_rating": 68.94814814814815,
        "avg_pace": 66.87764060356653,
        "avg_physical": 66.28199588477366,
        "avg_defence": 53.43045267489712,
        "avg_attack": 54.28960905349794,
        "buildUpPlaySpeed": 65.37037037037037,
        "buildUpPlayPassing": 59.44444444444444,
        "chanceCreationPassing": 49.44444444444444,
        "chanceCreationCrossing": 41.2962962962963,
        "chanceCreationShooting": 50.370370370370374,
        "defencePressure": 57.77777777777778,
        "defenceAggression": 68.33333333333333,
        "defenceTeamWidth": 57.77777777777778,
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["cluster"] == 1
    assert result["team_profile"] == "High-Pressure Wide Play"
    assert result["distance_to_centroid"] == 3.446


def test_frontend_and_download_assets() -> None:
    homepage = client.get("/")
    stylesheet = client.get("/static/style.css")
    script = client.get("/static/app.js")
    example = client.get("/example-csv")
    docs = client.get("/docs")

    assert homepage.status_code == 200
    assert "Football Team Performance Profiler" in homepage.text
    assert stylesheet.status_code == 200
    assert script.status_code == 200
    assert example.status_code == 200
    assert "avg_overall_rating" in example.text
    assert docs.status_code == 200
