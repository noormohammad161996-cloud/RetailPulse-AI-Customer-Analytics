# File: notebooks/68_validate_reorder_point_formulas.py
# Purpose: Validate stored reorder-point formulas and flag unusual variability.

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "improved_inventory_reorder_points.csv"
)

df = pd.read_csv(INPUT_FILE)

# Reconstruct the basic reorder-point formula.
df["expected_reorder_point_check"] = (
    df["expected_lead_time_demand"] + df["safety_stock_approx"]
)

df["reorder_point_difference"] = (
    df["reorder_point_approx"] - df["expected_reorder_point_check"]
)

print("=" * 70)
print("RETAILPULSE - REORDER-POINT FORMULA VALIDATION")
print("=" * 70)

tolerance = 0.02
consistent = df["reorder_point_difference"].abs() <= tolerance

print(f"\nProducts checked: {len(df):,}")
print(f"Formula-consistent products: {consistent.sum():,}")
print(f"Products needing formula review: {(~consistent).sum():,}")

print("\nDemand CV distribution:")
print(df["demand_cv"].describe().round(3).to_string())

print("\nProducts with demand CV >= 3:")
high_cv = df[df["demand_cv"] >= 3].sort_values(
    "demand_cv", ascending=False
)

columns = [
    "product_id",
    "product_name",
    "months_with_sales",
    "average_monthly_demand",
    "monthly_demand_std",
    "demand_cv",
    "safety_stock_approx",
    "reorder_point_approx",
]

print(f"Count: {len(high_cv):,}")
if high_cv.empty:
    print("No products met this review threshold.")
else:
    print(high_cv[columns].head(10).round(2).to_string(index=False))

print("\nLargest formula differences:")
print(
    df.loc[
        df["reorder_point_difference"].abs().nlargest(5).index,
        [
            "product_id",
            "reorder_point_approx",
            "expected_reorder_point_check",
            "reorder_point_difference",
        ],
    ].round(3).to_string(index=False)
)

print("\nValidation completed. Original CSV was not modified.")
