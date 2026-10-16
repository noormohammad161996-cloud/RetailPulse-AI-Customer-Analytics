# File: notebooks/66_find_inventory_outputs.py
# Purpose: Find existing inventory outputs and calculation scripts.

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

print("=" * 65)
print("RETAILPULSE - INVENTORY FILE DISCOVERY")
print("=" * 65)

print("\nInventory-related processed data files:")
for path in sorted(DATA_DIR.glob("*")):
    if any(word in path.name.lower() for word in
           ["inventory", "reorder", "demand", "product"]):
        print(f"{path.name} ({path.stat().st_size:,} bytes)")

print("\nScripts mentioning reorder points or safety stock:")
keywords = ["reorder", "safety_stock", "lead_time"]

for path in sorted(NOTEBOOKS_DIR.glob("*.py")):
    try:
        content = path.read_text(encoding="utf-8").lower()
        matches = [word for word in keywords if word in content]
        if matches:
            print(f"{path.name}: {', '.join(matches)}")
    except (OSError, UnicodeDecodeError) as error:
        print(f"Could not inspect {path.name}: {error}")

print("\nFile discovery completed.")
