
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "monthly_sales_summary.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "monthly_forecasting_data.csv"


def main():
    monthly = pd.read_csv(INPUT_PATH, parse_dates=["month"])
    monthly = monthly.sort_values("month").reset_index(drop=True)

    # Create a continuous month index.
    full_months = pd.date_range(
        start=monthly["month"].min(),
        end=monthly["month"].max(),
        freq="MS",
    )

    monthly = (
        monthly.set_index("month")
        .reindex(full_months)
        .rename_axis("month")
        .reset_index()
    )

    # Flag missing months instead of silently treating them as zero sales.
    monthly["month_missing"] = monthly["sales_value"].isna()

    # Flag the final month because the dataset ends on December 9, 2011.
    monthly["is_partial_month"] = (
        (monthly["month"].dt.year == 2011)
        & (monthly["month"].dt.month == 12)
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(OUTPUT_PATH, index=False)

    print("RETAILPULSE - FORECASTING DATA PREPARATION")
    print("=" * 45)
    print(f"Expected monthly periods: {len(monthly)}")
    print(f"Missing monthly periods: {monthly['month_missing'].sum()}")
    print(f"Partial months flagged: {monthly['is_partial_month'].sum()}")

    print("\nLast six months:")
    print(monthly.tail(6).to_string(index=False))

    print(f"\nSaved to: {OUTPUT_PATH}")
    print("No sales values were imputed or changed.")


if __name__ == "__main__":
    main()
