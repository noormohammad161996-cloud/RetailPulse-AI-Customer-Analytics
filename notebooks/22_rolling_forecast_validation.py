from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "monthly_forecasting_data.csv"
)
OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "rolling_validation_results.csv"
)


def main():
    data = pd.read_csv(INPUT_PATH, parse_dates=["month"])
    data = data.sort_values("month").reset_index(drop=True)

    # Exclude the incomplete December 2011 month.
    data = data.loc[~data["is_partial_month"]].reset_index(drop=True)

    results = []

    # Each cutoff uses only prior observations and forecasts the next month.
    # Start after 12 months so a prior-year value is available.
    for test_index in range(12, len(data)):
        actual_month = data.loc[test_index, "month"]
        actual_value = data.loc[test_index, "sales_value"]

        previous_year_month = actual_month - pd.DateOffset(years=1)
        previous_year_rows = data.loc[
            data["month"] == previous_year_month, "sales_value"
        ]

        if previous_year_rows.empty:
            continue

        predicted_value = previous_year_rows.iloc[0]

        results.append({
            "month": actual_month,
            "actual_sales": actual_value,
            "predicted_sales": predicted_value,
            "absolute_error": abs(actual_value - predicted_value),
        })

    validation = pd.DataFrame(results)

    if validation.empty:
        raise ValueError("No valid rolling validation periods were found.")

    mae = validation["absolute_error"].mean()
    wape = (
        validation["absolute_error"].sum()
        / validation["actual_sales"].abs().sum()
    ) * 100

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    validation.to_csv(OUTPUT_PATH, index=False)

    print("RETAILPULSE - ROLLING FORECAST VALIDATION")
    print("=" * 45)
    print(f"Evaluation periods: {len(validation)}")
    print(f"MAE: {mae:,.2f}")
    print(f"WAPE: {wape:.2f}%")
    print("\nPeriod-by-period results:")
    print(validation.to_string(index=False))
    print(f"\nResults saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
