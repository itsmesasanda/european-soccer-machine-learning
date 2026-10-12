# Model and Method Comparison

## Supervised baselines

All values below use the 2014/15 validation season; no test result was used for selection.

| Method | Representation | Accuracy | Macro F1 |
|---|---|---:|---:|
| Dummy, most frequent | All 80 | 0.4480 | 0.2063 |
| Random Forest | All 80 | 0.5112 | 0.3889 |
| Balanced Random Forest | Top 40 | 0.5109 | 0.3832 |
| Logistic Regression | All 80, standardized | 0.4832 | 0.4383 |
| Logistic Regression | Top 40, standardized | 0.4858 | 0.4431 |
| PCA + Logistic Regression | 42 components | 0.4874 | 0.4523 |
| Gradient Boosting | All 80, balanced weights | 0.4738 | 0.4545 |

Generated source: `outputs/tables/baseline_model_comparison.csv`.

## Final candidate comparison

Using the selected Top-40 representation:

| Method | Accuracy | Macro F1 | Draw F1 |
|---|---:|---:|---:|
| Gradient Boosting | 0.4764 | 0.4570 | 0.3020 |
| HistGradientBoosting | 0.4744 | 0.4524 | 0.2883 |
| Linear SVM | 0.4995 | 0.3922 | 0.0491 |
| Extra Trees | 0.5155 | 0.3815 | 0.0264 |

Extra Trees has the largest accuracy but almost no useful Draw performance. Gradient Boosting leads the primary Macro F1 measure and is selected before test access.

## Feature-set and imbalance evidence

- Top 40 Gradient Boosting: Macro F1 `0.4570`, accuracy `0.4764`.
- All 80 Gradient Boosting: Macro F1 `0.4545`, accuracy `0.4738`.
- Unweighted Top-40 Gradient Boosting: Macro F1 `0.3806`, Draw F1 `0.0264`.
- Balanced Top-40 Gradient Boosting: Macro F1 `0.4570`, Draw F1 `0.3020`.

The smaller feature set and balanced sample weights are therefore retained.

## Hyperparameter tuning

Twenty configurations are sampled deterministically from the declared parameter space. Each model fits training only and is evaluated on 2014/15 validation.

Best configuration:

```text
n_estimators      250
learning_rate     0.05
max_depth         2
min_samples_leaf  5
subsample         1.0
random_state      42
```

Best validation performance: Macro F1 `0.4636`, accuracy `0.4813`.

## Locked final test

After locking all decisions, the model is refitted on training plus validation and evaluated once on 2015/16:

| Metric | Value |
|---|---:|
| Accuracy | 0.4545 |
| Macro F1 | 0.4410 |
| Weighted F1 | 0.4618 |
| Home Win F1 | 0.5477 |
| Draw F1 | 0.3110 |
| Away Win F1 | 0.4644 |

## Unsupervised method comparison

| Method | Dimensions | Clusters | Silhouette | Davies-Bouldin | Calinski-Harabasz | Noise | Largest assigned cluster |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original K-Means | 15 | 5 | 0.1003 | 2.1681 | 107.8473 | 0.0% | 28.1% |
| Hierarchical | 15 | 5 | 0.0686 | 2.6068 | 84.3548 | 0.0% | 27.5% |
| GMM, tied covariance | 15 | 7 | 0.0421 | 2.5545 | 46.0667 | 0.0% | 57.8% |
| PCA + K-Means candidate | 7 | 5 | 0.1443 | 1.7136 | 162.8428 | 0.0% | 28.6% |
| DBSCAN diagnostic | 15 | 2 | 0.3215 | 0.8308 | 12.3176 | 3.7% | 99.6% |
| PCA + DBSCAN diagnostic | 5 | 2 | 0.3578 | 0.7405 | 25.0994 | 2.3% | 99.3% |

The rows do not all share a metric space. PCA + K-Means metrics use the seven-component space, which retains 75.9% of variance. Its labels score 0.1007 silhouette, 2.1596 Davies–Bouldin, and 107.6439 Calinski–Harabasz when assessed in the original standardized feature space—effectively the same as the retained model. Its assignments are also very similar to current K-Means (adjusted Rand index 0.9304).

The density-method metrics exclude noise. Their apparently high silhouette scores describe one giant cluster and a four- or seven-row microcluster, not a useful segmentation; none of the searched configurations passed the generous usability screen. Original K-Means is therefore retained for its five balanced, directly interpretable profiles and deployment continuity. The low absolute silhouette remains central: these are overlapping historical archetypes, not natural categories with sharp boundaries. Generated source: `outputs/team_profiling/tables/extended_clustering_model_comparison.csv`.
