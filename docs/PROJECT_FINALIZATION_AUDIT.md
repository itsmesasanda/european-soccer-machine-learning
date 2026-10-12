# Project Finalization Audit

**Audit started:** 2026-10-12  
**Scope:** repository cleanup, assignment-evidence audit, reproducibility, final supervised and unsupervised outputs, and static deployment verification.  
**Status:** initial pre-deletion audit. The completion record is appended after final execution.

## 1. Repository snapshot before cleanup

The following snapshot was taken before any file was deleted or moved.

```text
.
├── .dockerignore
├── .DS_Store
├── .gitignore
├── .pytest_cache/
├── .venv/                         # 491 MB local environment
├── Dockerfile
├── README.md                      # deployment-focused and incomplete for submission
├── data/
│   ├── extracted/                 # seven exported relational tables
│   ├── processed/                 # engineered, split, and team-season datasets
│   └── raw/                       # source workbook
├── gradio_space/                  # abandoned Gradio deployment attempt
├── huggingface_app/               # abandoned FastAPI/Docker deployment
├── models/team_profiling/         # final K-Means/scaler artifacts and mappings
├── notebooks/
│   ├── backups/                   # five *.original.ipynb backups
│   ├── main scope/                # five supervised notebooks
│   └── second scope/              # three unsupervised notebooks
├── outputs/
│   ├── figures/                   # supervised/source-EDA figures
│   ├── tables/                    # supervised/source-EDA tables
│   └── team_profiling/            # unsupervised figures and tables
├── pytest.ini                     # FastAPI-only test configuration
├── reports/                       # empty
├── requirements.txt
├── scripts/                       # empty
├── src/                           # mostly empty/obsolete early scripts
└── static_space/                  # final browser-only deployment
```

The detailed inventory contained 13 notebook files, 3 processed supervised CSVs, 3 team-profile CSVs, 4 final clustering artifacts, 33 top-level report tables/figures, and 25 team-profiling tables/figures. Git showed a pre-existing modified root `README.md`, untracked `gradio_space/`, and untracked `static_space/`.

## 2. Notebook inventory and disposition

| Current notebook | Cells | Execution state | Initial finding | Planned disposition |
|---|---:|---|---|---|
| `notebooks/main scope/data_inspection_and_feature_engineering.ipynb.ipynb` | 41 | Executed, no stored errors | Accidental double extension; current path logic is not safe from a nested notebook folder | Rename to supervised Notebook 01 and make root discovery robust |
| `notebooks/main scope/exploratory_data_analysis.ipynb` | 74 | Executed, no stored errors | Strong source-table EDA, but no concise final-engineered-dataset EDA/retention section | Move to supervised Notebook 02 and add only the missing evidence |
| `notebooks/main scope/data_cleaning_and_preprocessing.ipynb` | 38 | Executed, no stored errors | Chronological split is present; loading/transforming test predictors here is acceptable, but decisions must remain train/validation-only | Move to supervised Notebook 03 and strengthen leakage wording |
| `notebooks/main scope/feature_selection_and_baseline_modeling.ipynb` | 47 | Executed, no stored errors | Good baseline evidence; prose contains approximate hard-coded results and the Top-40 decision was made with Random Forest rather than the final Gradient Boosting | Move to supervised Notebook 04; retain defensible completed comparisons and generate decision tables |
| `notebooks/main scope/final_model_fitting.ipynb` | 31 | Executed, no stored errors | Imports/evaluates XGBoost, has no reproducible tuning stage, and fixes Top 40 before comparing final-model feature sets | Replace unfinished XGBoost section, add Top-40/all-feature comparison and chronological holdout tuning, then perform one locked test evaluation |
| `notebooks/second scope/team_performance_profiling.ipynb` | 20 | Executed, no stored errors | Useful team-season feature construction | Move to unsupervised Notebook 01 |
| `notebooks/second scope/team_performance_eda.ipynb` | 24 | Executed, no stored errors | Required selection/redundancy reasoning and exports are present | Move to unsupervised Notebook 02 |
| `notebooks/second scope/team_performance_clustering.ipynb` | 28 | Executed, no stored errors | K-Means/Hierarchical/GMM comparison is present; one source mention of “confidence” must be checked so centroid distance is never described that way | Move to unsupervised Notebook 03 and re-execute |

