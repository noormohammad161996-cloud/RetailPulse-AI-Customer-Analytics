# File: notebooks/54_inspect_forecast_outputs.py
# Purpose: Inspect existing sales forecasting outputs before
# integrating forecasting results into the Streamlit dashboard.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CANDIDATE_FILES = [
    "monthly_sales_summary.csv",
    "monthly_forecasting_data.csv",
    "kmeans_model_comparison.csv",  # Not a sales forecast; inspect separately.
]

print("=" * 65)
print("RETAILPULSE - FORECAST OUTPUT INSPECTION")
print("=" * 65)

for filename in CANDIDATE_FILES:
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
            print("\nFirst 5 rows:")
            print(df.head().to_string(index=False))

    except Exception as exc:
        print(f"Could not read file: {exc}")

print("\n--- OTHER FORECAST-RELATED CSV FILES ---")

forecast_keywords = [
    "forecast",
    "monthly_sales",
    "sales_forecast",
]

matches = []

if PROCESSED_DIR.exists():
    for file_path in sorted(PROCESSED_DIR.glob("*.csv")):
        if any(
            keyword in file_path.name.lower()
            for keyword in forecast_keywords
        ):
            matches.append(file_path)

if matches:
    for file_path in matches:
        print(f"- {file_path.relative_to(PROJECT_ROOT)}")
else:
    print("No matching forecast CSV files found.")

print("\nForecast output inspection completed.")
