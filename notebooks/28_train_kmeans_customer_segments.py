from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Input and output paths
input_file = PROJECT_ROOT / "data" / "processed" / "customer_kmeans_features.csv"
output_file = PROJECT_ROOT / "data" / "processed" / "customer_kmeans_clusters.csv"
metrics_file = PROJECT_ROOT / "data" / "processed" / "kmeans_model_comparison.csv"
summary_file = PROJECT_ROOT / "data" / "processed" / "kmeans_cluster_summary.csv"

# Load prepared customer data
df = pd.read_csv(input_file)

# Use standardized features only
feature_columns = [
    "recency_scaled",
    "frequency_scaled",
    "monetary_scaled",
]
X = df[feature_columns]

# Test different numbers of clusters
results = []

print("TESTING K-MEANS CLUSTER COUNTS")
print("==============================")

for k in range(2, 9):
    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10,
    )

    labels = model.fit_predict(X)
    score = silhouette_score(X, labels)

    results.append({
        "number_of_clusters": k,
        "silhouette_score": score,
        "inertia": model.inertia_,
    })

    print(f"k={k}: silhouette score = {score:.4f}")

# Save comparison metrics
metrics = pd.DataFrame(results)
metrics.to_csv(metrics_file, index=False)

# Choose the highest silhouette score as the initial candidate
best_k = int(
    metrics.loc[metrics["silhouette_score"].idxmax(), "number_of_clusters"]
)

print(f"\nBest candidate by silhouette score: k={best_k}")

# Train the final candidate model
final_model = KMeans(
    n_clusters=best_k,
    random_state=42,
    n_init=10,
)

df["cluster"] = final_model.fit_predict(X)

# Save customer-level assignments
df.to_csv(output_file, index=False)

# Summarize each cluster using original RFM values
summary = (
    df.groupby("cluster")
    .agg(
        customer_count=("customer_id", "size"),
        average_recency_days=("recency_days", "mean"),
        average_frequency=("frequency", "mean"),
        average_monetary=("monetary", "mean"),
        total_monetary=("monetary", "sum"),
    )
    .round(2)
    .reset_index()
)

summary.to_csv(summary_file, index=False)

print("\nCLUSTER SUMMARY")
print("===============")
print(summary.to_string(index=False))

print("\nFiles saved:")
print(f"Model comparison: {metrics_file}")
print(f"Customer clusters: {output_file}")
print(f"Cluster summary: {summary_file}")

print(
    "\nReminder: the highest silhouette score is an initial candidate, "
    "not proof that the clusters are the most useful for the business."
)
