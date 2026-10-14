
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "interim" / "retail_combined.parquet"

SHEET_1 = "Year 2009-2010"
SHEET_2 = "Year 2010-2011"

# Compare the actual transaction fields, not the worksheet name.
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
    print("RETAILPULSE - WORKSHEET OVERLAP COMPARISON")
    print("=" * 48)

    data = pd.read_parquet(DATA_PATH)

    start_date = pd.Timestamp("2010-12-01")
    end_date = pd.Timestamp("2010-12-10")

    overlap = data[
        data["invoice_date"].ge(start_date)
        & data["invoice_date"].lt(end_date)
    ].copy()

    first = overlap.loc[
        overlap["source_sheet"] == SHEET_1, COMPARE_COLUMNS
    ]
    second = overlap.loc[
        overlap["source_sheet"] == SHEET_2, COMPARE_COLUMNS
    ]

    print(f"\nDate window: {start_date.date()} to 2010-12-09")
    print(f"Rows in {SHEET_1}: {len(first):,}")
    print(f"Rows in {SHEET_2}: {len(second):,}")

    # Count identical records, including repeated occurrences.
    first_counts = (
        first.groupby(COMPARE_COLUMNS, dropna=False)
        .size()
        .rename("count_first")
        .reset_index()
    )

    second_counts = (
        second.groupby(COMPARE_COLUMNS, dropna=False)
        .size()
        .rename("count_second")
        .reset_index()
    )

    comparison = first_counts.merge(
        second_counts,
        on=COMPARE_COLUMNS,
        how="outer",
    )

    comparison[["count_first", "count_second"]] = (
        comparison[["count_first", "count_second"]].fillna(0).astype(int)
    )

    # Number of matching occurrences, respecting duplicate counts.
    comparison["matching_count"] = comparison[
        ["count_first", "count_second"]
    ].min(axis=1)

    matching_rows = int(comparison["matching_count"].sum())
    only_first = int(
        (comparison["count_first"] - comparison["matching_count"]).sum()
    )
    only_second = int(
        (comparison["count_second"] - comparison["matching_count"]).sum()
    )

    print("\nComparison results:")
    print(f"Matching record occurrences: {matching_rows:,}")
    print(f"Unmatched occurrences in first sheet: {only_first:,}")
    print(f"Unmatched occurrences in second sheet: {only_second:,}")

    print("\nVerification complete. No source data was changed.")


if __name__ == "__main__":
    main()
