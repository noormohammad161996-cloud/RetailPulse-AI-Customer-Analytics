# File: notebooks/72_check_inventory_dataset_compatibility.py
# Purpose: Check whether dashboard and risk-review data can be joined.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

DASHBOARD_FILE = DATA_DIR / "inventory_dashboard_data.csv"
RISK_FILE = DATA_DIR / "inventory_risk_review.csv"

for path in [DASHBOARD_FILE, RISK_FILE]:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

dashboard = pd.read_csv(DASHBOARD_FILE, dtype={"product_id": str})
risk = pd.read_csv(RISK_FILE, dtype={"product_id": str})

print("=" * 65)
print("RETAILPULSE - DATASET COMPATIBILITY CHECK")
print("=" * 65)

print("\nDashboard dataset shape:", dashboard.shape)
print("Risk-review dataset shape:", risk.shape)

print("\nDashboard product ID duplicates:",
      dashboard["product_id"].duplicated().sum())
print("Risk-review product ID duplicates:",
      risk["product_id"].duplicated().sum())

dashboard_ids = set(dashboard["product_id"].dropna())
risk_ids = set(risk["product_id"].dropna())

print("\nDashboard unique product IDs:", len(dashboard_ids))
print("Risk-review unique product IDs:", len(risk_ids))
print("IDs present in both:", len(dashboard_ids & risk_ids))
print("Dashboard IDs missing from risk review:",
      len(dashboard_ids - risk_ids))
print("Risk-review IDs missing from dashboard:",
      len(risk_ids - dashboard_ids))

print("\nRisk-review columns:")
print(risk.columns.tolist())

print("\nCompatibility check completed. No files were changed.")
