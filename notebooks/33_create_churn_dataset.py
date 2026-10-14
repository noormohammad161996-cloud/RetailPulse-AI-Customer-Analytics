from pathlib import Path

import pandas as pd

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Input and output paths
input_file = PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"
output_file = PROJECT_ROOT / "data" / "processed" / "customer_churn_dataset.csv"

# Historical prediction and observation windows
feature_cutoff = pd.Timestamp("2011-08-31 23:59:59")
observation_start = pd.Timestamp("2011-09-01 00:00:00")
observation_end = pd.Timestamp("2011-11-30 23:59:59")

print("RETAILPULSE - CREATE CHURN DATASET")
print("==================================")

# Load the filtered sales dataset
df = pd.read_parquet(input_file)

df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")

# Keep records with identified customers and valid dates
df = df.dropna(subset=["customer_id", "invoice_date"]).copy()

# Feature window: information available on or before the cutoff
feature_data = df[df["invoice_date"] <= feature_cutoff].copy()

# Observation window: future behavior used only to create the label
observation_data = df[
    (df["invoice_date"] >= observation_start)
    & (df["invoice_date"] <= observation_end)
].copy()

if feature_data.empty or observation_data.empty:
    raise ValueError("Feature or observation window contains no transactions.")

# Calculate customer features using only the feature window
reference_date = feature_cutoff.normalize() + pd.Timedelta(days=1)

customer_features = (
    feature_data.groupby("customer_id")
    .agg(
        last_purchase_date=("invoice_date", "max"),
        frequency=("invoice_id", "nunique"),
        monetary=("quantity", lambda values: 0),
    )
    .reset_index()
)

# Calculate monetary value separately
feature_data["line_value"] = (
    feature_data["quantity"] * feature_data["unit_price"]
)

monetary_values = (
    feature_data.groupby("customer_id")["line_value"]
    .sum()
    .rename("monetary")
    .reset_index()
)

customer_features = customer_features.drop(columns=["monetary"]).merge(
    monetary_values,
    on="customer_id",
    how="left",
)

customer_features["recency_days"] = (
    reference_date - customer_features["last_purchase_date"].dt.normalize()
).dt.days

customer_features = customer_features.drop(columns=["last_purchase_date"])

# Define churn from observed purchases in the future window
purchasing_customers = set(observation_data["customer_id"].unique())

customer_features["churned"] = (
    ~customer_features["customer_id"].isin(purchasing_customers)
).astype(int)

# Save the dataset
output_file.parent.mkdir(parents=True, exist_ok=True)
customer_features.to_csv(output_file, index=False)

print(f"Feature cutoff: {feature_cutoff}")
print(f"Observation window: {observation_start.date()} to {observation_end.date()}")
print(f"Customers in dataset: {len(customer_features):,}")

print("\nChurn label counts (0 = retained, 1 = churned):")
print(customer_features["churned"].value_counts().sort_index().to_string())

print("\nChurn label percentages:")
print(
    (customer_features["churned"].value_counts(normalize=True) * 100)
    .sort_index()
    .round(2)
    .to_string()
)

print(f"\nDataset saved to: {output_file}")
print("\nNote: Churn here means no recorded purchase during the selected")
print("three-month observation window. It is a project-defined label.")
