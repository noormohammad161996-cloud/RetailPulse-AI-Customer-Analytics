
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "retail_deduplicated.parquet"

EXPECTED_ROWS = 1_044_848


def main():
    print("RETAILPULSE - CLEANED DATA VALIDATION")
    print("=" * 42)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    data = pd.read_parquet(DATA_PATH)

    print(f"\nTotal rows: {len(data):,}")
    print(f"Total columns: {len(data.columns)}")
    print(f"Expected rows: {EXPECTED_ROWS:,}")
    print(f"Row count check: {'PASS' if len(data) == EXPECTED_ROWS else 'FAIL'}")

    print("\nDate range:")
    print(f"Earliest: {data['invoice_date'].min()}")
    print(f"Latest:   {data['invoice_date'].max()}")

    print("\nMissing values:")
    print(data.isna().sum().to_string())

    print("\nExact duplicate rows across transaction fields:")
    transaction_columns = [
        "invoice_id",
        "product_id",
        "product_name",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
    ]
    duplicate_count = int(
        data.duplicated(subset=transaction_columns, keep="first").sum()
    )
    print(f"Duplicate occurrences: {duplicate_count:,}")

    print("\nTransaction checks:")
    print(f"Quantity <= 0: {(data['quantity'] <= 0).sum():,}")
    print(f"Unit price <= 0: {(data['unit_price'] <= 0).sum():,}")
    print(
        "Cancellation-style invoice IDs: "
        f"{data['invoice_id'].astype(str).str.startswith('C').sum():,}"
    )

    print("\nRows by source worksheet:")
    print(data["source_sheet"].value_counts().to_string())

    print("\nValidation finished. No data was changed.")


if __name__ == "__main__":
    main()