### Duplicate, obsolete, or failed notebooks

- `notebooks/backups/05_final_model_fitting.original.ipynb` is an empty, invalid JSON file.
- `notebooks/backups/feature_selection_and_baseline_modeling.original.ipynb` has only five cells and a stored `NameError` because `X_train` is undefined.
- The other three `*.original.ipynb` files are large superseded snapshots containing older structure, unexecuted cells, parent-relative paths, and—in one case—absolute `/Users/...` paths.
- All five backup notebooks are obsolete duplicates and are cleanup candidates after this audit exists.

## 3. Deployment and temporary-file audit

### Deployment folders

- `static_space/` is the final public deployment and must remain.
- `gradio_space/` is the failed/abandoned Gradio attempt and is not part of the final submission.
- `huggingface_app/`, `Dockerfile`, `.dockerignore`, and `pytest.ini` exist only for the abandoned FastAPI/Docker deployment. Their tests exercise that deployment rather than the ML workflow.

### Temporary/local files found

- `.venv/` (491 MB)
- `.pytest_cache/`
- Python `__pycache__/` directories under `gradio_space/`
- `.DS_Store` files at repository root and under `data/`, `notebooks/`, and `outputs/`
- notebook backup directory and accidental double-extension notebook

The existing `.gitignore` already ignores some of these, but it also ignores all raw, extracted, and processed data without documenting how to recreate them. It needs a submission-oriented update.

## 4. Generated outputs and trained artifacts

### Supervised/source-EDA outputs already present

- Source-table data-quality summaries, missingness tables, league/season summaries, and EDA figures.
- Mutual-information and Random-Forest importance tables.
- A Top-40 feature list and feature-count comparison.
- Validation comparison and earlier final-test metrics/classification report.

The existing final supervised filenames do not fully match the required submission contract. In particular, the repository lacks `gradient_boosting_tuning_results.csv`, a tuning-summary figure/table, weighted F1 in the final metrics, `final_supervised_model_config.csv`, and the required `final_supervised_*` output names.

### Unsupervised outputs already present

- K-Means/Hierarchical/GMM metric comparison.
- K-Means cluster-count evidence and GMM AIC/BIC figure.
- Final standardized centroids, defining features, representative teams by centroid distance, profile-performance summary, and longitudinal profile transitions.
- Saved StandardScaler, K-Means model, exact feature order, and profile-name mapping under `models/team_profiling/`.

The current clustering comparison reports a low K-Means silhouette score (`0.1003`), so overlap between archetypes must remain an explicit limitation.

## 5. Broken logic, paths, stale results, and duplication

- The final supervised notebook imports `XGBClassifier` and evaluates XGBoost. This is an unfinished optional dependency and is not needed for a defensible comparison.
- The final supervised notebook has no `ParameterSampler` tuning stage and therefore does not satisfy the requested chronological holdout tuning procedure.
- Top 40 versus all valid features has not been compared for the selected Gradient Boosting model.
- Several notebook markdown cells state approximate result values from an earlier run. Those values can become stale and must be replaced by generated outputs or synchronized during final execution.
- Current project-root discovery in several supervised notebooks handles only the project root or a direct `notebooks/` working directory. It will fail when notebooks live under `notebooks/supervised/`.
- `src/inspect_excel.py` treats the workbook path as a directory and calls `.glob("*.xlsx")` on it, so it cannot work as written.
- `src/data_preparation.py`, `src/evaluate_models.py`, `src/feature_engineering.py`, and `src/train_models.py` are empty placeholders. The substantive workflow is duplicated in notebooks instead.
- `outputs/figures/EDA/` and several figures directly under `outputs/figures/` represent overlapping EDA generations. Final execution must establish which set is current before stale duplicates are removed.
- No notebook currently references a nonexistent required input, but the new output names requested by the brief are not yet generated.

