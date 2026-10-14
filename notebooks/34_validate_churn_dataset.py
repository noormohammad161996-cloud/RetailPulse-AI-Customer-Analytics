from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
input_file = PROJECT_ROOT / "data" / "processed" / "customer_churn_dataset.csv"

df = pd.read_csv(input_file)

print("RETAILPULSE - CHURN DATASET VALIDATION")
print("======================================")

# Basic information
print(f"Total rows: {len(df):,}")
print(f"Total columns: {len(df.columns)}")
print(f"Unique customers: {df['customer_id'].nunique():,}")

# Required columns
required_columns = [
    "customer_id",
    "frequency",
    "monetary",
    "recency_days",
    "churned",
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Missing values
print("\nMissing values:")
print(df[required_columns].isna().sum().to_string())

# Duplicate customers
print(f"\nDuplicate customer IDs: {df['customer_id'].duplicated().sum()}")

# Validate feature values
print("\nFeature validation:")
print(f"Customers with frequency <= 0: {(df['frequency'] <= 0).sum()}")
print(f"Customers with negative recency: {(df['recency_days'] < 0).sum()}")
print(f"Customers with non-positive monetary: {(df['monetary'] <= 0).sum()}")

# Validate target labels
print("\nChurn label values:")
print(sorted(df["churned"].dropna().unique()))

if not set(df["churned"].dropna().unique()).issubset({0, 1}):
    raise ValueError("Unexpected churn label values.")

# Check the class distribution
print("\nTarget distribution:")
print(
    df["churned"]
    .value_counts()
    .sort_index()
    .rename(index={0: "Retained (0)", 1: "Churned (1)"})
    .to_string()
)

print("\nValidation checks completed.")
