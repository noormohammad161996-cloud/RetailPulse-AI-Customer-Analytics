# File: notebooks/65_inspect_inventory_reorder_points.py
# Purpose: Inspect existing inventory reorder-point calculations.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

FILES_TO_CHECK = [
    "improved_inventory_demand_metrics.csv",
    "inventory_reorder_points.csv",
    "improved_reorder_points.csv",
]

print("=" * 70)
print("RETAILPULSE - INVENTORY REORDER-POINT INSPECTION")
print("=" * 70)

for filename in FILES_TO_CHECK:
    file_path = DATA_DIR / filename

    print(f"\n{'-' * 60}")
    print("File:", filename)

    if not file_path.exists():
        print("Status: File not found")
        continue

    df = pd.read_csv(file_path)

    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("\nFirst three records:")
    print(df.head(3).to_string(index=False))

print("\nInspection completed.")
