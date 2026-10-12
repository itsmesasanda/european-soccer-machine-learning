from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = PROJECT_ROOT / "data/raw/european_soccer_database.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "data/extracted"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not EXCEL_PATH.exists():
    raise FileNotFoundError(
        "Expected source workbook at data/raw/european_soccer_database.xlsx"
    )

print("Using Excel file: data/raw/european_soccer_database.xlsx")
excel_file = pd.ExcelFile(EXCEL_PATH)

for sheet_name in excel_file.sheet_names:
    print(f"Converting: {sheet_name}")

    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)

    output_file = OUTPUT_DIR / f"{sheet_name}.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Saved: {output_file.relative_to(PROJECT_ROOT)} "
        f"({len(df)} rows, {len(df.columns)} columns)"
    )

print("\nFinished converting all sheets.")
