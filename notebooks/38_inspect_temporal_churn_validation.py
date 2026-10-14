from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
input_file = PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"

df = pd.read_parquet(input_file)

df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")

df = df.dropna(subset=["customer_id", "invoice_date"]).copy()

print("RETAILPULSE - TEMPORAL CHURN VALIDATION INSPECTION")
print("=================================================")

print(f"First transaction: {df['invoice_date'].min()}")
print(f"Last transaction:  {df['invoice_date'].max()}")

print("\nTransactions by month:")
monthly = (
    df.groupby(df["invoice_date"].dt.to_period("M"))
    .agg(
        transaction_rows=("invoice_id", "size"),
        identified_customers=("customer_id", "nunique"),
    )
)

print(monthly.to_string())

print("\nCandidate historical cutoffs:")
for cutoff in [
    "2010-12-31",
    "2011-03-31",
    "2011-05-31",
    "2011-08-31",
]:
    cutoff_date = pd.Timestamp(cutoff) + pd.Timedelta(days=1)

    feature_customers = df.loc[
        df["invoice_date"] < cutoff_date, "customer_id"
    ].nunique()

    print(
        f"Cutoff {cutoff}: "
        f"{feature_customers:,} customers with prior transactions"
    )

print("\nInspection completed.")
