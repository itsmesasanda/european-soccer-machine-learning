from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/extracted")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

excel_files = list(RAW_DIR.glob("*.xlsx"))

if not excel_files:
    raise FileNotFoundError("No Excel file found in data/raw")

excel_path = excel_files[0]

print("Using Excel file:", excel_path)

excel_file = pd.ExcelFile(excel_path)

for sheet_name in excel_file.sheet_names:
    print(f"Converting: {sheet_name}")

    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    output_file = OUTPUT_DIR / f"{sheet_name}.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Saved: {output_file} "
        f"({len(df)} rows, {len(df.columns)} columns)"
    )

print("\nFinished converting all sheets.")