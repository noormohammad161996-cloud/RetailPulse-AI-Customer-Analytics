
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "interim" / "retail_combined.parquet"

def main():
    data = pd.read_parquet(DATA_PATH)

    print("RETAILPULSE - WORKSHEET OVERLAP VERIFICATION")
    print(f"\nTotal rows: {len(data):,}")

    print("\nRows by source worksheet:")
    print(data["source_sheet"].value_counts().to_string())

    print("\nDate ranges by source worksheet:")
    for sheet_name, frame in data.groupby("source_sheet"):
        print(
            f"{sheet_name}: "
            f"{frame['invoice_date'].min()} to "
            f"{frame['invoice_date'].max()}"
        )

    overlap_start = pd.Timestamp("2010-12-01")
    overlap_end = pd.Timestamp("2010-12-10")

    overlap_rows = data[
        data["invoice_date"].ge(overlap_start)
        & data["invoice_date"].lt(overlap_end)
    ]

    print("\nRows dated Dec 1–9, 2010, by worksheet:")
    print(overlap_rows["source_sheet"].value_counts().to_string())

    print("\nVerification complete. No data was changed.")

if __name__ == "__main__":
    main()
