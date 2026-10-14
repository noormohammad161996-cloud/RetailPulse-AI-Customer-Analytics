from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "monthly_forecasting_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

RESULT_PATH = OUTPUT_DIR / "seasonal_naive_results.csv"
CHART_PATH = OUTPUT_DIR / "seasonal_naive_forecast.png"


def main():
    data = pd.read_csv(INPUT_PATH, parse_dates=["month"])
    data = data.sort_values("month").reset_index(drop=True)

    # Exclude incomplete December 2011 from evaluation.
    complete = data.loc[~data["is_partial_month"]].copy()

    # Hold out the last five complete months.
    train = complete.iloc[:-5].copy()
    test = complete.iloc[-5:].copy()

    # Seasonal-naive forecast: use the same month one year earlier.
    history = data.set_index("month")["sales_value"]

    test["predicted_sales"] = test["month"].apply(
        lambda month: history.get(month - pd.DateOffset(years=1), float("nan"))
    )
    test["actual_sales"] = test["sales_value"]

    if test["predicted_sales"].isna().any():
        raise ValueError(
            "Some test months do not have prior-year observations. "
            "Check the monthly data before evaluating."
        )

    test["absolute_error"] = (
        test["actual_sales"] - test["predicted_sales"]
    ).abs()

    mae = test["absolute_error"].mean()
    wape = (
        test["absolute_error"].sum()
        / test["actual_sales"].abs().sum()
    ) * 100

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    test.to_csv(RESULT_PATH, index=False)

    plt.figure(figsize=(11, 6))
    plt.plot(
        train["month"], train["sales_value"],
        marker="o", label="Training actuals"
    )
    plt.plot(
        test["month"], test["actual_sales"],
        marker="o", label="Test actuals"
    )
    plt.plot(
        test["month"], test["predicted_sales"],
        marker="x", linestyle="--",
        label="Same month previous year"
    )
    plt.title("RetailPulse - Seasonal-Naive Forecast")
    plt.xlabel("Month")
    plt.ylabel("Sales value")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=160)
    plt.close()

    print("RETAILPULSE - SEASONAL-NAIVE FORECAST")
    print("=" * 42)
    print(f"Training months: {len(train)}")
    print(f"Testing months: {len(test)}")
    print(f"MAE: {mae:,.2f}")
    print(f"WAPE: {wape:.2f}%")

    print("\nTest-period results:")
    print(
        test[["month", "actual_sales", "predicted_sales", "absolute_error"]]
        .to_string(index=False)
    )

    print(f"\nResults saved to: {RESULT_PATH}")
    print(f"Chart saved to: {CHART_PATH}")


if __name__ == "__main__":
    main()
