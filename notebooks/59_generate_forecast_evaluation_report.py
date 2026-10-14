# File: notebooks/59_generate_forecast_evaluation_report.py
# Purpose: Generate a report comparing sales forecast models.

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "forecast_model_comparison.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "forecast_evaluation_report.txt"
)

print("=" * 65)
print("RETAILPULSE - FORECAST EVALUATION REPORT")
print("=" * 65)

df = pd.read_csv(INPUT_FILE)

required_columns = {
    "month",
    "actual_sales",
    "predicted_sales",
    "model",
}

missing = required_columns - set(df.columns)

if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

# Calculate model-level metrics from the recorded forecasts.
results = []

for model_name, group in df.groupby("model"):
    actual = group["actual_sales"]
    predicted = group["predicted_sales"]

    absolute_error = (actual - predicted).abs()

    mae = absolute_error.mean()
    wape = (
        absolute_error.sum() / actual.abs().sum() * 100
        if actual.abs().sum() != 0
        else float("nan")
    )

    results.append({
        "model": model_name,
        "test_months": group["month"].nunique(),
        "MAE": mae,
        "WAPE_percent": wape,
    })

summary = pd.DataFrame(results).sort_values("WAPE_percent")

best_model = summary.iloc[0]["model"]

lines = [
    "RETAILPULSE - FORECAST EVALUATION REPORT",
    "=" * 50,
    "",
    f"Models evaluated: {len(summary)}",
    f"Test months per model: {df['month'].nunique()}",
    "",
    "MODEL METRICS (ranked by WAPE, lower is better)",
    "-" * 50,
    summary.to_string(index=False, float_format=lambda x: f"{x:,.2f}"),
    "",
    f"Best model on this test period: {best_model}",
    "",
    "Metric definitions:",
    "- MAE: Mean Absolute Error; lower is better.",
    "- WAPE: Weighted Absolute Percentage Error; lower is better.",
    "",
    "Limitations:",
    "- Evaluation uses only five test months.",
    "- Historical performance does not guarantee future accuracy.",
    "- More rolling-origin validation is needed before production use.",
]

report = "\n".join(lines) + "\n"
OUTPUT_FILE.write_text(report, encoding="utf-8")

print(summary.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
print(f"\nBest model on this test period: {best_model}")
print(f"Report saved to: {OUTPUT_FILE}")
print("\nForecast evaluation report generated successfully.")
