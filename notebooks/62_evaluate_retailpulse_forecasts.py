# File: notebooks/62_evaluate_retailpulse_forecasts.py
# Purpose: Evaluate RetailPulse forecast models using multiple metrics.

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "forecast_model_comparison.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "forecast_detailed_metrics.csv"
)

print("=" * 65)
print("RETAILPULSE - DETAILED FORECAST EVALUATION")
print("=" * 65)

df = pd.read_csv(INPUT_FILE)

required = {"actual_sales", "predicted_sales", "model"}
missing = required - set(df.columns)

if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

results = []

for model_name, group in df.groupby("model"):
    actual = group["actual_sales"].to_numpy(dtype=float)
    predicted = group["predicted_sales"].to_numpy(dtype=float)

    absolute_errors = np.abs(actual - predicted)

    mae = mean_absolute_error(actual, predicted)
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)

    wape = (
        absolute_errors.sum() / np.abs(actual).sum() * 100
        if np.abs(actual).sum() > 0
        else np.nan
    )

    # R-squared can be unstable with only five test observations.
    r2 = (
        r2_score(actual, predicted)
        if len(actual) >= 2 and np.var(actual) > 0
        else np.nan
    )

    results.append({
        "model": model_name,
        "test_months": len(actual),
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "WAPE_percent": wape,
        "R2": r2,
    })

summary = pd.DataFrame(results).sort_values("WAPE_percent")
summary.to_csv(OUTPUT_FILE, index=False, float_format="%.6f")

print("\nModel metrics (ranked by WAPE):")
print(summary.to_string(index=False, float_format=lambda x: f"{x:,.4f}"))

print(f"\nResults saved to: {OUTPUT_FILE}")
print("\nNote: Metrics are based on five test months only.")
print("R-squared may be unstable with such a small test sample.")
print("\nDetailed forecast evaluation completed.")