## 6. Data and leakage audit

- Raw `Match.csv` contains 25,979 matches and 115 columns.
- The current engineered supervised dataset contains 17,609 matches and 156 total columns before candidate filtering.
- Processed splits contain 80 predictors plus target: 11,413 training rows, 3,067 validation rows, and 3,129 test rows.
- Chronology is explicitly defined as training `2010/11–2013/14`, validation `2014/15`, and test `2015/16`.
- Obvious post-match fields (match goals and event XML fields) are not in the processed candidate set. Difference features are built from historical team/player/tactical attributes and recent form.
- The feature-engineering notebook documents historical joins, but the final evidence set still needs a compact retention table and an explicit machine-checkable statement that only pre-match information is used.
- The preprocessing notebook transforms all three splits with a common deterministic schema. Feature ranking/model selection is currently train/validation-only, but the final notebook loads `y_test` near the beginning. That creates avoidable audit ambiguity even though test predictions occur after the model assertion. The revised final notebook should isolate test evaluation after all feature, model, and tuning decisions are locked.
- Hyperparameter tuning must use training fits and the 2014/15 validation holdout only. Ordinary shuffled K-fold validation is inappropriate for this chronological design.

## 7. Missing assignment evidence at audit start

The repository does not yet contain the required standalone evidence documents:

- problem framing canvas
- workflow
- decision log
- EDA insight log
- preprocessing/feature log
- model/method comparison
- recommendations and limitations
- AI-use statement
- member contribution map
- model data dictionary

The root README is currently a short FastAPI deployment description. It does not describe the complete project, dataset provenance, both ML tasks, notebook order, final evidence, reproduction steps, limitations, static demo, or AI-use disclosure.

The EDA also lacks a single concise section covering the final engineered modelling dataset, including retention, final candidate missingness, duplicate IDs, feature types, target/league/season coverage, and selected engineered-feature distributions.

## 8. Initial assignment-evidence checklist

| Evidence area | Initial status | Location/action |
|---|---|---|
| Business problem and decision lens | Partial | Scattered notebook prose; create framing document |
| Unit of analysis and workflow | Partial | Notebook objectives; create workflow document |
| Decision log | Missing | Create evidence-based chronological log |
| Source EDA/data quality | Strong | Existing EDA notebook and tables |
| Final engineered-data EDA | Missing/partial | Add focused section and retention outputs |
| Preprocessing and feature engineering | Present but scattered | Consolidate in log/data dictionary |
| Leakage prevention | Present but needs explicit audit | Add checks and documentation |
| Feature selection | Present | Resolve final-model Top-40/all ambiguity |
| Class imbalance handling | Present | Balanced training sample weights |
| Model comparison | Present but includes unfinished XGBoost | Remove XGBoost and refresh comparison |
| Hyperparameter tuning | Missing | Add modest deterministic holdout search |
| Untouched final test | Partial | Re-run once after all choices are locked |
| Recommendation/limitations | Partial | Create evidence document; retain uncertainty and low silhouette limitations |
| Stakeholder value | Partial | Consolidate in framing/recommendations |
| Dataset/data dictionary | Missing | Create from actual pipeline columns |
| Reproducibility | Incomplete | Clean requirements, paths, README, and fresh execution |
| AI-use transparency | Missing | Create disclosure without inventing member-specific claims |

## 9. Safe cleanup decision

After this pre-deletion audit is saved, it is safe to remove the five backup notebooks, the abandoned Gradio and FastAPI/Docker deployment files, caches, `.DS_Store` files, the local virtual environment from the submission tree, empty obsolete source placeholders, and redundant stale outputs once their replacements are generated. The source workbook, extracted/processed data, report-quality outputs, clustering artifacts, and `static_space/` are protected.

---

## 10. Finalization completed

This section records the post-change state. Sections 1–9 intentionally remain as the before-change audit trail.

### Repository cleanup and structure

The following material was moved out of the submission tree only after the initial audit was written:

