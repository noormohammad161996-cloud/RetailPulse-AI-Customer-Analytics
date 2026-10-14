# File: notebooks/55_inspect_forecast_results.py
# Purpose: Inspect existing forecast result files and their metrics.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FORECAST_FILES = [
    "baseline_forecast_results.csv",
    "prophet_forecast_results.csv",
]

print("=" * 65)
print("RETAILPULSE - FORECAST RESULTS INSPECTION")
print("=" * 65)

for filename in FORECAST_FILES:
    file_path = PROCESSED_DIR / filename

    print(f"\n--- {filename} ---")

    if not file_path.exists():
        print("File not found.")
        continue

    try:
        df = pd.read_csv(file_path)

        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")
        print("Column names:", list(df.columns))

        if not df.empty:
            print("\nFirst 10 rows:")
            print(df.head(10).to_string(index=False))

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:
            print("\nNumeric column summary:")
            print(df[numeric_columns].describe().round(3).to_string())

    except Exception as exc:
        print(f"Could not read file: {exc}")

print("\nForecast results inspection completed.")
