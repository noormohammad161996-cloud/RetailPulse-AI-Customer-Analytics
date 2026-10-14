# File: notebooks/51_validate_inventory_demand.py
# Purpose: Validate monthly demand data and create safer preliminary
# inventory metrics without converting monthly standard deviation
# into daily standard deviation.

from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "improved_inventory_demand_metrics.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "validated_inventory_demand.csv"
)

# Explicit assumptions, not values from the source dataset.
LEAD_TIME_DAYS = 14
DAYS_PER_MONTH = 30.4375
Z_SCORE = 1.645  # Approximate 95% service level

print("=" * 65)
print("RETAILPULSE - INVENTORY DEMAND VALIDATION")
print("=" * 65)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

required_columns = {
    "product_id",
    "product_name",
    "months_observed",
    "months_with_sales",
    "total_recorded_quantity",
    "average_monthly_demand",
    "monthly_demand_std",
}

missing = required_columns - set(df.columns)

if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

# Validate numeric columns.
numeric_columns = [
    "months_observed",
    "months_with_sales",
    "total_recorded_quantity",
    "average_monthly_demand",
    "monthly_demand_std",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

if df[numeric_columns].isna().any().any():
    raise ValueError("Missing or invalid numeric values detected.")

if (df["average_monthly_demand"] < 0).any():
    raise ValueError("Negative average demand detected.")

if (df["monthly_demand_std"] < 0).any():
    raise ValueError("Negative demand standard deviation detected.")

# Calculate monthly-based planning estimates.
df["expected_lead_time_demand"] = (
    df["average_monthly_demand"]
    * LEAD_TIME_DAYS
    / DAYS_PER_MONTH
)

# Approximate variability over the lead time.
# This assumes independent daily demand and uses monthly variability
# as a proxy. It is not a validated daily-demand distribution.
df["safety_stock_estimate"] = (
    Z_SCORE
    * df["monthly_demand_std"]
    * np.sqrt(LEAD_TIME_DAYS / DAYS_PER_MONTH)
)

df["reorder_point_estimate"] = (
    df["expected_lead_time_demand"]
    + df["safety_stock_estimate"]
)

# Flag products with insufficient observed sales history.
df["validation_status"] = np.where(
    df["months_with_sales"] < 6,
    "Review - fewer than 6 sales months",
    "Preliminary - validate business assumptions",
)

# Flag highly variable demand.
df["variability_flag"] = np.where(
    df["demand_cv"] >= 1,
    "High variability",
    "Not flagged by CV threshold",
)

# Mark cases where variability cannot be estimated reliably.
df["variability_data_warning"] = np.where(
    (df["months_with_sales"] < 2)
    | (df["monthly_demand_std"] == 0),
    "Insufficient variation evidence",
    "Variation observed",
)

result_columns = [
    "product_id",
    "product_name",
    "months_observed",
    "months_with_sales",
    "total_recorded_quantity",
    "average_monthly_demand",
    "monthly_demand_std",
    "demand_cv",
    "expected_lead_time_demand",
    "safety_stock_estimate",
    "reorder_point_estimate",
    "validation_status",
    "variability_flag",
    "variability_data_warning",
]

df[result_columns[8:11]] = df[result_columns[8:11]].round(2)

df = df.sort_values(
    "reorder_point_estimate",
    ascending=False,
)

df[result_columns].to_csv(OUTPUT_FILE, index=False)

print(f"\nProducts validated: {len(df):,}")
print(f"Assumed lead time: {LEAD_TIME_DAYS} days")
print("Assumed service level: 95%")
print(f"Output saved to: {OUTPUT_FILE}")

print("\n--- DATA VALIDATION CHECKS ---")
print(f"Duplicate product IDs: {df['product_id'].duplicated().sum()}")
print(
    "Products with fewer than 6 sales months:",
    (df["months_with_sales"] < 6).sum(),
)
print(
    "Products with high demand variability:",
    (df["demand_cv"] >= 1).sum(),
)
print(
    "Products with insufficient variation evidence:",
    (df["variability_data_warning"]
     == "Insufficient variation evidence").sum(),
)

print("\n--- TOP 10 PRELIMINARY REORDER POINT ESTIMATES ---")
print(
    df[
        [
            "product_id",
            "product_name",
            "months_with_sales",
            "average_monthly_demand",
            "expected_lead_time_demand",
            "safety_stock_estimate",
            "reorder_point_estimate",
            "validation_status",
        ]
    ].head(10).to_string(index=False)
)

print(
    "\nReminder: These are estimates, not actual purchase quantities. "
    "Stock on hand, open purchase orders, actual supplier lead times, "
    "and stockout data are unavailable."
)

print("\nInventory demand validation completed.")
