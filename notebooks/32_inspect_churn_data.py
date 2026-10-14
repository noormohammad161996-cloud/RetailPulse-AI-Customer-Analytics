from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
input_file = PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"

df = pd.read_parquet(input_file)

df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")

print("RETAILPULSE - CHURN DATA INSPECTION")
print("===================================")

print(f"Total transaction rows: {len(df):,}")
print(f"Identified customers: {df['customer_id'].nunique():,}")
print(f"Earliest transaction: {df['invoice_date'].min()}")
print(f"Latest transaction: {df['invoice_date'].max()}")

print("\nTransactions by year:")
print(df.groupby(df["invoice_date"].dt.year).size().to_string())

print("\nTransactions by month (last 6 months):")
monthly = (
    df.groupby(df["invoice_date"].dt.to_period("M"))
    .size()
    .tail(6)
)
print(monthly.to_string())

print("\nMissing values in key columns:")
print(df[["customer_id", "invoice_date", "quantity", "unit_price"]].isna().sum())
