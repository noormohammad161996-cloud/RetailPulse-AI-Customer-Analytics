# File: notebooks/56_create_forecast_comparison.py
# Purpose: Combine existing forecast predictions for dashboard charts.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = (
    PROCESSED_DIR / "forecast_model_comparison.csv"
)

FORECAST_FILES = {
    "Mean baseline": "baseline_forecast_results.csv",
    "Prophet": "prophet_forecast_results.csv",
    "Seasonal naive": "seasonal_naive_results.csv",
}

print("=" * 65)
print("RETAILPULSE - FORECAST MODEL COMPARISON")
print("=" * 65)

frames = []

for model_name, filename in FORECAST_FILES.items():
    file_path = PROCESSED_DIR / filename

    print(f"\nChecking {filename}...")

    if not file_path.exists():
        print("File not found; skipping this model.")
        continue

    df = pd.read_csv(file_path)

    required = {"month", "actual_sales", "predicted_sales"}
    missing = required - set(df.columns)

    if missing:
        print(f"Skipping file; missing columns: {sorted(missing)}")
        continue

    model_df = df[
        ["month", "actual_sales", "predicted_sales"]
    ].copy()

    model_df["month"] = pd.to_datetime(
        model_df["month"], errors="coerce"
    )

    model_df["actual_sales"] = pd.to_numeric(
        model_df["actual_sales"], errors="coerce"
    )

    model_df["predicted_sales"] = pd.to_numeric(
        model_df["predicted_sales"], errors="coerce"
    )

    model_df = model_df.dropna(
        subset=["month", "actual_sales", "predicted_sales"]
    )

    model_df["model"] = model_name
    model_df["absolute_error"] = (
        model_df["actual_sales"] - model_df["predicted_sales"]
    ).abs()

    frames.append(model_df)

if not frames:
    raise RuntimeError(
        "No valid forecast files were found. "
        "Check the existing forecast output filenames."
    )

comparison = pd.concat(frames, ignore_index=True)

comparison["month"] = comparison["month"].dt.strftime("%Y-%m-%d")

comparison = comparison.sort_values(["month", "model"])

comparison.to_csv(OUTPUT_FILE, index=False)

print(f"\nModels included: {comparison['model'].nunique()}")
print(f"Forecast records: {len(comparison):,}")
print(f"Output saved to: {OUTPUT_FILE}")

print("\n--- MODEL SUMMARY ---")

summary = (
    comparison.groupby("model")
    .apply(
        lambda group: pd.Series({
            "test_months": group["month"].nunique(),
            "MAE": group["absolute_error"].mean(),
            "WAPE_percent": (
                group["absolute_error"].sum()
                / group["actual_sales"].abs().sum()
                * 100
                if group["actual_sales"].abs().sum() != 0
                else float("nan")
            ),
        }),
        include_groups=False,
    )
    .round(2)
)

print(summary.to_string())

print("\nForecast comparison dataset created.")
