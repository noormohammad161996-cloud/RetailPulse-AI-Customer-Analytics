from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"


def analyse_sheet(sheet_name):
    print("\n" + "=" * 60)
    print(f"DATA QUALITY REPORT: {sheet_name}")
    print("=" * 60)

    # Load one worksheet at a time to limit memory usage
    df = pd.read_excel(DATA_PATH, sheet_name=sheet_name)

    # Remove accidental spaces from column names for reliable access
    df.columns = df.columns.str.strip()

    # Basic counts
    print(f"Total rows: {len(df):,}")
    print(f"Unique invoices: {df['Invoice'].nunique():,}")
    print(f"Unique products: {df['StockCode'].nunique():,}")
    print(f"Unique identified customers: {df['Customer ID'].nunique():,}")

    # Date range
    print(f"\nFirst transaction date: {df['InvoiceDate'].min()}")
    print(f"Last transaction date:  {df['InvoiceDate'].max()}")

    # Missing values
    print("\nMissing customer IDs:", f"{df['Customer ID'].isna().sum():,}")
    print("Missing descriptions:", f"{df['Description'].isna().sum():,}")

    # Potential cancellations
    invoice_text = df["Invoice"].astype(str).str.strip()
    cancelled = invoice_text.str.upper().str.startswith("C")
    print("\nInvoices with cancellation-style IDs:", f"{cancelled.sum():,}")

    # Quantity and price checks
    print("Zero or negative quantities:", f"{(df['Quantity'] <= 0).sum():,}")
    print("Zero or negative prices:", f"{(df['Price'] <= 0).sum():,}")

    # Transaction value estimate; not yet a verified accounting total
    df["line_value"] = df["Quantity"] * df["Price"]
    print(f"\nNet line value (Quantity x Price): {df['line_value'].sum():,.2f}")

    # Duplicate rows
    print("Duplicate rows:", f"{df.duplicated().sum():,}")

    del df


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    workbook = pd.ExcelFile(DATA_PATH)
    print("RETAILPULSE - DATA QUALITY ANALYSIS")

    for sheet_name in workbook.sheet_names:
        analyse_sheet(sheet_name)

    print("\nData quality analysis completed.")
    print("Original Excel workbook was not modified.")


if __name__ == "__main__":
    main()