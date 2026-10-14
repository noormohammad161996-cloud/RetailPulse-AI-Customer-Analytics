
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"

COLUMN_MAPPING = {
    "Invoice": "invoice_id",
    "StockCode": "product_id",
    "Description": "product_name",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "unit_price",
    "Customer ID": "customer_id",
    "Country": "country",
}


def load_retail_data():
    """Load and combine both original Excel worksheets."""

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {RAW_DATA_PATH}")

    sheets = pd.read_excel(RAW_DATA_PATH, sheet_name=None)
    frames = []

    for sheet_name, df in sheets.items():
        df.columns = df.columns.str.strip()
        df = df.rename(columns=COLUMN_MAPPING)

        # Use consistent text types for identifiers and text fields.
        df["invoice_id"] = df["invoice_id"].astype("string")
        df["product_id"] = df["product_id"].astype("string")
        df["product_name"] = df["product_name"].astype("string")
        df["country"] = df["country"].astype("string")

        # Preserve the original worksheet name.
        df["source_sheet"] = sheet_name
        frames.append(df)

        print(f"Loaded worksheet: {sheet_name} ({len(df):,} rows)")

    return pd.concat(frames, ignore_index=True)


def save_interim_data(data):
    """Save combined data without removing any records."""

    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = INTERIM_DATA_DIR / "retail_combined.parquet"

    data.to_parquet(output_path, index=False)

    print(f"\nSaved intermediate data to: {output_path}")
    print(f"Combined rows: {len(data):,}")
    print(f"Columns: {list(data.columns)}")


def main():
    print("RETAILPULSE - DATA INGESTION")
    print("=" * 40)

    data = load_retail_data()
    save_interim_data(data)

    print("\nData ingestion completed successfully.")


if __name__ == "__main__":
    main()
