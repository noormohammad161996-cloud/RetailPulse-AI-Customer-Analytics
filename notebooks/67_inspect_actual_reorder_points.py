# File: notebooks/67_inspect_actual_reorder_points.py
# Purpose: Inspect the existing reorder-point output.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "improved_inventory_reorder_points.csv"
)

print("=" * 70)
print("RETAILPULSE - ACTUAL REORDER-POINT REVIEW")
print("=" * 70)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Output file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

print("\nDataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nFirst five records:")
print(df.head().to_string(index=False))

print("\nNumeric column summary:")
print(df.describe().round(2).to_string())

print("\nMissing values by column:")
print(df.isna().sum().to_string())

print("\nInspection completed.")
