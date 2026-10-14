from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Input and output paths
input_file = PROJECT_ROOT / "data" / "processed" / "kmeans_cluster_summary.csv"
output_file = PROJECT_ROOT / "data" / "processed" / "kmeans_cluster_chart.png"

# Load cluster summary
df = pd.read_csv(input_file)

# Plot customer counts
plt.figure(figsize=(9, 5))
bars = plt.bar(
    df["cluster"].astype(str),
    df["customer_count"],
)

plt.title("RetailPulse - K-Means Customer Clusters", fontsize=14, fontweight="bold")
plt.xlabel("Cluster")
plt.ylabel("Number of Customers")

# Add count labels
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{int(height):,}",
        ha="center",
        va="bottom",
    )

plt.tight_layout()
plt.savefig(output_file, dpi=200, bbox_inches="tight")
plt.close()

print("K-MEANS CLUSTER CHART CREATED")
print("=============================")
print(f"Chart saved to: {output_file}")
print("\nCluster customer counts:")
print(df[["cluster", "customer_count"]].to_string(index=False))
