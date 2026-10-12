"""Generate the engineered supervised dataset dictionary from actual columns."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENGINEERED_PATH = PROJECT_ROOT / "data/processed/model_data_engineered.csv"
PROCESSED_PATH = PROJECT_ROOT / "data/processed/train_processed.csv"
OUTPUT_PATH = PROJECT_ROOT / "docs/model_data_dictionary.csv"

TACTICAL_FEATURES = {
    "buildUpPlaySpeed": "build-up play speed",
    "buildUpPlayPassing": "build-up passing tendency",
    "buildUpPlayDribblingClass": "build-up dribbling class",
    "buildUpPlayPositioningClass": "build-up positioning class",
    "chanceCreationPassing": "chance-creation passing tendency",
    "chanceCreationCrossing": "chance-creation crossing tendency",
    "chanceCreationShooting": "chance-creation shooting tendency",
    "chanceCreationPositioningClass": "chance-creation positioning class",
    "defencePressure": "defensive pressure tendency",
    "defenceAggression": "defensive aggression tendency",
    "defenceTeamWidth": "defensive team-width tendency",
    "defenceDefenderLineClass": "defensive line class",
}
SQUAD_FEATURES = {
    "avg_overall_rating": "mean historical overall rating of listed players",
    "avg_potential": "mean historical potential of listed players",
    "goalkeeper_rating": "maximum historical goalkeeper composite in the lineup",
    "avg_attack": "mean historical attacking composite of outfield players",
    "avg_passing": "mean historical passing composite of outfield players",
    "avg_technical": "mean historical technical composite of outfield players",
    "avg_pace": "mean historical pace composite of outfield players",
    "avg_physical": "mean historical physical composite of outfield players",
    "avg_defence": "mean historical defensive composite of outfield players",
}
FORM_FEATURES = {
    "form_points_5": "points collected in the previous five matches",
    "avg_goals_scored_5": "mean goals scored in the previous five matches",
    "avg_goals_conceded_5": "mean goals conceded in the previous five matches",
}


def is_used(column: str, processed_columns: set[str]) -> bool:
    if column in processed_columns:
        return True
    if column == "season" and "season_start_year" in processed_columns:
        return True
    return any(name.startswith(f"{column}_") for name in processed_columns)


def describe(column: str) -> tuple[str, str, str, str]:
    """Return source/derived, description, formula/logic, leakage status."""
    if column == "target":
        return (
            "Derived from Match",
            "Three-class match outcome label.",
            "Home Win if home goals > away goals; Draw if equal; otherwise Away Win.",
            "Outcome label only; never included among predictors.",
        )
    if column in {"home_team_goal", "away_team_goal"}:
        side = "home" if column.startswith("home") else "away"
        return (
            "Match",
            f"Final goals scored by the {side} team.",
            "Recorded final score.",
            "Excluded: post-match leakage and used to derive target.",
        )
    if column.endswith("_diff"):
        base = column.removesuffix("_diff")
        special = {
            "overall_rating": "avg_overall_rating",
            "potential": "avg_potential",
            "attack": "avg_attack",
            "passing": "avg_passing",
            "technical": "avg_technical",
            "pace": "avg_pace",
            "physical": "avg_physical",
            "defence": "avg_defence",
            "goalkeeper": "goalkeeper_rating",
            "form_points": "form_points_5",
            "recent_goals_scored": "avg_goals_scored_5",
            "recent_goals_conceded": "avg_goals_conceded_5",
        }
        paired = special.get(base, base)
        return (
            "Derived",
            f"Home-minus-away difference for {paired.replace('_', ' ')}.",
            f"home_{paired} - away_{paired}",
            "Allowed: derived only from pre-match historical inputs.",
        )
    for side in ("home", "away"):
        prefix = f"{side}_"
        if column.startswith(prefix):
            base = column[len(prefix):]
            if base in TACTICAL_FEATURES:
                return (
                    "Team_Attributes historical join",
                    f"Latest available {TACTICAL_FEATURES[base]} for the {side} team.",
                    "Backward date join using the latest snapshot on or before match date.",
                    "Allowed; same-calendar-date timing is a documented limitation.",
                )
            if base in FORM_FEATURES:
                return (
                    "Derived from prior Match rows",
                    f"{FORM_FEATURES[base].capitalize()} for the {side} team.",
                    "Five-match rolling statistic after shift(1).",
                    "Allowed: current match is excluded by shift(1).",
                )
            if base in SQUAD_FEATURES:
                return (
                    "Player_Attributes historical join",
                    f"{SQUAD_FEATURES[base].capitalize()} for the {side} lineup.",
                    "Backward player/date joins followed by lineup aggregation.",
                    "Allowed; same-calendar-date timing is a documented limitation.",
                )
            if base == "players_listed":
                return (
                    "Derived from Match lineup IDs",
                    f"Count of listed {side} players.",
                    "Non-missing player IDs among 11 lineup slots.",
                    "Excluded after redundancy audit (>0.96 correlation with rated-player count).",
                )
            if base == "players_with_attributes":
                return (
                    "Derived from historical Player_Attributes coverage",
                    f"Count of {side} lineup players with a historical rating.",
                    "Count after backward player/date join.",
                    "Allowed; describes pre-match source coverage.",
                )
            if base.startswith("player_X") or base.startswith("player_Y"):
                return (
                    "Match",
                    f"Raw recorded {base[-2:]} formation coordinate for a {side} player slot.",
                    "Source formation coordinate.",
                    "Excluded: raw coordinates are outside the selected methodology.",
                )
            if base.startswith("player_") and base.removeprefix("player_").isdigit():
                return (
                    "Match",
                    f"Player API identifier in a {side} lineup slot.",
                    "Source foreign key.",
                    "Excluded: high-cardinality identity; replaced by historical aggregates.",
                )
            if base == "team_attr_date":
                return (
                    "Derived join metadata",
                    f"Date of the tactical snapshot selected for the {side} team.",
                    "Latest Team_Attributes date on or before match date.",
                    "Excluded: audit metadata, not a strength predictor.",
                )

    core = {
        "id": ("Match", "Internal match row identifier.", "Source primary key", "Excluded identifier."),
        "match_api_id": ("Match", "External match API identifier.", "Source identifier", "Excluded identifier."),
        "country_id": ("Match", "Country foreign key.", "Source identifier", "Excluded identifier."),
        "league_id": ("Match", "League foreign key.", "Source identifier", "Excluded identifier; readable league is encoded."),
        "home_team_api_id": ("Match", "Home-team foreign key.", "Source identifier", "Excluded identifier."),
        "away_team_api_id": ("Match", "Away-team foreign key.", "Source identifier", "Excluded identifier."),
        "season": ("Match", "Competition season label.", "Source season; converted to start year", "Allowed and converted to season_start_year."),
        "stage": ("Match", "League round/stage number.", "Source pre-match schedule field", "Allowed pre-match field."),
        "date": ("Match", "Calendar date of the fixture.", "Source timestamp", "Excluded metadata; season captures time trend."),
        "country_name": ("Country/League lookup", "Country name for the league.", "Lookup by country_id", "Excluded metadata."),
        "league_name": ("League lookup", "Competition name.", "Lookup by league_id and one-hot encoding", "Allowed categorical context."),
        "home_team_name": ("Team lookup", "Readable home-team name.", "Lookup by home_team_api_id", "Excluded metadata/identity."),
        "away_team_name": ("Team lookup", "Readable away-team name.", "Lookup by away_team_api_id", "Excluded metadata/identity."),
    }
    if column in core:
        return core[column]
    return (
        "Engineered workflow",
        column.replace("_", " ").capitalize() + ".",
        "See supervised Notebook 01 for the recorded transformation.",
        "Allowed only if represented in the final processed feature schema.",
    )


def main() -> None:
    engineered = pd.read_csv(ENGINEERED_PATH, low_memory=False)
    processed_columns = set(pd.read_csv(PROCESSED_PATH, nrows=0).columns) - {"target"}
    rows = []
    for column in engineered.columns:
        source, description, formula, leakage = describe(column)
        used = is_used(column, processed_columns) and column != "target"
        rows.append(
            {
                "column": column,
                "type": str(engineered[column].dtype),
                "source_or_derived": source,
                "description": description,
                "formula_or_logic": formula,
                "used_for_modelling": used,
                "leakage_status_or_exclusion_reason": leakage,
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
