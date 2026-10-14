
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "monthly_forecasting_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

RESULT_PATH = OUTPUT_DIR / "baseline_forecast_results.csv"
CHART_PATH = OUTPUT_DIR / "baseline_forecast.png"


def main():
    data = pd.read_csv(INPUT_PATH, parse_dates=["month"])
    data = data.sort_values("month").reset_index(drop=True)

    # Exclude the incomplete final month from model evaluation.
    complete = data.loc[~data["is_partial_month"]].copy()

    # First 19 complete months train; last 5 complete months test.
    train = complete.iloc[:-5].copy()
    test = complete.iloc[-5:].copy()

    # Baseline: forecast every test month using the training mean.
    baseline_value = train["sales_value"].mean()
    test["actual_sales"] = test["sales_value"]
    test["predicted_sales"] = baseline_value
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
        train["month"],
        train["sales_value"],
        marker="o",
        label="Training actuals",
    )
    plt.plot(
        test["month"],
        test["actual_sales"],
        marker="o",
        label="Test actuals",
    )
    plt.plot(
        test["month"],
        test["predicted_sales"],
        marker="x",
        linestyle="--",
        label="Mean baseline forecast",
    )
    plt.title("RetailPulse - Baseline Monthly Sales Forecast")
    plt.xlabel("Month")
    plt.ylabel("Sales value")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=160)
    plt.close()

    print("RETAILPULSE - BASELINE FORECAST")
    print("=" * 35)
    print(f"Training months: {len(train)}")
    print(f"Testing months: {len(test)}")
    print(f"Training mean forecast: {baseline_value:,.2f}")
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
