# File: notebooks/46_analyze_product_demand.py
# Purpose: Summarize product demand and measure its variability.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "product_monthly_demand.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "product_demand_summary.csv"
)

print("=" * 65)
print("RETAILPULSE - PRODUCT DEMAND ANALYSIS")
print("=" * 65)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

required_columns = {
    "product_id",
    "product_name",
    "month",
    "quantity_sold",
    "transaction_rows",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {sorted(missing_columns)}"
    )

df["quantity_sold"] = pd.to_numeric(
    df["quantity_sold"], errors="coerce"
)
df = df.dropna(subset=["product_id", "month", "quantity_sold"])

# Summarize the observed monthly sales for each product.
summary = (
    df.groupby(["product_id", "product_name"], dropna=False)
    .agg(
        months_with_records=("month", "nunique"),
        total_quantity_sold=("quantity_sold", "sum"),
        average_monthly_quantity=("quantity_sold", "mean"),
        monthly_demand_std=("quantity_sold", "std"),
        minimum_monthly_quantity=("quantity_sold", "min"),
        maximum_monthly_quantity=("quantity_sold", "max"),
    )
    .reset_index()
)

# A product with one observed month has no meaningful sample std.
summary["monthly_demand_std"] = (
    summary["monthly_demand_std"].fillna(0)
)

# Coefficient of variation measures variability relative to average.
summary["demand_cv"] = 0.0
positive_average = summary["average_monthly_quantity"] > 0

summary.loc[positive_average, "demand_cv"] = (
    summary.loc[positive_average, "monthly_demand_std"]
    / summary.loc[positive_average, "average_monthly_quantity"]
)

def classify_demand(cv):
    if cv < 0.5:
        return "Low variability"
    elif cv < 1.0:
        return "Moderate variability"
    return "High variability"

summary["demand_variability"] = summary["demand_cv"].apply(
    classify_demand
)

summary = summary.sort_values(
    "total_quantity_sold", ascending=False
)

summary.to_csv(OUTPUT_FILE, index=False)

print(f"\nProducts analyzed: {len(summary):,}")
print(f"Output saved to: {OUTPUT_FILE}")

print("\n--- TOP 10 PRODUCTS BY TOTAL QUANTITY ---")
print(
    summary[
        [
            "product_id",
            "product_name",
            "total_quantity_sold",
            "average_monthly_quantity",
            "monthly_demand_std",
            "demand_cv",
            "demand_variability",
        ]
    ].head(10).to_string(index=False)
)

print("\n--- DEMAND VARIABILITY COUNTS ---")
print(summary["demand_variability"].value_counts().to_string())

print("\nDemand analysis completed.")
