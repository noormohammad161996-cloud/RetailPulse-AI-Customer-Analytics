# File: notebooks/50_generate_inventory_analysis_report.py
# Purpose: Summarize inventory estimates and flag unusual results.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "improved_inventory_reorder_points.csv"
)
REPORT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "inventory_analysis_report.txt"
)
FLAGS_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "inventory_products_requiring_review.csv"
)

print("=" * 65)
print("RETAILPULSE - INVENTORY ANALYSIS REPORT")
print("=" * 65)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

# Flag estimates requiring additional review.
df["review_reason"] = ""

limited_history = df["months_with_sales"] < 6
df.loc[limited_history, "review_reason"] += (
    "Limited sales history; "
)

high_variability = df["demand_cv"] >= 1
df.loc[high_variability, "review_reason"] += (
    "High demand variability; "
)

extreme_safety_stock = (
    df["safety_stock_approx"] > 3 * df["expected_lead_time_demand"]
)
df.loc[extreme_safety_stock, "review_reason"] += (
    "Safety stock exceeds 3x expected lead-time demand; "
)

review_df = df[df["review_reason"] != ""].copy()

# Sort products by the largest safety-stock estimates.
review_df = review_df.sort_values(
    "safety_stock_approx", ascending=False
)

review_df.to_csv(FLAGS_FILE, index=False)

lines = [
    "RETAILPULSE - INVENTORY ANALYSIS REPORT",
    "=" * 50,
    "",
    f"Products assessed: {len(df):,}",
    f"Products flagged for review: {len(review_df):,}",
    "",
    "ASSUMPTIONS",
    "- Supplier lead time: 14 days",
    "- Service level: 95%",
    "- Demand estimated from historical sales",
    "- Actual inventory levels and supplier lead times unavailable",
    "",
    "IMPORTANT LIMITATIONS",
    "- Historical sales are not the same as true customer demand.",
    "- Stockout and product availability data are unavailable.",
    "- Monthly-to-daily variability conversion is approximate.",
    "- Reorder points are estimates, not purchase quantities.",
    "",
    "TOP 10 PRODUCTS REQUIRING REVIEW",
    "-" * 50,
]

columns = [
    "product_id",
    "product_name",
    "months_with_sales",
    "demand_cv",
    "expected_lead_time_demand",
    "safety_stock_approx",
    "reorder_point_approx",
    "review_reason",
]

for _, row in review_df[columns].head(10).iterrows():
    lines.append(
        f"\nProduct: {row['product_id']} - {row['product_name']}"
        f"\nMonths with sales: {row['months_with_sales']}"
        f"\nDemand CV: {row['demand_cv']}"
        f"\nExpected lead-time demand: "
        f"{row['expected_lead_time_demand']}"
        f"\nEstimated safety stock: {row['safety_stock_approx']}"
        f"\nEstimated reorder point: {row['reorder_point_approx']}"
        f"\nReview reason: {row['review_reason']}"
    )

REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

print(f"\nProducts assessed: {len(df):,}")
print(f"Products flagged for review: {len(review_df):,}")
print(f"Report saved to: {REPORT_FILE}")
print(f"Review dataset saved to: {FLAGS_FILE}")

print("\n--- TOP 10 PRODUCTS REQUIRING REVIEW ---")
print(review_df[columns].head(10).to_string(index=False))

print("\nInventory report generation completed.")
