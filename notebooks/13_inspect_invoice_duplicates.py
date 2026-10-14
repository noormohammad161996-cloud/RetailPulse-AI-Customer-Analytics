from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"
CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "retail_deduplicated.parquet"

TARGET_INVOICE = "489517"

COLUMNS = [
    "invoice_id",
    "product_id",
    "product_name",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
]


def main():
    print("RETAILPULSE - RAW INVOICE INVESTIGATION")
    print("=" * 43)

    cleaned = pd.read_parquet(CLEAN_PATH)
    invoice_rows = cleaned[
        cleaned["invoice_id"].astype(str) == TARGET_INVOICE
    ]

    print(f"\nCombined dataset: {len(invoice_rows)} rows for invoice {TARGET_INVOICE}")
    print(invoice_rows[COLUMNS].to_string(index=False))

    print("\nRepeated product lines in this invoice:")
    repeated = (
        invoice_rows.groupby(
            ["product_id", "product_name", "quantity", "unit_price"],
            dropna=False,
        )
        .size()
        .reset_index(name="occurrences")
    )
    repeated = repeated[repeated["occurrences"] > 1]
    print(
        repeated.to_string(index=False)
        if not repeated.empty
        else "No repeated product lines found."
    )

    print("\nChecking the original Excel worksheets...")
    for sheet in ["Year 2009-2010", "Year 2010-2011"]:
        raw = pd.read_excel(
            RAW_PATH,
            sheet_name=sheet,
            usecols=[
                "Invoice",
                "StockCode",
                "Description",
                "Quantity",
                "InvoiceDate",
                "Price",
                "Customer ID",
                "Country",
            ],
        )

        raw["Invoice"] = raw["Invoice"].astype(str)
        source_invoice = raw[raw["Invoice"] == TARGET_INVOICE]

        print(f"\n{sheet}: {len(source_invoice)} rows")
        if not source_invoice.empty:
            print(source_invoice.to_string(index=False))

    print("\nInspection complete. No data was changed.")


if __name__ == "__main__":
    main()
