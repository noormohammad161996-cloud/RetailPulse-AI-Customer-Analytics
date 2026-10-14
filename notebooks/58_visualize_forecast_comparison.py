# File: notebooks/58_visualize_forecast_comparison.py
# Purpose: Compare actual monthly sales with three forecast models.

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

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
    / "forecast_model_comparison.png"
)

print("=" * 65)
print("RETAILPULSE - FORECAST COMPARISON VISUALIZATION")
print("=" * 65)

df = pd.read_csv(INPUT_FILE)
df["month"] = pd.to_datetime(df["month"])

# Keep one copy of actual sales for each month.
actual = (
    df[["month", "actual_sales"]]
    .drop_duplicates(subset=["month"])
    .sort_values("month")
)

plt.figure(figsize=(12, 7))

plt.plot(
    actual["month"],
    actual["actual_sales"],
    marker="o",
    linewidth=3,
    label="Actual Sales",
)

for model_name in df["model"].unique():
    model_data = (
        df[df["model"] == model_name]
        .sort_values("month")
    )

    plt.plot(
        model_data["month"],
        model_data["predicted_sales"],
        marker="o",
        linestyle="--",
        label=model_name,
    )

plt.title("Actual vs Predicted Monthly Sales")
plt.xlabel("Month")
plt.ylabel("Sales Value")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
plt.close()

print(f"\nChart saved to: {OUTPUT_FILE}")
print(f"Months compared: {actual['month'].nunique()}")
print(f"Models compared: {df['model'].nunique()}")
print("\nForecast visualization completed successfully.")