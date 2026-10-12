# Preprocessing and Feature Log

## Supervised feature engineering

| Feature group | Logic | Temporal/leakage control |
|---|---|---|
| Target | Home Win if home goals exceed away goals; Draw if equal; otherwise Away Win | Goals used only for label and excluded from predictors |
| Team tactics | Latest home/away `Team_Attributes` snapshot | Backward join on or before match date |
| Recent form | Previous-five-match points, goals scored and goals conceded | `shift(1)` before rolling calculation excludes current match |
| Player strength | Latest historical player rating; lineup-level averages for overall, potential, attack, passing, technical, pace, physical and defence; maximum goalkeeper composite | Backward player/date join; future records asserted absent |
| Relative strength | Home value minus away value for ratings, form and tactics | Derived entirely from allowed historical variables |

Important formulas include:

```text
overall_rating_diff = home_avg_overall_rating - away_avg_overall_rating
form_points_diff = home_form_points_5 - away_form_points_5
attack_diff = home_avg_attack - away_avg_attack
defence_diff = home_avg_defence - away_avg_defence
passing_diff = home_avg_passing - away_avg_passing
```

All engineered definitions and exclusions are enumerated in `model_data_dictionary.csv`.

## Conceptual exclusions

- Betting odds: excluded by project scope.
- Goals and event XML: post-match leakage.
- Match/team/player IDs and readable team names: identity/traceability rather than continuous strength.
- Raw player IDs and formation coordinates: high-cardinality/raw representation outside the chosen methodology.
- Historical snapshot dates: used to enforce temporal joins, not as strength variables.

## Coverage filtering

- Select modelling seasons 2010/11–2015/16.
- Require both teams to have a historical tactical snapshot.
- Require five previous matches for all form variables.
- Require at least eight lineup players with historical attributes for each side.

This produces 17,609 unique matches and 75 complete candidate predictors.

## Chronological preprocessing

| Split | Seasons | Rows |
|---|---|---:|
| Training | 2010/11–2013/14 | 11,413 |
| Validation | 2014/15 | 3,067 |
| Test | 2015/16 | 3,129 |

- Season is converted to numeric start year.
- Categorical levels are learned from training data and one-hot encoded with unknown validation/test categories ignored.
- Output columns are aligned across all splits.
- Two near-duplicate lineup-count variables are removed after a training-data correlation audit.
- The resulting files contain 80 numeric predictors plus target and no missing or infinite predictor values.

## Feature selection

- Variance audit: no constant processed predictors.
- Correlation audit: removes only the two near-duplicate lineup counts; football rating variables remain available for model-based evaluation.
- Mutual Information and Random Forest importance: training-only rankings.
- Feature-count experiment: Top 10/20/30/40 versus all features on validation.
- Final-model check: Gradient Boosting Top 40 (`0.4570` Macro F1) versus all 80 (`0.4545`). Top 40 is retained.

## Class imbalance

Class treatment is evaluated by model rather than assumed beneficial. Balanced Random Forest does not improve Macro F1. For Gradient Boosting on Top 40, balanced sample weights improve validation Macro F1 from `0.3806` to `0.4570` and Draw F1 from `0.0264` to `0.3020`, so that treatment is retained for tuning and final fitting.

## Known preprocessing limitations

- Source snapshots have dates but not times; a same-calendar-date record may have been updated after kickoff.
- Duplicate player/date rows use the preserved `keep="last"` rule; some duplicate groups contain blank records.
- Minimum-coverage filtering changes the population toward matches with better historical data coverage.
