# File: notebooks/47_calculate_inventory_metrics.py
# Purpose: Calculate preliminary inventory planning metrics.
# Important: Lead time and service level below are assumptions.

from pathlib import Path
import math
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "product_demand_summary.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "inventory_planning_metrics.csv"
)

# Explicit planning assumptions — not supplied by the dataset.
LEAD_TIME_DAYS = 14
SERVICE_LEVEL = 0.95
DAYS_PER_MONTH = 30.4375

# Z-score for a 95% service level under a normal-demand assumption.
Z_SCORE = 1.645

print("=" * 65)
print("RETAILPULSE - PRELIMINARY INVENTORY METRICS")
print("=" * 65)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

required_columns = {
    "product_id",
    "product_name",
    "months_with_records",
    "total_quantity_sold",
    "average_monthly_quantity",
    "monthly_demand_std",
}

missing = required_columns - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

# Convert monthly demand measures to daily approximations.
df["average_daily_demand"] = (
    df["average_monthly_quantity"] / DAYS_PER_MONTH
)

df["daily_demand_std"] = (
    df["monthly_demand_std"] / math.sqrt(DAYS_PER_MONTH)
)

# Approximate expected demand during the assumed lead time.
df["expected_lead_time_demand"] = (
    df["average_daily_demand"] * LEAD_TIME_DAYS
)

# Preliminary safety stock and reorder point.
df["safety_stock"] = (
    Z_SCORE
    * df["daily_demand_std"]
    * math.sqrt(LEAD_TIME_DAYS)
)

df["reorder_point"] = (
    df["expected_lead_time_demand"] + df["safety_stock"]
)

# A single observed month cannot establish reliable variability.
df["planning_data_quality"] = df["months_with_records"].apply(
    lambda months: (
        "Insufficient history"
        if months < 6
        else "Preliminary estimate"
    )
)

# Round calculated indicators for easier review.
metric_columns = [
    "average_daily_demand",
    "daily_demand_std",
    "expected_lead_time_demand",
    "safety_stock",
    "reorder_point",
]

df[metric_columns] = df[metric_columns].round(2)

df.to_csv(OUTPUT_FILE, index=False)

print(f"\nProducts assessed: {len(df):,}")
print(f"Assumed lead time: {LEAD_TIME_DAYS} days")
print(f"Assumed service level: {SERVICE_LEVEL:.0%}")
print(f"Output saved to: {OUTPUT_FILE}")

print("\n--- TOP 10 PRODUCTS BY TOTAL SALES QUANTITY ---")
print(
    df.sort_values("total_quantity_sold", ascending=False)[
        [
            "product_id",
            "product_name",
            "months_with_records",
            "average_daily_demand",
            "expected_lead_time_demand",
            "safety_stock",
            "reorder_point",
            "planning_data_quality",
        ]
    ].head(10).to_string(index=False)
)

print("\n--- PLANNING DATA QUALITY ---")
print(df["planning_data_quality"].value_counts().to_string())

print("\nPreliminary inventory metrics completed.")
print("These are estimates, not actual stock or purchase orders.")
