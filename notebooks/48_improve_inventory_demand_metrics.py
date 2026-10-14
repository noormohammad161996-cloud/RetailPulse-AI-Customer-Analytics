# File: notebooks/48_improve_inventory_demand_metrics.py
# Purpose: Improve monthly demand estimates for inventory planning.

from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"
)
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "improved_inventory_demand_metrics.csv"
)

print("=" * 65)
print("RETAILPULSE - IMPROVED INVENTORY DEMAND METRICS")
print("=" * 65)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_parquet(INPUT_FILE)

required = {"product_id", "product_name", "quantity", "invoice_date"}
missing = required - set(df.columns)

if missing:
    raise ValueError(f"Required columns missing: {sorted(missing)}")

df["invoice_date"] = pd.to_datetime(
    df["invoice_date"], errors="coerce"
)
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

df = df.dropna(
    subset=["product_id", "product_name", "invoice_date", "quantity"]
).copy()

# Use complete calendar months only.
# December 2011 is excluded because the source ends on December 9.
df = df[
    (df["invoice_date"] >= "2009-12-01")
    & (df["invoice_date"] < "2011-12-01")
].copy()

df["month"] = df["invoice_date"].dt.to_period("M")

# Sum recorded quantities for each product and calendar month.
monthly = (
    df.groupby(["product_id", "month"], as_index=False)
    .agg(quantity_sold=("quantity", "sum"))
)

# Build a complete monthly calendar for every observed product.
all_months = pd.period_range(
    start="2009-12",
    end="2011-11",
    freq="M"
)

product_ids = monthly["product_id"].drop_duplicates()

calendar = pd.MultiIndex.from_product(
    [product_ids, all_months],
    names=["product_id", "month"]
).to_frame(index=False)

# Missing product-month records mean no recorded sale in that month.
complete = calendar.merge(
    monthly,
    on=["product_id", "month"],
    how="left"
)

complete["quantity_sold"] = (
    complete["quantity_sold"].fillna(0)
)

# Attach a product description.
descriptions = (
    df.sort_values("invoice_date")
    .drop_duplicates("product_id", keep="last")
    [["product_id", "product_name"]]
)

complete = complete.merge(
    descriptions,
    on="product_id",
    how="left"
)

# Calculate demand statistics across the full 24-month period.
summary = (
    complete.groupby(["product_id", "product_name"], as_index=False)
    .agg(
        months_observed=("month", "nunique"),
        months_with_sales=("quantity_sold", lambda s: (s != 0).sum()),
        total_recorded_quantity=("quantity_sold", "sum"),
        average_monthly_demand=("quantity_sold", "mean"),
        monthly_demand_std=("quantity_sold", "std"),
        minimum_monthly_demand=("quantity_sold", "min"),
        maximum_monthly_demand=("quantity_sold", "max"),
    )
)

summary["monthly_demand_std"] = (
    summary["monthly_demand_std"].fillna(0)
)

summary["demand_cv"] = np.where(
    summary["average_monthly_demand"] > 0,
    summary["monthly_demand_std"]
    / summary["average_monthly_demand"].replace(0, np.nan),
    np.nan
)

def classify_history(months_with_sales):
    if months_with_sales < 6:
        return "Limited sales history"
    return "Reviewable sales history"

summary["history_status"] = summary["months_with_sales"].apply(
    classify_history
)

summary = summary.sort_values(
    "total_recorded_quantity", ascending=False
)

summary.to_csv(OUTPUT_FILE, index=False)

print(f"\nComplete months included: {len(all_months)}")
print(f"Products analyzed: {len(summary):,}")
print(f"Product-month rows: {len(complete):,}")
print("Partial December 2011 excluded.")

print(f"\nOutput saved to: {OUTPUT_FILE}")

print("\n--- TOP 10 PRODUCTS BY RECORDED QUANTITY ---")
print(
    summary[
        [
            "product_id",
            "product_name",
            "months_with_sales",
            "total_recorded_quantity",
            "average_monthly_demand",
            "monthly_demand_std",
            "demand_cv",
            "history_status",
        ]
    ].head(10).to_string(index=False)
)

print("\n--- HISTORY STATUS ---")
print(summary["history_status"].value_counts().to_string())

print(
    "\nNote: Zero-filled months indicate no recorded sales, "
    "not confirmed zero customer demand."
)
print("Improved inventory demand analysis completed.")
