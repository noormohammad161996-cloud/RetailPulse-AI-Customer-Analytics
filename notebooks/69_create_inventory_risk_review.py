# File: notebooks/69_create_inventory_risk_review.py
# Purpose: Flag inventory estimates needing additional review.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_FILE = DATA_DIR / "improved_inventory_reorder_points.csv"
OUTPUT_CSV = DATA_DIR / "inventory_risk_review.csv"
OUTPUT_REPORT = DATA_DIR / "inventory_risk_review_report.txt"

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

# These are review rules for this project, not universal industry standards.
def classify_product(row):
    if row["months_with_sales"] < 6:
        return "Insufficient sales history"
    if row["demand_cv"] >= 3:
        return "High demand variability"
    if row["demand_cv"] >= 2:
        return "Moderate-to-high demand variability"
    return "Lower relative variability"

df["risk_review_category"] = df.apply(classify_product, axis=1)

# Put products needing the most attention first.
df = df.sort_values(
    ["months_with_sales", "demand_cv"],
    ascending=[True, False],
)

review_columns = [
    "product_id",
    "product_name",
    "months_with_sales",
    "average_monthly_demand",
    "monthly_demand_std",
    "demand_cv",
    "expected_lead_time_demand",
    "safety_stock_approx",
    "reorder_point_approx",
    "recommendation_status",
    "risk_review_category",
]

df[review_columns].to_csv(OUTPUT_CSV, index=False)

counts = df["risk_review_category"].value_counts()
lines = [
    "RETAILPULSE - INVENTORY RISK REVIEW",
    "=" * 45,
    f"Products analyzed: {len(df):,}",
    "",
    "Review categories:",
]

for category, count in counts.items():
    lines.append(f"{category}: {count:,}")

lines.extend([
    "",
    "Interpretation and limitations:",
    "- Categories are preliminary review flags, not proven stockout risks.",
    "- Fewer than six sales months indicates limited observed sales history.",
    "- High CV indicates variability relative to average recorded demand.",
    "- Recorded sales do not establish actual stock on hand.",
    "- Lead time and service-level assumptions require business validation.",
])

OUTPUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("\nInventory review completed.")
print("\nCategory counts:")
print(counts.to_string())
print(f"\nCSV saved to: {OUTPUT_CSV.relative_to(PROJECT_ROOT)}")
print(f"Report saved to: {OUTPUT_REPORT.relative_to(PROJECT_ROOT)}")
print("\nFirst ten flagged products:")
print(df[review_columns].head(10).to_string(index=False))
