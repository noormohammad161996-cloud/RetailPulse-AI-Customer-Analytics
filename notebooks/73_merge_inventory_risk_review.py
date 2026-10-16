# File: notebooks/73_merge_inventory_risk_review.py
# Purpose: Merge risk-review categories into a separate dashboard dataset.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

DASHBOARD_FILE = DATA_DIR / "inventory_dashboard_data.csv"
RISK_FILE = DATA_DIR / "inventory_risk_review.csv"
OUTPUT_FILE = DATA_DIR / "inventory_dashboard_with_risk_review.csv"

for path in [DASHBOARD_FILE, RISK_FILE]:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

dashboard = pd.read_csv(DASHBOARD_FILE, dtype={"product_id": str})
risk = pd.read_csv(RISK_FILE, dtype={"product_id": str})

# Keep only the new risk-review fields needed for the merge.
risk_columns = [
    "product_id",
    "risk_review_category",
]

risk_subset = risk[risk_columns].copy()

merged = dashboard.merge(
    risk_subset,
    on="product_id",
    how="left",
    validate="one_to_one",
    indicator=True,
)

unmatched = (merged["_merge"] != "both").sum()
merged = merged.drop(columns=["_merge"])

if unmatched:
    raise ValueError(f"{unmatched} dashboard products were not matched.")

if len(merged) != len(dashboard):
    raise ValueError("The merge unexpectedly changed the dashboard row count.")

if merged["risk_review_category"].isna().any():
    raise ValueError("Some products have missing risk-review categories.")

merged.to_csv(OUTPUT_FILE, index=False)

print("=" * 65)
print("RETAILPULSE - RISK-REVIEW DATASET MERGE")
print("=" * 65)
print("Original dashboard rows:", len(dashboard))
print("Merged dataset rows:", len(merged))
print("Matched products:", len(merged))
print("Unmatched products:", unmatched)
print("\nRisk-review category counts:")
print(merged["risk_review_category"].value_counts().to_string())
print(f"\nSaved to: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")
print("\nMerge completed successfully.")
