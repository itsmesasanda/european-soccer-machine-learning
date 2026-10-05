import pandas as pd
from openpyxl import load_workbook
from pathlib import Path

# Find Excel file automatically
RAW_DIR = Path("data/raw/european_soccer_database.xlsx")
excel_files = list(RAW_DIR.glob("*.xlsx"))

if not excel_files:
    raise FileNotFoundError("No Excel file found in data/raw")

FILE_PATH = excel_files[0]

print("Using:", FILE_PATH)

# Open workbook in read-only mode
workbook = load_workbook(
    FILE_PATH,
    read_only=True,
    data_only=True
)

print("\nTABLES FOUND")
print("=" * 60)

for sheet_name in workbook.sheetnames:
    print(sheet_name)

print("\n\nTABLE DETAILS")
print("=" * 60)

for sheet_name in workbook.sheetnames:

    sheet = workbook[sheet_name]

    print(f"\nTABLE: {sheet_name}")
    print("-" * 60)

    # First row contains column names
    first_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))

    print("Rows:", sheet.max_row - 1)
    print("Columns:", sheet.max_column)

    print("\nColumn names:")

    for column in first_row:
        print(" -", column)

workbook.close()