- failed `gradio_space/` deployment;
- abandoned `huggingface_app/`, `Dockerfile`, `.dockerignore`, and `pytest.ini` FastAPI/Docker/pytest path;
- five obsolete notebooks under `notebooks/backups/`, including one invalid zero-byte file and one failed partial notebook;
- legacy `notebooks/main scope/` and `notebooks/second scope/` folders after their maintained notebooks were placed in the standardized structure;
- local `.venv/`, `.pytest_cache/`, `__pycache__/`, and `.DS_Store` files;
- empty or broken source placeholders, retaining only the working workbook conversion utility;
- overlapping/stale EDA figures and superseded final-test outputs after their replacements were generated.

For recoverability during finalization, these items were staged at `/tmp/european-soccer-finalization-backup.1sFqyc`. That path is temporary operating-system storage and must not be treated as a durable project backup.

The final notebook structure is:

```text
notebooks/supervised/
├── 01_data_inspection_and_feature_engineering.ipynb
├── 02_exploratory_data_analysis.ipynb
├── 03_data_cleaning_and_preprocessing.ipynb
├── 04_feature_selection_and_baseline_modeling.ipynb
└── 05_final_model_fitting_and_evaluation.ipynb

notebooks/unsupervised/
├── 01_team_performance_profiling.ipynb
├── 02_team_performance_eda.ipynb
└── 03_team_performance_clustering.ipynb
```

Maintained notebooks were moved/renamed from the two legacy scope folders as follows:

| Previous path/name | Final path/name |
|---|---|
| `notebooks/main scope/data_inspection_and_feature_engineering.ipynb.ipynb` | `notebooks/supervised/01_data_inspection_and_feature_engineering.ipynb` |
| `notebooks/main scope/exploratory_data_analysis.ipynb` | `notebooks/supervised/02_exploratory_data_analysis.ipynb` |
| `notebooks/main scope/data_cleaning_and_preprocessing.ipynb` | `notebooks/supervised/03_data_cleaning_and_preprocessing.ipynb` |
| `notebooks/main scope/feature_selection_and_baseline_modeling.ipynb` | `notebooks/supervised/04_feature_selection_and_baseline_modeling.ipynb` |
| `notebooks/main scope/final_model_fitting.ipynb` | `notebooks/supervised/05_final_model_fitting_and_evaluation.ipynb` |
| `notebooks/second scope/team_performance_profiling.ipynb` | `notebooks/unsupervised/01_team_performance_profiling.ipynb` |
| `notebooks/second scope/team_performance_eda.ipynb` | `notebooks/unsupervised/02_team_performance_eda.ipynb` |
| `notebooks/second scope/team_performance_clustering.ipynb` | `notebooks/unsupervised/03_team_performance_clustering.ipynb` |

Notebook-specific changes are summarized here:

| Notebook | Finalization change |
|---|---|
| Supervised 01 | Robust paths, explicit retention stages, historical-coverage evidence, and generated retention table |
| Supervised 02 | Preserved source EDA; added engineered-dataset audit, target/feature/correlation analysis, and report outputs |
| Supervised 03 | Robust paths and clearer chronological fit/transform and leakage wording |
| Supervised 04 | Refreshed feature/scaling/baseline tables and added model-specific imbalance comparison |
| Supervised 05 | Removed unfinished optional experiment; added feature-set comparison, candidate comparison, deterministic holdout tuning, decision lock, and single final test section |
| Unsupervised 01 | Robust paths and reproducible team-season dataset generation |
| Unsupervised 02 | Preserved feature/redundancy evidence and reproducible final clustering-feature export |
| Unsupervised 03 | Re-executed method comparison and clarified distance/concentration language and overlapping-cluster limitation |

### Supervised workflow completion

