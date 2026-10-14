# File: notebooks/52_prepare_inventory_dashboard_data.py
# Purpose: Prepare a clean inventory dataset for the Streamlit dashboard.

from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "validated_inventory_demand.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_dashboard_data.csv"
)

print("=" * 65)
print("RETAILPULSE - INVENTORY DASHBOARD DATA PREPARATION")
print("=" * 65)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

# Assign a simple dashboard category using existing CV results.
def classify_inventory_risk(row):
    if row["months_with_sales"] < 6:
        return "Insufficient history"
    if row["demand_cv"] >= 1:
        return "High demand variability"
    if row["demand_cv"] >= 0.5:
        return "Moderate demand variability"
    return "Lower demand variability"

df["inventory_review_category"] = df.apply(
    classify_inventory_risk,
    axis=1
)

# Use the available columns; do not invent actual stock quantities.
dashboard_columns = [
    "product_id",
    "product_name",
    "months_with_sales",
    "total_recorded_quantity",
    "average_monthly_demand",
    "monthly_demand_std",
    "demand_cv",
    "expected_lead_time_demand",
    "safety_stock_estimate",
    "reorder_point_estimate",
    "validation_status",
    "variability_data_warning",
    "inventory_review_category",
]

missing = set(dashboard_columns) - set(df.columns)
if missing:
    raise ValueError(f"Required columns missing: {sorted(missing)}")

dashboard_df = df[dashboard_columns].copy()

dashboard_df["demand_cv"] = dashboard_df["demand_cv"].replace(
    [np.inf, -np.inf], np.nan
)

dashboard_df = dashboard_df.sort_values(
    "total_recorded_quantity",
    ascending=False
)

dashboard_df.to_csv(OUTPUT_FILE, index=False)

print(f"\nDashboard product records: {len(dashboard_df):,}")
print(f"Output saved to: {OUTPUT_FILE}")

print("\n--- INVENTORY REVIEW CATEGORIES ---")
print(
    dashboard_df["inventory_review_category"]
    .value_counts()
    .to_string()
)

print("\n--- SAMPLE DASHBOARD DATA ---")
print(
    dashboard_df[
        [
            "product_id",
            "product_name",
            "average_monthly_demand",
            "reorder_point_estimate",
            "inventory_review_category",
        ]
    ].head(10).to_string(index=False)
)

print(
    "\nNote: Reorder points are preliminary estimates. "
    "Actual inventory on hand is not available."
)

print("\nInventory dashboard data preparation completed.")
