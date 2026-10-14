from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "monthly_forecasting_data.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "baseline_comparison.csv"


def calculate_metrics(actual, predicted):
    errors = (actual - predicted).abs()
    mae = errors.mean()
    wape = errors.sum() / actual.abs().sum() * 100
    return mae, wape


def main():
    data = pd.read_csv(INPUT_PATH, parse_dates=["month"])
    data = data.sort_values("month").reset_index(drop=True)

    # Exclude incomplete December 2011.
    data = data.loc[~data["is_partial_month"]].reset_index(drop=True)

    # Use the same 12 months as the rolling seasonal-naive evaluation.
    test = data.iloc[12:].copy()
    training_history = data.iloc[:12]

    # Fixed mean baseline based on the first 12 months.
    mean_prediction = training_history["sales_value"].mean()

    mean_predictions = pd.Series(
        mean_prediction, index=test.index, dtype=float
    )

    # Seasonal-naive predictions use the same month one year earlier.
    history = data.set_index("month")["sales_value"]
    seasonal_predictions = test["month"].apply(
        lambda month: history.get(
            month - pd.DateOffset(years=1), float("nan")
        )
    )

    if seasonal_predictions.isna().any():
        raise ValueError("A seasonal-naive prediction is missing.")

    results = pd.DataFrame({
        "month": test["month"].values,
        "actual_sales": test["sales_value"].values,
        "mean_prediction": mean_predictions.values,
        "seasonal_naive_prediction": seasonal_predictions.values,
    })

    results.to_csv(OUTPUT_PATH, index=False)

    mean_mae, mean_wape = calculate_metrics(
        results["actual_sales"], results["mean_prediction"]
    )
    seasonal_mae, seasonal_wape = calculate_metrics(
        results["actual_sales"], results["seasonal_naive_prediction"]
    )

    print("RETAILPULSE - FAIR BASELINE COMPARISON")
    print("=" * 42)
    print(f"Evaluation months: {len(results)}")
    print("\nModel metrics:")
    print(f"Mean baseline MAE: {mean_mae:,.2f}")
    print(f"Mean baseline WAPE: {mean_wape:.2f}%")
    print(f"Seasonal-naive MAE: {seasonal_mae:,.2f}")
    print(f"Seasonal-naive WAPE: {seasonal_wape:.2f}%")

    print("\nPeriod-by-period predictions:")
    print(results.to_string(index=False))
    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
