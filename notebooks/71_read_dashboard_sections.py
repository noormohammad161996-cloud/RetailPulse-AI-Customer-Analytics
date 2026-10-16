# File: notebooks/71_read_dashboard_sections.py
# Purpose: Print the dashboard source code in three sections.

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_FILE = PROJECT_ROOT / "app" / "inventory_dashboard.py"

if not DASHBOARD_FILE.exists():
    raise FileNotFoundError(f"Dashboard not found: {DASHBOARD_FILE}")

lines = DASHBOARD_FILE.read_text(encoding="utf-8").splitlines()

for start, end in [(1, 70), (71, 130), (131, 200)]:
    print(f"\n{'=' * 20} LINES {start}-{end} {'=' * 20}")
    for number in range(start, min(end, len(lines)) + 1):
        print(f"{number:4}: {lines[number - 1]}")

print("\nInspection completed. No files were changed.")
