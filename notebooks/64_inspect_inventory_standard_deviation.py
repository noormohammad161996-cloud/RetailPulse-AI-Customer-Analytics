# File: notebooks/64_inspect_inventory_standard_deviation.py
# Purpose: Inspect real demand variability metrics used in inventory planning.

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "improved_inventory_demand_metrics.csv"
)

print("=" * 65)
print("RETAILPULSE - INVENTORY STANDARD DEVIATION REVIEW")
print("=" * 65)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Required file not found: {INPUT_FILE}\n"
        "Run the earlier inventory-demand preparation programs first."
    )

df = pd.read_csv(INPUT_FILE)

print("\nDataset shape:", df.shape)
print("\nAvailable columns:")
print(df.columns.tolist())

print("\nFirst five records:")
print(df.head().to_string(index=False))

std_columns = [
    column for column in df.columns
    if "std" in column.lower() or "standard_deviation" in column.lower()
]

if std_columns:
    print("\nStandard-deviation-related columns:")
    for column in std_columns:
        print(f"\n{column}")
        print(df[column].describe().to_string())
else:
    print(
        "\nNo obvious standard deviation column was found. "
        "We will inspect the actual column names before calculating anything."
    )

print("\nInventory variability inspection completed.")
