# European Soccer Machine Learning

An end-to-end university machine-learning project built from the European Soccer Database. It addresses two related questions:

1. Can a match outcome—Home Win, Draw, or Away Win—be estimated from information available before kick-off?
2. Can European club-seasons be grouped into interpretable performance archetypes for benchmarking?

The repository contains a chronological supervised-learning workflow, an unsupervised team-profiling workflow, reproducible evidence outputs, and a browser-only static demonstration. The final deliverable is an analytical prototype, not a betting system or a guarantee of future performance.

## Dataset and provenance

The source is the [European Soccer Database on Kaggle](https://www.kaggle.com/datasets/hugomathien/soccer), covering match, league, team, team-attribute, player, and player-attribute records. The submitted workbook is expected at:

```text
data/raw/european_soccer_database.xlsx
```

Its SHA-256 checksum is:

```text
9288748def6d4dab386c3d9dc74f79485ccfde5fa4a2a70a5ed010ebe78695db
```

Raw, extracted, and processed datasets are intentionally gitignored because of their size; report-ready figures and result tables remain in the repository. Full source details, extracted-table checksums, and processing notes are in [docs/data_provenance.md](docs/data_provenance.md). The generated [model data dictionary](docs/model_data_dictionary.csv) records all 156 engineered columns, their derivation, modelling use, and leakage status.

## Methods

### Supervised match-outcome modelling

- Unit of analysis: one match.
- Training: seasons 2010/11–2013/14.
- Validation and all model decisions: season 2014/15.
- Locked final test: season 2015/16, evaluated once after the feature set, imbalance treatment, model family, and hyperparameters were fixed.
- Inputs: historical player-strength aggregates, team tactical attributes, prior-five-match form, league, season, and match stage.
- Leakage control: final scores, event fields, identifiers, and current-match outcomes are excluded from predictors; rolling form uses `shift(1)`.

Gradient Boosting was selected after baseline and candidate-model comparisons. For that model, the Top-40 feature set marginally exceeded all 80 valid processed features on validation Macro F1 (0.4570 versus 0.4545). Balanced sample weights materially improved minority-class behaviour for Gradient Boosting, although the same treatment did not improve Random Forest—so imbalance handling is documented as model-specific.

A deterministic `ParameterSampler` search evaluated 20 configurations by repeatedly fitting on training seasons and scoring only on the 2014/15 holdout. The locked configuration used 250 estimators, learning rate 0.05, depth 2, minimum leaf size 5, subsample 1.0, and random state 42.

Final 2015/16 test results:

| Metric | Value |
|---|---:|
| Accuracy | 0.4545 |
| Macro F1 | 0.4410 |
| Weighted F1 | 0.4618 |
| Home Win F1 | 0.5477 |
| Draw F1 | 0.3110 |
| Away Win F1 | 0.4644 |

The draw class remains the hardest outcome. This is a central limitation, not a hidden failure. Exact results are saved in [final_supervised_test_metrics.csv](outputs/tables/final_supervised_test_metrics.csv), [final_supervised_classification_report.csv](outputs/tables/final_supervised_classification_report.csv), and [final_supervised_model_config.csv](outputs/tables/final_supervised_model_config.csv).

### Unsupervised team profiling

- Unit of analysis: one club in one season.
- Candidate methods: K-Means, agglomerative clustering, Gaussian mixture modelling, PCA + K-Means, DBSCAN, and a limited PCA + DBSCAN sensitivity check.
- Final method: standardized K-Means with five clusters, selected for its comparative metrics, interpretability, reproducibility, and deployment suitability.
- Final K-Means metrics: silhouette 0.1003, Davies–Bouldin 2.1681, and Calinski–Harabasz 107.8473.

Seven-component PCA retained 75.9% of variance. Its five-cluster K-Means candidate scored 0.1443 silhouette in the reduced space and closely reproduced the current assignments (adjusted Rand index 0.9304), but its silhouette was only 0.1007 when those labels were assessed in the original 15-feature space. Both DBSCAN searches produced one giant cluster plus a very small group, so neither supplied usable football archetypes.

The low full-space silhouette score indicates overlapping rather than sharply separated team archetypes. Cluster assignment is therefore a descriptive benchmarking aid. Distance to a centroid, its margin, and its nearest/second-nearest ratio are geometric separation measures—not probability or confidence. The complete sensitivity analysis is in [Notebook 04](notebooks/unsupervised/04_clustering_overlap_and_alternatives.ipynb) and [extended_clustering_model_comparison.csv](outputs/team_profiling/tables/extended_clustering_model_comparison.csv).

The public [Football Team Performance Profiler](https://huggingface.co/spaces/itsemesasanda/football-team-profiler) reproduces the saved scaler and K-Means assignment entirely in browser-side JavaScript. It profiles historical club-season inputs; it does not predict future matches. Python-to-JavaScript parity is covered by `scripts/validate_static_space.py`.

## Notebook order

Run the notebooks in this order:

```text
notebooks/supervised/
  01_data_inspection_and_feature_engineering.ipynb
  02_exploratory_data_analysis.ipynb
  03_data_cleaning_and_preprocessing.ipynb
  04_feature_selection_and_baseline_modeling.ipynb
  05_final_model_fitting_and_evaluation.ipynb

notebooks/unsupervised/
  01_team_performance_profiling.ipynb
  02_team_performance_eda.ipynb
  03_team_performance_clustering.ipynb
  04_clustering_overlap_and_alternatives.ipynb
```

The two workflows share source data but answer different questions. Complete the supervised sequence before the unsupervised sequence when reproducing the whole project.

## Reproduce the project

The final workflow was executed with Python 3.9.6. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python src/excel_to_csv.py
python scripts/run_notebooks.py
python scripts/generate_data_dictionary.py
python scripts/validate_static_space.py
node --check static_space/app.js
```

`src/excel_to_csv.py` is only needed when `data/extracted/*.csv` is absent. The notebook runner executes each notebook in a fresh kernel and records pass/fail status in [notebook_execution_status.csv](outputs/tables/notebook_execution_status.csv). It stops at the first failure.

To inspect the static application locally:

```bash
python -m http.server 8000 --directory static_space
```

Then open `http://localhost:8000`.

## Repository structure

```text
data/                 raw workbook plus extracted and processed data
docs/                 assignment evidence, audit, provenance, and dictionary
models/team_profiling saved scaler, K-Means model, features, and profile names
notebooks/supervised  chronological match-outcome workflow
notebooks/unsupervised club-season profiling workflow
outputs/              generated figures and machine-readable result tables
scripts/              execution, documentation, and deployment validation tools
src/                  source-workbook conversion utility
static_space/         self-contained Hugging Face Static Space
```

## Evidence and limitations

The finalization audit and assignment evidence are indexed in [docs/PROJECT_FINALIZATION_AUDIT.md](docs/PROJECT_FINALIZATION_AUDIT.md). Key supporting documents include the [problem framing canvas](docs/problem_framing_canvas.md), [workflow](docs/workflow.md), [decision log](docs/decision_log.md), [model comparison](docs/model_method_comparison.md), and [recommendations and limitations](docs/recommendations_and_limitations.md).

Important limitations include dataset age, imperfect source completeness, same-calendar-date ambiguity in historical attribute snapshots, residual class imbalance, low draw recall, moderate chronological generalization, and overlapping team clusters. The results should support analysis and discussion, not automated sporting or financial decisions.

AI assistance was used for code review, restructuring, documentation, reproducibility checks, and deployment validation. Project claims remain tied to executable notebooks and generated artifacts; no fabricated experiment results or member-specific contribution claims were added. See [docs/ai_use_statement.md](docs/ai_use_statement.md). Group members must review and sign the [member contribution map](docs/member_contribution_map.md) before submission.
