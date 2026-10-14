from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "retail_deduplicated.parquet"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "data_quality_report.txt"


def main():
    data = pd.read_parquet(DATA_PATH)

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

    report = [
        "RETAILPULSE - DATA QUALITY REPORT",
        "=" * 40,
        f"Total rows: {len(data):,}",
        f"Total columns: {len(data.columns)}",
        f"Date range: {data['invoice_date'].min()} to {data['invoice_date'].max()}",
        "",
        "MISSING VALUES",
        "-" * 20,
        data.isna().sum().to_string(),
        "",
        "TRANSACTION QUALITY",
        "-" * 20,
        f"Rows with quantity <= 0: {(data['quantity'] <= 0).sum():,}",
        f"Rows with unit price <= 0: {(data['unit_price'] <= 0).sum():,}",
        (
            "Cancellation-style invoice IDs: "
            f"{data['invoice_id'].astype(str).str.startswith('C').sum():,}"
        ),
        (
            "Exact duplicate occurrences (excluding source_sheet): "
            f"{data.duplicated(subset=transaction_columns).sum():,}"
        ),
        "",
        "SOURCE WORKSHEET COUNTS",
        "-" * 20,
        data["source_sheet"].value_counts().to_string(),
        "",
        "DECISIONS",
        "-" * 20,
        "- Original Excel data is preserved.",
        "- Verified worksheet overlap for Dec 1-9, 2010 was removed from the second sheet.",
        "- Other identical transaction lines have not been automatically removed.",
        "- Missing customer IDs and product names have not been automatically removed.",
        "- Non-positive quantities and prices require separate business-rule review.",
    ]

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\n".join(report))
    print(f"\nReport saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
