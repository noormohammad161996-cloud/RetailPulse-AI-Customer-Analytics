from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
input_file = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "temporal_churn_validation.csv"
)

df = pd.read_csv(input_file)

required_columns = [
    "customer_id",
    "frequency",
    "monetary",
    "recency_days",
    "churned",
]

print("TEMPORAL CHURN DATASET VALIDATION")
print("=================================")

print(f"Rows: {len(df):,}")
print(f"Unique customers: {df['customer_id'].nunique():,}")

print("\nMissing values:")
print(df[required_columns].isna().sum().to_string())

print(
    "\nDuplicate customer IDs:",
    df["customer_id"].duplicated().sum(),
)

print("\nFeature checks:")
print("Frequency <= 0:", (df["frequency"] <= 0).sum())
print("Negative recency:", (df["recency_days"] < 0).sum())
print("Monetary <= 0:", (df["monetary"] <= 0).sum())

print("\nChurn label counts:")
print(df["churned"].value_counts().sort_index().to_string())

assert not df[required_columns].isna().any().any(), (
    "Missing values found in required columns."
)
assert not df["customer_id"].duplicated().any(), (
    "Duplicate customer IDs found."
)
assert (df["frequency"] > 0).all(), "Invalid frequency values found."
assert (df["recency_days"] >= 0).all(), "Invalid recency values found."
assert (df["monetary"] > 0).all(), "Invalid monetary values found."
assert set(df["churned"].unique()).issubset({0, 1}), (
    "Unexpected churn labels found."
)

print("\nAll validation checks passed.")
