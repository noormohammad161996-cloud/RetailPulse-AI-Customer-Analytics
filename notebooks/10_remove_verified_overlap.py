
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "interim" / "retail_combined.parquet"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "retail_deduplicated.parquet"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "overlap_removal_report.txt"


def main():
    print("RETAILPULSE - VERIFIED OVERLAP CLEANING")
    print("=" * 45)

    data = pd.read_parquet(INPUT_PATH)
    original_rows = len(data)

    start_date = pd.Timestamp("2010-12-01")
    end_date = pd.Timestamp("2010-12-10")

    overlap_mask = (
        data["invoice_date"].ge(start_date)
        & data["invoice_date"].lt(end_date)
    )

    first_sheet = data[
        overlap_mask & (data["source_sheet"] == "Year 2009-2010")
    ]
    second_sheet = data[
        overlap_mask & (data["source_sheet"] == "Year 2010-2011")
    ]

    # Stop if the previously verified overlap has unexpectedly changed.
    if len(first_sheet) != 22523 or len(second_sheet) != 22523:
        raise ValueError(
            "Overlap counts differ from verification. "
            "No cleaned output was created."
        )

    # Remove only the verified duplicate date window from the second sheet.
    remove_mask = (
        overlap_mask
        & (data["source_sheet"] == "Year 2010-2011")
    )

    cleaned = data.loc[~remove_mask].copy()
    removed_rows = original_rows - len(cleaned)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_parquet(OUTPUT_PATH, index=False)

    report = [
        "RETAILPULSE - OVERLAP REMOVAL REPORT",
        "=" * 38,
        f"Input rows: {original_rows:,}",
        f"Rows in first sheet's overlap window: {len(first_sheet):,}",
        f"Rows in second sheet's overlap window: {len(second_sheet):,}",
        f"Rows removed from second sheet: {removed_rows:,}",
        f"Output rows: {len(cleaned):,}",
        "Rule: Retain the first worksheet's copies for the verified overlap.",
        "Missing customer IDs and product names were not removed.",
        f"Output file: {OUTPUT_PATH}",
        "Original input file was not modified.",
    ]

    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\n".join(report))
    print("\nCleaning complete.")


if __name__ == "__main__":
    main()
