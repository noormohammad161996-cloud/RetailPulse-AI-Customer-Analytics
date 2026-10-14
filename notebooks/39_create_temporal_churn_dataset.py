from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

input_file = DATA_DIR / "sales_analysis.parquet"
output_file = DATA_DIR / "temporal_churn_validation.csv"

feature_cutoff = pd.Timestamp("2010-12-31 23:59:59")
observation_start = pd.Timestamp("2011-01-01 00:00:00")
observation_end = pd.Timestamp("2011-03-31 23:59:59")

df = pd.read_parquet(input_file)

df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")

df = df.dropna(subset=["customer_id", "invoice_date"]).copy()

# Historical feature window
features_data = df[df["invoice_date"] <= feature_cutoff].copy()

# Future observation window used only for labels
future_data = df[
    (df["invoice_date"] >= observation_start)
    & (df["invoice_date"] <= observation_end)
].copy()

if features_data.empty or future_data.empty:
    raise ValueError("Feature or observation window contains no transactions.")

# Build customer features using only the feature window
features_data["line_value"] = (
    features_data["quantity"] * features_data["unit_price"]
)

customers = (
    features_data.groupby("customer_id")
    .agg(
        last_purchase=("invoice_date", "max"),
        frequency=("invoice_id", "nunique"),
        monetary=("line_value", "sum"),
    )
    .reset_index()
)

customers["recency_days"] = (
    (feature_cutoff.normalize() + pd.Timedelta(days=1))
    - customers["last_purchase"].dt.normalize()
).dt.days

customers = customers.drop(columns=["last_purchase"])

# Define the outcome using the future window
future_customer_ids = set(future_data["customer_id"].unique())

customers["churned"] = (
    ~customers["customer_id"].isin(future_customer_ids)
).astype(int)

# Save the separate temporal cohort
customers.to_csv(output_file, index=False)

print("TEMPORAL CHURN VALIDATION DATASET CREATED")
print("=========================================")
print(f"Feature cutoff: {feature_cutoff.date()}")
print(f"Observation window: {observation_start.date()} to {observation_end.date()}")
print(f"Customers: {len(customers):,}")

print("\nLabel counts (0 = retained, 1 = churned):")
print(customers["churned"].value_counts().sort_index().to_string())

print(f"\nSaved to: {output_file}")
print(
    "\nThis is an earlier historical cohort. It is not yet a model "
    "evaluation result."
)
