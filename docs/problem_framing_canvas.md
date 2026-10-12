# Problem Framing Canvas

## Business problem

Football analysts need evidence-based ways to summarize historical team strength and assess likely match outcomes without treating uncertain sport results as deterministic. This project uses the European Soccer Database to answer two related questions:

1. **Primary supervised question:** given information available before kickoff, can a model distinguish Home Win, Draw, and Away Win outcomes?
2. **Secondary unsupervised question:** can team-season squad and tactical characteristics be organized into interpretable historical archetypes?

## Decision lens

| Lens | Definition |
|---|---|
| Primary metric | Macro F1, because each outcome class has equal importance and Draw is less frequent/harder to identify |
| Secondary metrics | Accuracy, weighted F1, and precision/recall/F1 for each outcome |
| Validation design | Chronological holdout: train 2010/11–2013/14, validate 2014/15, test 2015/16 |
| Model-selection rule | Choose features, method, imbalance treatment, and hyperparameters using training plus validation logic only |
| Final evidence | Evaluate the locked model once on 2015/16; do not compare alternatives on test |
| Clustering lens | Prefer separation metrics, stability/interpretability evidence, and useful profiles; do not present cluster assignment as certainty |

## Unit of analysis

- **Supervised:** one played league match, with the target defined by the final home/away score and predictors constructed from pre-match history.
- **Unsupervised:** one team in one season after minimum match-coverage filtering.

## Stakeholders and value

- Analysts can use the supervised work as a transparent historical benchmark and inspect which relative-strength variables are informative.
- Coaches and performance staff can use team profiles to compare squad/tactical archetypes and review profile changes across seasons.
- Students and assessors can trace each decision from source-table quality through final evaluation using notebooks, generated tables, and the decision log.

## Scope boundaries

- The supervised model is not an automated betting system and does not claim reliable certainty for an individual fixture.
- Betting odds are excluded so the model reflects engineered football information rather than market consensus.
- Post-match events, goals, and future records are excluded from predictors.
- The browser demo performs **team-profile assignment**, not future match prediction.
- Results apply to the represented European leagues and historical period; they are not assumed to transfer unchanged to current football.

## Evidence of success

- Reproducible chronological workflow with no test-driven selection.
- Final generated supervised metrics and class-level report.
- Completed K-Means/Hierarchical/GMM comparison, PCA/DBSCAN sensitivity analysis, and interpretable profile-overlap evidence.
- Exact browser/Python parity for the deployed K-Means pipeline.
- Honest limitations, especially difficult Draw prediction and overlapping clusters.
