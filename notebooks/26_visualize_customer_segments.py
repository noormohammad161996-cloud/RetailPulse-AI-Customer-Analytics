from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Input and output files
input_file = PROJECT_ROOT / "data" / "processed" / "customer_segment_summary.csv"
output_file = PROJECT_ROOT / "data" / "processed" / "customer_segments_chart.png"

# Load the segment summary
df = pd.read_csv(input_file)

# Sort segments by customer count
df = df.sort_values("customer_count", ascending=True)

# Create the chart
plt.figure(figsize=(11, 6))
bars = plt.barh(df["segment"], df["customer_count"])

plt.title("RetailPulse - Customer Segment Distribution", fontsize=15, fontweight="bold")
plt.xlabel("Number of Customers", fontsize=12)
plt.ylabel("Customer Segment", fontsize=12)

# Display customer counts at the end of each bar
for bar in bars:
    width = bar.get_width()
    plt.text(
        width + 15,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width):,}",
        va="center",
        fontsize=10,
    )

plt.tight_layout()

# Save the chart
plt.savefig(output_file, dpi=200, bbox_inches="tight")
plt.close()

print("CUSTOMER SEGMENT CHART CREATED")
print("================================")
print(f"Segments displayed: {len(df)}")
print(f"Chart saved to: {output_file}")
print("\nCustomer counts:")
print(df[["segment", "customer_count"]].to_string(index=False))
