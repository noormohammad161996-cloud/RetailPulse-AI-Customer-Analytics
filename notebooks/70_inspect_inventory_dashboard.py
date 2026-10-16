# File: notebooks/70_inspect_inventory_dashboard.py
# Purpose: Inspect the dashboard structure before making changes.

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_FILE = PROJECT_ROOT / "app" / "inventory_dashboard.py"

if not DASHBOARD_FILE.exists():
    raise FileNotFoundError(f"Dashboard not found: {DASHBOARD_FILE}")

content = DASHBOARD_FILE.read_text(encoding="utf-8")
lines = content.splitlines()

print("=" * 65)
print("RETAILPULSE - DASHBOARD STRUCTURE")
print("=" * 65)
print(f"\nTotal lines: {len(lines)}")

print("\nImports and configuration:")
for number, line in enumerate(lines, start=1):
    if number > 80:
        break
    if line.strip().startswith(
        ("import ", "from ", "st.set_page_config", "DATA_FILE", "DATA_PATH")
    ):
        print(f"{number:4}: {line}")

print("\nSection headings and dashboard components:")
for number, line in enumerate(lines, start=1):
    stripped = line.strip()
    if (
        stripped.startswith("#")
        or "st.title(" in stripped
        or "st.header(" in stripped
        or "st.subheader(" in stripped
        or "st.sidebar" in stripped
        or "st.download_button(" in stripped
    ):
        print(f"{number:4}: {stripped[:150]}")

print("\nDashboard inspection completed. No files were changed.")
