from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

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


def main():
    print("=" * 60)
    print("RETAILPULSE - COMBINED DATASET PROFILE")
    print("=" * 60)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    # Load each worksheet and combine them
    sheets = pd.read_excel(DATA_PATH, sheet_name=None)

    frames = []
    for sheet_name, frame in sheets.items():
        frame.columns = frame.columns.str.strip()
        frame = frame.rename(columns=COLUMN_MAPPING)
        frame["source_sheet"] = sheet_name
        frames.append(frame)

    df = pd.concat(frames, ignore_index=True)

    # Derived fields for analysis; original columns remain unchanged in meaning
    df["is_cancellation"] = (
        df["invoice_id"].astype(str).str.strip().str.upper().str.startswith("C")
    )
    df["line_value"] = df["quantity"] * df["unit_price"]

    print(f"\nCombined rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Unique invoices: {df['invoice_id'].nunique():,}")
    print(f"Unique products: {df['product_id'].nunique():,}")
    print(f"Unique identified customers: {df['customer_id'].nunique():,}")
    print(f"Date range: {df['invoice_date'].min()} to {df['invoice_date'].max()}")

    print("\nStandardized columns:")
    print(df.columns.tolist())

    print("\nMissing values:")
    print(df.isna().sum().to_string())

    print("\nDuplicate rows across combined data (excluding source_sheet):")
    business_columns = list(COLUMN_MAPPING.values())
    print(f"{df.duplicated(subset=business_columns).sum():,}")

    print("\nCancellation-style invoice rows:")
    print(f"{df['is_cancellation'].sum():,}")

    print("\nQuantity and price checks:")
    print(f"Quantity <= 0: {(df['quantity'] <= 0).sum():,}")
    print(f"Unit price <= 0: {(df['unit_price'] <= 0).sum():,}")

    print(f"\nNet line value (not verified revenue): {df['line_value'].sum():,.2f}")

    print("\nTop 10 countries by transaction-row count:")
    print(df["country"].value_counts().head(10).to_string())

    print("\nCombined profile completed.")
    print("No files were modified or deleted.")


if __name__ == "__main__":
    main()