- Project-root discovery was made robust to execution from the repository root or either nested notebook directory.
- The engineered-data EDA now records the complete retention path: 25,979 source matches, 19,423 in retained seasons, 18,268 with historical team attributes, 18,016 with five-match form, and 17,609 with rated-player coverage.
- The final engineered audit records 17,609 rows, 75 candidate features, no candidate missing values, no duplicate match identifiers, 11 leagues, and six seasons. It adds generated target, selected-feature, and correlation evidence.
- Source-leakage fields remain excluded. Prior-five-match form uses `shift(1)`, and feature/model/tuning decisions use training plus validation only.
- Baseline outputs now include scaling, model, feature-selection, and model-specific imbalance comparisons. Random Forest did not improve with balanced weights, while balanced Gradient Boosting improved validation Macro F1 from 0.3806 to 0.4570.
- The unfinished executable XGBoost experiment was removed; a short decision-log note retains the reason for excluding the optional dependency.
- The selected Gradient Boosting model was compared using the Top-40 feature set and all 80 valid processed features. Top 40 won on validation Macro F1: 0.4570 versus 0.4545.
- Candidate validation Macro F1 scores were 0.4570 for Gradient Boosting, 0.4524 for Histogram Gradient Boosting, 0.3922 for Linear SVM, and 0.3815 for Extra Trees.
- A deterministic 20-configuration `ParameterSampler` search fit only on 2010/11–2013/14 and scored only on 2014/15. The selected validation configuration achieved 0.4636 Macro F1 and 0.4813 accuracy.
- The locked configuration was then refit on combined training and validation seasons and evaluated once on 2015/16. Final test accuracy is 0.4545, Macro F1 is 0.4410, and weighted F1 is 0.4618. Class F1 scores are 0.5477 for Home Win, 0.3110 for Draw, and 0.4644 for Away Win.
- Required result contracts now exist as `final_supervised_test_metrics.csv`, `final_supervised_classification_report.csv`, `final_supervised_model_config.csv`, `gradient_boosting_tuning_results.csv`, `gradient_boosting_tuning_summary.csv`, and corresponding report-quality figures.

### Unsupervised workflow and static deployment completion

- K-Means, hierarchical clustering, and Gaussian mixture modelling remain compared in one generated table.
- Five-cluster K-Means remains the final method, with silhouette 0.1003, Davies–Bouldin 2.1681, and Calinski–Harabasz 107.8473.
- Low cluster separation is explicitly retained as a limitation. K-Means centroid distance is described only as geometric similarity; Gaussian-mixture output is described as posterior membership concentration rather than generic confidence.
- The final scaler, K-Means model, exact feature order, profile names, centroids, representative teams, transition summaries, and cluster interpretations are present.
- `static_space/` is the only deployment. It is self-contained and browser-only, and it is described as historical profile assignment—not future-match prediction.
- The Python-to-JavaScript parity check covered 20 historical rows with zero cluster mismatches, zero rounded-distance mismatches, six CSV validation cases, and no scikit-learn feature-name warnings. JavaScript syntax checks also passed.

## 11. Fresh execution and static validation

All eight maintained notebooks were executed in order with a new kernel per notebook using Python 3.9.6 and the dependency versions pinned in `requirements.txt`. The machine-readable status file is `outputs/tables/notebook_execution_status.csv`; every row reports `passed`:

| Notebook group | Passed | Stored execution errors after run |
|---|---:|---:|
| Supervised | 5/5 | 0 |
| Unsupervised | 3/3 | 0 |
| Total | 8/8 | 0 |

Additional checks completed:

- every maintained notebook is valid JSON;
- every code cell compiles;
- no maintained notebook source or stored output contains absolute `/Users/...` paths, `%pip`, `!pip`, TODO/FIXME markers, or stored warnings/errors;
- the generated data dictionary contains all 156 engineered columns;
- the static JavaScript passes `node --check`;
- direct Python model inference and browser-JavaScript inference agree on all parity cases;
- the source workbook SHA-256 is `9288748def6d4dab386c3d9dc74f79485ccfde5fa4a2a70a5ed010ebe78695db`.

A second completely empty virtual environment was also attempted as an installation-only check. Dependency resolution succeeded, but the external package host repeatedly timed out while downloading `openpyxl`; therefore a fully independent reinstall could not be completed in that session. Notebook execution itself used the previously verified environment moved outside the repository, with versions pinned in `requirements.txt`, and every notebook ran in a fresh kernel. This infrastructure limitation is recorded rather than presented as an experimental failure.

