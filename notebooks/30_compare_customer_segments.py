from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

rules_file = DATA_DIR / "customer_segments.csv"
kmeans_file = DATA_DIR / "customer_kmeans_clusters.csv"

output_file = DATA_DIR / "customer_segmentation_comparison.csv"

# Load both segmentation outputs
rules = pd.read_csv(rules_file)
kmeans = pd.read_csv(kmeans_file)

# Confirm both datasets contain customer IDs
if "customer_id" not in rules.columns or "customer_id" not in kmeans.columns:
    raise ValueError("customer_id column is missing from one of the files.")

# Select the required columns
rules = rules[["customer_id", "segment"]].copy()
kmeans = kmeans[["customer_id", "cluster"]].copy()

# Ensure customer IDs use a consistent type
rules["customer_id"] = pd.to_numeric(rules["customer_id"], errors="coerce")
kmeans["customer_id"] = pd.to_numeric(kmeans["customer_id"], errors="coerce")

rules = rules.dropna(subset=["customer_id"])
kmeans = kmeans.dropna(subset=["customer_id"])

# Merge the two methods by customer ID
comparison = rules.merge(
    kmeans,
    on="customer_id",
    how="inner",
    validate="one_to_one",
)

# Count each rule-based segment within each K-Means cluster
cross_tab = pd.crosstab(
    comparison["segment"],
    comparison["cluster"],
)

comparison.to_csv(output_file, index=False)

print("CUSTOMER SEGMENTATION COMPARISON")
print("================================")
print(f"Customers compared: {len(comparison):,}")
print(f"Rule-based segments: {comparison['segment'].nunique()}")
print(f"K-Means clusters: {comparison['cluster'].nunique()}")

print("\nRule-based segments by K-Means cluster:")
print(cross_tab.to_string())

print(f"\nCustomer-level comparison saved to: {output_file}")
