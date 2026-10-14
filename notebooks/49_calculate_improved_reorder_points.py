# File: notebooks/49_calculate_improved_reorder_points.py
# Purpose: Estimate reorder points using calendar-month demand statistics.
# Lead time and service level are assumptions, not source data.

from pathlib import Path
import math
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "improved_inventory_demand_metrics.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "improved_inventory_reorder_points.csv"
)

LEAD_TIME_DAYS = 14
DAYS_PER_MONTH = 30.4375
Z_SCORE = 1.645  # Approximate 95% service level

print("=" * 65)
print("RETAILPULSE - IMPROVED REORDER POINT ANALYSIS")
print("=" * 65)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

required = {
    "product_id",
    "product_name",
    "months_with_sales",
    "average_monthly_demand",
    "monthly_demand_std",
    "history_status",
}

missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

# Convert monthly demand to approximate daily demand.
df["average_daily_demand"] = (
    df["average_monthly_demand"] / DAYS_PER_MONTH
)

# Approximate daily standard deviation from monthly variability.
# This is a simplifying assumption, not a validated daily-demand model.
df["daily_demand_std_approx"] = (
    df["monthly_demand_std"] / math.sqrt(DAYS_PER_MONTH)
)

df["expected_lead_time_demand"] = (
    df["average_daily_demand"] * LEAD_TIME_DAYS
)

df["safety_stock_approx"] = (
    Z_SCORE
    * df["daily_demand_std_approx"]
    * math.sqrt(LEAD_TIME_DAYS)
)

df["reorder_point_approx"] = (
    df["expected_lead_time_demand"]
    + df["safety_stock_approx"]
)

# Avoid presenting weak-history estimates as reliable recommendations.
df["recommendation_status"] = np.where(
    df["months_with_sales"] < 6,
    "Review manually - limited history",
    "Preliminary estimate - validate assumptions",
)

numeric_columns = [
    "average_daily_demand",
    "daily_demand_std_approx",
    "expected_lead_time_demand",
    "safety_stock_approx",
    "reorder_point_approx",
]

df[numeric_columns] = df[numeric_columns].round(2)

df = df.sort_values(
    "reorder_point_approx", ascending=False
)

df.to_csv(OUTPUT_FILE, index=False)

print(f"\nProducts assessed: {len(df):,}")
print(f"Assumed lead time: {LEAD_TIME_DAYS} days")
print("Assumed service level: 95%")
print(f"Output saved to: {OUTPUT_FILE}")

print("\n--- TOP 10 PRELIMINARY REORDER POINTS ---")
print(
    df[
        [
            "product_id",
            "product_name",
            "months_with_sales",
            "average_daily_demand",
            "expected_lead_time_demand",
            "safety_stock_approx",
            "reorder_point_approx",
            "recommendation_status",
        ]
    ].head(10).to_string(index=False)
)

print("\n--- RECOMMENDATION STATUS ---")
print(df["recommendation_status"].value_counts().to_string())

print(
    "\nIMPORTANT: These are estimated reorder points, not "
    "purchase quantities. Actual on-hand stock, open orders, "
    "supplier lead times, and stockout data are unavailable."
)
print("Improved reorder point analysis completed.")