## 12. Final assignment-evidence checklist

| Evidence area | Final status | Evidence |
|---|---|---|
| Business problem, users, and decision lens | Complete | `docs/problem_framing_canvas.md` |
| Unit of analysis and end-to-end workflow | Complete | `docs/workflow.md` and ordered notebooks |
| Decision chronology | Complete | `docs/decision_log.md` |
| Source and engineered EDA | Complete | supervised Notebook 02 and generated tables/figures |
| Data retention and quality | Complete | `data_retention.csv`, `engineered_dataset_audit.csv` |
| Preprocessing and feature engineering | Complete | supervised Notebooks 01/03 and `docs/preprocessing_feature_log.md` |
| Leakage prevention | Complete | notebooks, dictionary, workflow, and final configuration |
| Feature selection and imbalance evidence | Complete | supervised Notebook 04 and generated comparisons |
| Model comparison and tuning | Complete | supervised Notebook 05 and `docs/model_method_comparison.md` |
| Untouched chronological test evaluation | Complete | final metrics, report, configuration, and confusion matrix |
| Clustering comparison and interpretation | Complete | unsupervised Notebook 03 and profiling outputs |
| Recommendations, stakeholder value, and limitations | Complete | `docs/recommendations_and_limitations.md` |
| Dataset provenance and checksums | Complete | `docs/data_provenance.md` |
| Model data dictionary | Complete | `docs/model_data_dictionary.csv` |
| Reproducibility and execution status | Complete | `requirements.txt`, `scripts/run_notebooks.py`, status CSV, README |
| AI-use transparency | Complete | `docs/ai_use_statement.md` |
| Member contribution evidence | Manual sign-off required | `docs/member_contribution_map.md` deliberately contains no invented names/claims |

## 13. Remaining manual attention before submission

1. Each group member must complete and approve `docs/member_contribution_map.md`; identities and individual contributions cannot be inferred safely from repository evidence.
2. Confirm that the large source workbook is included through the university’s accepted submission method or that assessors can obtain the exact Kaggle source. Raw/generated data are gitignored intentionally.
3. Open the public Hugging Face Space once from a normal browser and confirm it still resolves at `https://huggingface.co/spaces/itsemesasanda/football-team-profiler`; finalization validated the local static files but did not publish or mutate the remote Space.
4. If required by marking rules, repeat `python -m pip install -r requirements.txt` on a stable network. The recorded external download timeout was unrelated to repository code.
5. No final report and no personal learning journey were created, in accordance with the requested scope.

No git history was rewritten and no commit, push, remote publication, or score-driven tuning beyond the documented modest search was performed.

## 14. Post-finalization unsupervised extension

After the original eight-notebook finalization, a ninth maintained notebook was added at `notebooks/unsupervised/04_clustering_overlap_and_alternatives.ipynb`. It uses the same protected 15-feature matrix and adds PCA + K-Means, full-space DBSCAN, a limited PCA + DBSCAN check, and current-model assignment-separation analysis. It does not alter supervised notebooks or overwrite the final scaler, K-Means model, feature order, or profile-name mapping.

The seven-component/five-cluster PCA candidate retains 75.9% variance and has native-space silhouette `0.1443`, but its original-space silhouette is `0.1007` and its assignments closely match the existing K-Means result (ARI `0.9304`). No plain or PCA-reduced DBSCAN configuration passed the usability screen: the strongest valid configurations assign more than 99% of non-noise rows to one cluster. The original K-Means k=5 therefore remains final and the static deployment is unchanged.

The extension was executed from top to bottom in a fresh Python 3.9.6 kernel with no stored errors or warnings. The current status record reports 5/5 supervised and 4/4 unsupervised notebooks passed (9/9 total). The extended comparison and all search, loading, explained-variance, ambiguity, and diagnostic outputs are under `outputs/team_profiling/`.

