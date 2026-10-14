
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

BUSINESS_COLUMNS = [
    "Invoice", "StockCode", "Description", "Quantity",
    "InvoiceDate", "Price", "Customer ID", "Country",
]


def main():
    sheets = pd.read_excel(DATA_PATH, sheet_name=None)
    frames = []

    for sheet_name, df in sheets.items():
        df.columns = df.columns.str.strip()
        df["source_sheet"] = sheet_name
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)

    grouped = data.groupby(
        BUSINESS_COLUMNS,
        dropna=False,
        sort=False,
    ).agg(
        occurrences=("source_sheet", "size"),
        worksheet_count=("source_sheet", "nunique"),
        worksheets=("source_sheet", lambda s: ", ".join(sorted(s.unique()))),
    ).reset_index()

    cross_sheet = grouped[grouped["worksheet_count"] > 1].copy()

    print("RETAILPULSE - CROSS-SHEET INVESTIGATION")
    print(f"\nCross-sheet duplicate groups: {len(cross_sheet):,}")
    print(
        "Rows represented by these groups: "
        f"{cross_sheet['occurrences'].sum():,}"
    )

    if not cross_sheet.empty:
        dates = pd.to_datetime(cross_sheet["InvoiceDate"], errors="coerce")

        print(f"Earliest matching invoice date: {dates.min()}")
        print(f"Latest matching invoice date: {dates.max()}")

        overlap_start = pd.Timestamp("2010-12-01")
        overlap_end = pd.Timestamp("2010-12-10")

        in_overlap = dates.ge(overlap_start) & dates.lt(overlap_end)

        print(
            "Groups dated within Dec 1–9, 2010: "
            f"{in_overlap.sum():,}"
        )
        print(
            "Groups dated outside that period: "
            f"{(~in_overlap).sum():,}"
        )

        print("\nSample matching records:")
        print(
            cross_sheet[
                [
                    "Invoice", "StockCode", "Quantity",
                    "InvoiceDate", "Price", "occurrences", "worksheets",
                ]
            ].head(15).to_string(index=False)
        )

    print("\nInvestigation complete. No data was changed.")


if __name__ == "__main__":
    main()
