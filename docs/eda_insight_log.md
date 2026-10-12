# EDA Insight Log

## Source-table evidence

| Area | Evidence | Modelling implication |
|---|---|---|
| Unit of analysis | `Match` has 25,979 rows; one row is one fixture | Preserve one unique match ID per supervised observation |
| Target balance | Raw matches: Home Win 45.87%, Draw 25.39%, Away Win 28.74% | Use Macro F1 as primary; inspect every class |
| Goals/home advantage | Home wins are the largest class and goal distributions differ by venue | Retain home/away orientation and difference features |
| Leagues/seasons | Eleven leagues and eight raw seasons have different match counts, scoring and outcome shares | Retain league context; split chronologically rather than randomly |
| Team | 299 rows, no duplicate team IDs, 11 missing FIFA IDs, three repeated names | Join by `team_api_id`, not name or FIFA ID |
| Team_Attributes | Repeated team rows are dated tactical snapshots; coverage is incomplete before 2010 | Use backward date joins and document coverage filtering |
| Player | 11,060 rows; names are not unique identifiers | Join by `player_api_id` |
| Player_Attributes | 183,978 dated rating rows with correlated skill groups and patterned missingness | Aggregate historical skill groups; avoid treating repeated rows as duplicates |
| Relationship structure | Match links leagues, two teams and up to 22 player IDs | Build historical joins separately for home/away and validate key coverage |

## Final engineered modelling dataset

The generated final audit reports:

- 17,609 usable matches from six seasons and eleven leagues.
- 75 candidate features before encoding: 65 numeric and 10 categorical.
- Zero missing candidate values and zero duplicate match IDs.
- Home Win 45.58%, Draw 25.31%, Away Win 29.12%.
- 11,413 training rows, 3,067 validation rows, and 3,129 test rows after chronological splitting.

### Data retention

| Stage | Matches retained | Removed at stage | Raw retained |
|---|---:|---:|---:|
| Raw Match table | 25,979 | 0 | 100.00% |
| Keep 2010/11–2015/16 | 19,423 | 6,556 | 74.76% |
| Require historical team attributes | 18,268 | 1,155 | 70.32% |
| Require previous-five-match form | 18,016 | 252 | 69.35% |
| Require at least eight rated players per side | 17,609 | 407 | 67.78% |

The report-quality figure is `outputs/figures/data_retention.png` and its generated source table is `outputs/tables/data_retention.csv`.

## Engineered-feature insights

Only training plus validation seasons are used for feature/outcome EDA. The 2015/16 test outcomes are excluded.

- `overall_rating_diff`, attack, defence, and passing differences shift toward positive values for Home Wins and negative values for Away Wins; Draws are more concentrated around balanced strength.
- `form_points_diff` adds a short-term historical signal that is conceptually different from player ratings.
- Squad-strength difference variables are strongly correlated. This supports formal redundancy/feature-selection checks, not arbitrary EDA deletion.
- Relative-strength features rank highly in both Mutual Information and Random Forest importance evidence.
- Home Wins remain the largest development class, and Draw remains the difficult class that motivates Macro F1 and model-specific balancing.

Generated evidence:

- `engineered_features_by_outcome.png`
- `engineered_feature_correlation.png`
- `engineered_target_distribution.png`
- `engineered_feature_target_summary.csv`
- `engineered_feature_correlations.csv`

## Unsupervised EDA insights

- The final table contains 1,028 team-season observations across eleven leagues and six seasons.
- Squad quality, pace, physical, defence, tactics, and derived balance features contain meaningful correlation/redundancy, leading to a 15-feature final clustering representation.
- Performance outcomes such as points per match are retained for interpreting profiles, not used to form the clusters.
- Cluster overlap is substantial; the final K-Means silhouette score is only `0.1003`.
