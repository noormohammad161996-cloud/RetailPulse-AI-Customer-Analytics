from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "retail_deduplicated.parquet"

COMPARE_COLUMNS = [
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
    print("RETAILPULSE - REMAINING DUPLICATE INVESTIGATION")
    print("=" * 50)

    data = pd.read_parquet(DATA_PATH)

    duplicate_mask = data.duplicated(
        subset=COMPARE_COLUMNS,
        keep=False,
    )
    duplicates = data.loc[duplicate_mask].copy()

    print(f"\nTotal dataset rows: {len(data):,}")
    print(f"Rows belonging to duplicate groups: {len(duplicates):,}")
    print(
        "Duplicate occurrences beyond the first copy: "
        f"{data.duplicated(subset=COMPARE_COLUMNS, keep='first').sum():,}"
    )

    print("\nDuplicate rows by worksheet:")
    print(duplicates["source_sheet"].value_counts().to_string())

    print("\nMost affected invoice IDs:")
    print(
        duplicates["invoice_id"]
        .value_counts()
        .head(10)
        .to_string()
    )

    print("\nDuplicate rows by year-month:")
    duplicates["year_month"] = (
        duplicates["invoice_date"].dt.to_period("M").astype(str)
    )
    print(duplicates["year_month"].value_counts().sort_index().to_string())

    print("\nSample duplicate records:")
    print(
        duplicates.sort_values("invoice_date")
        .head(15)[COMPARE_COLUMNS + ["source_sheet"]]
        .to_string(index=False)
    )

    print("\nInvestigation complete. No data was changed.")


if __name__ == "__main__":
    main()
