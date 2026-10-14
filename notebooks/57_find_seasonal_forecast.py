# File: notebooks/57_find_seasonal_forecast.py
# Purpose: Find existing seasonal-naive forecast files in the project.

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

print("=" * 65)
print("RETAILPULSE - SEARCH FOR SEASONAL FORECAST OUTPUTS")
print("=" * 65)

keywords = ("seasonal", "forecast", "rolling")

matches = []

for folder_name in ("data", "notebooks", "models", "src"):
    folder = PROJECT_ROOT / folder_name

    if not folder.exists():
        continue

    for path in folder.rglob("*"):
        if not path.is_file():
            continue

        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue

        if any(word in path.name.lower() for word in keywords):
            matches.append(path)

if matches:
    for path in sorted(matches):
        print(path.relative_to(PROJECT_ROOT))
else:
    print("No matching forecast files found.")

print("\nSearch completed.")
