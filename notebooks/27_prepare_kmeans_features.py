from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Find the project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Define input and output files
input_file = PROJECT_ROOT / "data" / "processed" / "customer_rfm.csv"
output_file = PROJECT_ROOT / "data" / "processed" / "customer_kmeans_features.csv"

# Load the customer RFM data
df = pd.read_csv(input_file)

# Select the required columns
features = ["recency_days", "frequency", "monetary"]

# Remove rows with missing or invalid values
df = df.dropna(subset=features).copy()
df = df[
    (df["recency_days"] >= 0)
    & (df["frequency"] > 0)
    & (df["monetary"] > 0)
].copy()

# Reduce skew in frequency and monetary values
df["log_frequency"] = np.log1p(df["frequency"])
df["log_monetary"] = np.log1p(df["monetary"])

# Features that will be used by K-Means
model_features = ["recency_days", "log_frequency", "log_monetary"]

# Standardize the features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[model_features])

df[["recency_scaled", "frequency_scaled", "monetary_scaled"]] = scaled_features

# Save the prepared data
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("K-MEANS FEATURES PREPARED")
print("=========================")
print(f"Customers prepared: {len(df):,}")
print(f"Output saved to: {output_file}")

print("\nScaled feature statistics:")
print(
    df[["recency_scaled", "frequency_scaled", "monetary_scaled"]]
    .describe()
    .round(3)
)
