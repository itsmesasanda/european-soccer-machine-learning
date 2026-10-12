"""Execute the final notebooks in submission order and record each result."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import nbformat
import pandas as pd
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = [
    PROJECT_ROOT / "notebooks/supervised/01_data_inspection_and_feature_engineering.ipynb",
    PROJECT_ROOT / "notebooks/supervised/02_exploratory_data_analysis.ipynb",
    PROJECT_ROOT / "notebooks/supervised/03_data_cleaning_and_preprocessing.ipynb",
    PROJECT_ROOT / "notebooks/supervised/04_feature_selection_and_baseline_modeling.ipynb",
    PROJECT_ROOT / "notebooks/supervised/05_final_model_fitting_and_evaluation.ipynb",
    PROJECT_ROOT / "notebooks/unsupervised/01_team_performance_profiling.ipynb",
    PROJECT_ROOT / "notebooks/unsupervised/02_team_performance_eda.ipynb",
    PROJECT_ROOT / "notebooks/unsupervised/03_team_performance_clustering.ipynb",
    PROJECT_ROOT / "notebooks/unsupervised/04_clustering_overlap_and_alternatives.ipynb",
]
STATUS_PATH = PROJECT_ROOT / "outputs/tables/notebook_execution_status.csv"


def execute_notebook(path: Path, timeout: int) -> dict[str, object]:
    started = time.perf_counter()
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(PROJECT_ROOT)}},
        allow_errors=False,
        record_timing=True,
    )
    try:
        client.execute(cwd=str(PROJECT_ROOT))
        status = "passed"
        error = ""
    except CellExecutionError as exc:
        status = "failed"
        error = str(exc).splitlines()[-1][:500]
    except Exception as exc:
        status = "failed"
        details = str(exc).splitlines()
        message = details[-1] if details else "No error message was supplied."
        error = f"{type(exc).__name__}: {message}"[:500]
    finally:
        nbformat.write(notebook, path)

    return {
        "notebook": str(path.relative_to(PROJECT_ROOT)),
        "status": status,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "error": error,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Maximum seconds allowed for one notebook cell (default: 3600).",
    )
    args = parser.parse_args()

    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for notebook_path in NOTEBOOKS:
        print(f"Executing {notebook_path.relative_to(PROJECT_ROOT)}", flush=True)
        result = execute_notebook(notebook_path, args.timeout)
        rows.append(result)
        pd.DataFrame(rows).to_csv(STATUS_PATH, index=False)
        print(
            f"  {result['status']} in {result['elapsed_seconds']} seconds",
            flush=True,
        )
        if result["status"] == "failed":
            print(f"  {result['error']}", flush=True)
            return 1

    print(f"Execution log: {STATUS_PATH.relative_to(PROJECT_ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
