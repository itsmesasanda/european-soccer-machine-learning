# Project Workflow

## End-to-end flow

```text
European Soccer source workbook
        │
        ├─ export seven relational CSV tables
        │
        ├─ supervised: one row per match
        │      ├─ historical tactical snapshots
        │      ├─ previous-five-match form
        │      ├─ historical lineup strength
        │      ├─ home-minus-away differences
        │      ├─ chronological preprocessing
        │      ├─ feature/baseline evidence
        │      ├─ train/validation feature-set + method comparison
        │      ├─ 20-configuration validation tuning
        │      └─ one locked 2015/16 test evaluation
        │
        └─ unsupervised: one row per team-season
               ├─ coverage filtering and aggregation
               ├─ EDA/redundancy-based feature selection
               ├─ StandardScaler
               ├─ K-Means / Hierarchical / GMM comparison
               ├─ profiles, representatives, performance and transitions
               └─ PCA / DBSCAN sensitivity and assignment-overlap analysis
```

## Notebook execution order

| Order | Notebook | Primary input | Main output |
|---:|---|---|---|
| 1 | `supervised/01_data_inspection_and_feature_engineering.ipynb` | Seven extracted source tables | `model_data_engineered.csv`, retention and dataset summary tables |
| 2 | `supervised/02_exploratory_data_analysis.ipynb` | Source tables and engineered data | Source/final-data EDA figures and tables |
| 3 | `supervised/03_data_cleaning_and_preprocessing.ipynb` | Engineered matches | Chronological train, validation, and test processed CSVs |
| 4 | `supervised/04_feature_selection_and_baseline_modeling.ipynb` | Training and validation only | Feature rankings, Top-40 list, baseline and imbalance comparisons |
| 5 | `supervised/05_final_model_fitting_and_evaluation.ipynb` | Training/validation first; test only after lock | Tuning results and final supervised test outputs |
| 6 | `unsupervised/01_team_performance_profiling.ipynb` | Engineered matches | Team-season feature table |
| 7 | `unsupervised/02_team_performance_eda.ipynb` | Team-season table | Final clustering features and EDA outputs |
| 8 | `unsupervised/03_team_performance_clustering.ipynb` | Scaled clustering feature matrix | Model comparison, profiles, transitions, and saved K-Means artifacts |
| 9 | `unsupervised/04_clustering_overlap_and_alternatives.ipynb` | Existing team-season data and protected K-Means artifacts | PCA/DBSCAN experiments, ambiguity evidence, and extended comparison |

Run all notebooks with:

```bash
python scripts/run_notebooks.py
```

The generated execution record is `outputs/tables/notebook_execution_status.csv`.

## Leakage control gates

1. Final score creates the label but is excluded from predictors.
2. Match-event XML fields are excluded because they occur during/after the fixture.
3. Team and player attributes use backward date joins.
4. Recent form uses `shift(1)` before the five-match rolling calculation.
5. Preprocessing schema is learned from training and reused for validation/test.
6. Notebook 04 never loads the test file.
7. Notebook 05 loads the test file only after feature set, model family, imbalance treatment, and hyperparameters are locked.

## Deployment flow

The final public demo is `static_space/`. Saved StandardScaler and K-Means parameters are exported to JSON once; vanilla JavaScript reproduces feature derivation, scaling, Euclidean centroid distance, and cluster assignment entirely in the browser. CSV files do not leave the user's browser.
