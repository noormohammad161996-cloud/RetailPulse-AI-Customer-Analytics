from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "retail_deduplicated.parquet"
)
OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"
)
REPORT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "sales_analysis_report.txt"
)


def main():
    data = pd.read_parquet(INPUT_PATH)

    cancellation = data["invoice_id"].astype(str).str.startswith("C")
    valid_quantity = data["quantity"] > 0
    valid_price = data["unit_price"] > 0

    # Provisional filter for positive-value sales analysis.
    sales = data.loc[
        ~cancellation & valid_quantity & valid_price
    ].copy()

    sales["line_value"] = sales["quantity"] * sales["unit_price"]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    sales.to_parquet(OUTPUT_PATH, index=False)

    report = [
        "RETAILPULSE - PROVISIONAL SALES DATASET",
        "=" * 42,
        f"Input rows: {len(data):,}",
        f"Rows retained: {len(sales):,}",
        f"Rows excluded: {len(data) - len(sales):,}",
        f"Unique invoices: {sales['invoice_id'].nunique():,}",
        f"Unique identified customers: {sales['customer_id'].nunique():,}",
        f"Rows with missing customer IDs: {sales['customer_id'].isna().sum():,}",
        f"Rows with missing product names: {sales['product_name'].isna().sum():,}",
        f"Total positive line value: {sales['line_value'].sum():,.2f}",
        f"Date range: {sales['invoice_date'].min()} to {sales['invoice_date'].max()}",
        "",
        "Filter:",
        "- Invoice ID does not start with C.",
        "- Quantity is greater than zero.",
        "- Unit price is greater than zero.",
        "",
        "Important: This is a provisional analytical filter, not verified accounting revenue.",
        "Excluded records remain in the broader cleaned dataset.",
    ]

    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\n".join(report))
    print(f"\nSales dataset saved to: {OUTPUT_PATH}")
    print(f"Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
