from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

input_file = DATA_DIR / "churn_threshold_comparison.csv"
output_file = DATA_DIR / "churn_threshold_comparison.png"

df = pd.read_csv(input_file)

# Plot precision and recall at different thresholds
plt.figure(figsize=(9, 5))

plt.plot(
    df["threshold"],
    df["precision"],
    marker="o",
    label="Precision",
)

plt.plot(
    df["threshold"],
    df["recall"],
    marker="o",
    label="Recall",
)

plt.xlabel("Classification Threshold")
plt.ylabel("Score")
plt.title("RetailPulse - Churn Precision vs Recall")
plt.ylim(0, 1)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(output_file, dpi=200, bbox_inches="tight")
plt.close()

print("CHURN THRESHOLD CHART CREATED")
print("=============================")
print(f"Chart saved to: {output_file}")
print("\nThreshold metrics:")
print(df.round(4).to_string(index=False))
