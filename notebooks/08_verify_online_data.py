from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "interim" / "retail_combined.parquet"


def main():
    print("RETAILPULSE - ONLINE DATA VERIFICATION")
    print("=" * 45)

    if not DATA_PATH.exists():
        print(f"Data file not found: {DATA_PATH}")
        print("Please check the file path before continuing.")
        return

    data = pd.read_parquet(DATA_PATH)

    print(f"\nFile: {DATA_PATH}")
    print(f"Total rows: {len(data):,}")
    print(f"Total columns: {len(data.columns)}")

    print("\nColumns:")
    print(data.columns.tolist())

    print("\nMissing values:")
    print(data.isna().sum().to_string())

    print("\nDate range:")
    print(f"Start: {data['invoice_date'].min()}")
    print(f"End:   {data['invoice_date'].max()}")

    print("\nRows by worksheet:")
    print(data["source_sheet"].value_counts().to_string())

    print("\nSample records:")
    print(data.head(5).to_string(index=False))

    print("\nVerification complete. No data was changed.")


if __name__ == "__main__":
    main()