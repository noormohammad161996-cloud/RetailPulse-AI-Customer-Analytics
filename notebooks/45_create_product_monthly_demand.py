# File: notebooks/45_create_product_monthly_demand.py
# Purpose: Calculate monthly quantity sold for each product.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"
)
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "product_monthly_demand.csv"
)

print("=" * 60)
print("RETAILPULSE - MONTHLY PRODUCT DEMAND")
print("=" * 60)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

df = pd.read_parquet(INPUT_FILE)

# Keep only the columns required for monthly demand analysis.
df = df[["product_id", "product_name", "quantity", "invoice_date"]].copy()

df["invoice_date"] = pd.to_datetime(
    df["invoice_date"], errors="coerce"
)
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

# Remove rows without a product, date, or usable quantity.
df = df.dropna(
    subset=["product_id", "invoice_date", "quantity"]
)

# Group transactions into calendar months for each product.
df["month"] = df["invoice_date"].dt.to_period("M").astype(str)

monthly_demand = (
    df.groupby(
        ["product_id", "product_name", "month"],
        dropna=False,
        as_index=False
    )
    .agg(
        quantity_sold=("quantity", "sum"),
        transaction_rows=("quantity", "size")
    )
    .sort_values(["product_id", "month"])
)

# Save the output for later inventory analysis.
monthly_demand.to_csv(OUTPUT_FILE, index=False)

print(f"Input transaction rows: {len(df):,}")
print(f"Product-month records: {len(monthly_demand):,}")
print(f"Unique products: {monthly_demand['product_id'].nunique():,}")
print(f"Months covered: {monthly_demand['month'].nunique():,}")

print("\nFirst 10 records:")
print(monthly_demand.head(10).to_string(index=False))

print(f"\nOutput saved to: {OUTPUT_FILE}")
print("\nMonthly product demand preparation completed.")
