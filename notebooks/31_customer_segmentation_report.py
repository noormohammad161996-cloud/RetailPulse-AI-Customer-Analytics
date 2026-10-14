from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

comparison_file = DATA_DIR / "customer_segmentation_comparison.csv"
cluster_summary_file = DATA_DIR / "kmeans_cluster_summary.csv"
output_file = DATA_DIR / "customer_segmentation_report.txt"

comparison = pd.read_csv(comparison_file)
cluster_summary = pd.read_csv(cluster_summary_file)

lines = [
    "RETAILPULSE - CUSTOMER SEGMENTATION REPORT",
    "=" * 45,
    "",
    f"Customers compared: {len(comparison):,}",
    f"Rule-based segments: {comparison['segment'].nunique()}",
    f"K-Means clusters: {comparison['cluster'].nunique()}",
    "",
    "RULE-BASED SEGMENTS BY K-MEANS CLUSTER",
    "-" * 40,
]

cross_tab = pd.crosstab(comparison["segment"], comparison["cluster"])
lines.append(cross_tab.to_string())

lines.extend([
    "",
    "K-MEANS CLUSTER SUMMARY",
    "-" * 25,
    cluster_summary.to_string(index=False),
    "",
    "INTERPRETATION",
    "-" * 15,
    "Cluster 0 contains all recent loyal and recent high-value customers",
    "under the current rule-based definitions.",
    "Cluster 1 contains most one-time customers.",
    "At-risk and other customers are distributed across both clusters.",
    "",
    "LIMITATIONS",
    "-" * 12,
    "These results describe historical customer behavior.",
    "The cluster count was selected using the highest silhouette score",
    "among k=2 through k=8; business usefulness needs separate evaluation.",
    "Customer segments do not establish future churn or predict future purchases.",
])

output_file.write_text("\n".join(lines), encoding="utf-8")

print("CUSTOMER SEGMENTATION REPORT CREATED")
print("====================================")
print(f"Report saved to: {output_file}")
print("\nReport preview:\n")
print("\n".join(lines))
