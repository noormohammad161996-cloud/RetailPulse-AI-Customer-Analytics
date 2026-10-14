
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

BUSINESS_COLUMNS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]


def main():
    print("Loading worksheets...")

    sheets = pd.read_excel(DATA_PATH, sheet_name=None)
    frames = []

    for sheet_name, df in sheets.items():
        df.columns = df.columns.str.strip()
        df["source_sheet"] = sheet_name
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)

    print(f"Total rows: {len(data):,}")

    # Count how many times each transaction-line combination appears.
    # dropna=False ensures missing values are included in comparisons.
    grouped = data.groupby(
        BUSINESS_COLUMNS,
        dropna=False,
        sort=False,
    ).agg(
        occurrences=("source_sheet", "size"),
        worksheet_count=("source_sheet", "nunique"),
    )

    duplicate_groups = grouped[grouped["occurrences"] > 1]

    within_sheet_groups = duplicate_groups[
        duplicate_groups["worksheet_count"] == 1
    ]

    cross_sheet_groups = duplicate_groups[
        duplicate_groups["worksheet_count"] > 1
    ]

    print("\n--- DUPLICATE BREAKDOWN ---")
    print(f"Distinct duplicate groups: {len(duplicate_groups):,}")

    print(
        "Rows belonging to duplicate groups: "
        f"{duplicate_groups['occurrences'].sum():,}"
    )

    print(
        "Extra occurrences beyond the first record: "
        f"{(duplicate_groups['occurrences'] - 1).sum():,}"
    )

    print(
        "\nDuplicate groups confined to one worksheet: "
        f"{len(within_sheet_groups):,}"
    )

    print(
        "Duplicate groups appearing across worksheets: "
        f"{len(cross_sheet_groups):,}"
    )

    print("\n--- REPEATED RECORDS BY WORKSHEET ---")
    for sheet_name, df in data.groupby("source_sheet"):
        repeated = df.duplicated(
            subset=BUSINESS_COLUMNS,
            keep=False,
        )
        extra = df.duplicated(
            subset=BUSINESS_COLUMNS,
            keep="first",
        )

        print(f"\n{sheet_name}")
        print(f"Rows: {len(df):,}")
        print(f"Rows in duplicate groups: {repeated.sum():,}")
        print(f"Extra occurrences in this worksheet: {extra.sum():,}")

    print("\nInvestigation complete. Original data was not changed.")


if __name__ == "__main__":
    main()
