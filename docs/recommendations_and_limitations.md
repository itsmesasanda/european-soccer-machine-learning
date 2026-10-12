# Recommendations and Limitations

## Recommendations

1. **Use the supervised model as a benchmark, not an oracle.** Macro F1 `0.4410` shows useful structure but substantial uncertainty. Present the full class-level report alongside accuracy.
2. **Keep Draw performance visible.** Draw F1 is `0.3110`; operational summaries that show only overall accuracy would conceal this weakness.
3. **Prioritize relative team strength.** Overall, potential, attack, passing, defence and related home-minus-away differences are consistently informative and interpretable.
4. **Retain chronological evaluation.** Any extension should train on earlier periods and validate on later ones. Random shuffled cross-validation would overstate real forecasting conditions.
5. **Use profiles for comparative analysis.** The five K-Means archetypes are useful for summarizing squad/tactical tendencies, representative teams, performance context and transitions across seasons.
6. **Interpret centroid distance correctly.** Smaller distance means the standardized team characteristics are closer to a historical cluster centre. It is not probability, likelihood or confidence.
7. **Review boundary cases comparatively.** The median nearest/second-nearest distance margin is `0.6697`; 103 rows in the bottom margin decile form a transparent review group, not a class of objectively uncertain teams.
8. **Monitor drift before current use.** The data ends in 2016; ratings, tactics, leagues and competitive patterns may have changed.

## Supervised limitations

- Football outcomes contain irreducible randomness, injuries, tactical choices and match-day events absent from this dataset.
- Draws are difficult to separate from home/away wins using the available pre-match variables.
- The source provides dates rather than kickoff/snapshot times. Same-calendar-date historical joins may occasionally use a record updated after kickoff.
- Player/date duplicate handling preserves the existing `keep="last"` rule, including a small number of questionable blank duplicates.
- Coverage filters exclude matches without sufficient tactical history, five-match form, or rated lineup players; results therefore apply to the retained sample.
- Betting odds are intentionally excluded. This improves methodological focus but removes a powerful market benchmark.
- Feature importance is model-specific and predictive, not causal.
- The final test covers one season, so it cannot measure performance under every possible temporal shift.

## Unsupervised limitations

- K-Means assumes spherical groups in standardized Euclidean space.
- The silhouette score is low (`0.1003`), showing that the team archetypes overlap substantially.
- Seven PCA components retain only 75.9% of variance. Their higher native-space silhouette is not a like-for-like improvement over all 15 dimensions; rescoring the PCA labels in the original space produces `0.1007`.
- Plain and PCA-reduced DBSCAN searches found a giant assigned cluster above 99% plus a microcluster, so density-based separation is not useful in the searched spaces.
- The chosen five-cluster solution is a useful analytical segmentation, not proof of five objectively real types.
- The bottom-decile ambiguity group is distribution-relative and has no validated football-domain cutoff. Margins and ratios are not calibrated uncertainty.
- Profile labels are interpretations of standardized centroids and depend on the selected 15 variables.
- Team-season averages hide within-season changes, individual matches and tactical adaptation.
- Profile performance summaries are descriptive associations and must not be interpreted as causal effects.

## Stakeholder caution

Neither task should be used for high-stakes automated decisions. Analysts should combine these outputs with current team news, domain expertise, and uncertainty-aware reporting.
