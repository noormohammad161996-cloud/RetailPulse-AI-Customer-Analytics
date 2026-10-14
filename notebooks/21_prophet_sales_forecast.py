
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "monthly_forecasting_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

RESULT_PATH = OUTPUT_DIR / "prophet_forecast_results.csv"
CHART_PATH = OUTPUT_DIR / "prophet_forecast.png"


def main():
    data = pd.read_csv(INPUT_PATH, parse_dates=["month"])
    data = data.sort_values("month").reset_index(drop=True)

    # Exclude incomplete December 2011.
    complete = data.loc[~data["is_partial_month"]].copy()

    train = complete.iloc[:-5].copy()
    test = complete.iloc[-5:].copy()

    # Prophet requires columns named ds and y.
    prophet_train = train[["month", "sales_value"]].rename(
        columns={"month": "ds", "sales_value": "y"}
    )

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="additive",
    )
    model.fit(prophet_train)

    future = pd.DataFrame({"ds": test["month"]})
    forecast = model.predict(future)

    results = pd.DataFrame({
        "month": test["month"].values,
        "actual_sales": test["sales_value"].values,
        "predicted_sales": forecast["yhat"].values,
    })

    results["absolute_error"] = (
        results["actual_sales"] - results["predicted_sales"]
    ).abs()

    mae = results["absolute_error"].mean()
    wape = (
        results["absolute_error"].sum()
        / results["actual_sales"].abs().sum()
    ) * 100

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULT_PATH, index=False)

    plt.figure(figsize=(11, 6))
    plt.plot(
        train["month"], train["sales_value"],
        marker="o", label="Training actuals"
    )
    plt.plot(
        test["month"], results["actual_sales"],
        marker="o", label="Test actuals"
    )
    plt.plot(
        test["month"], results["predicted_sales"],
        marker="x", linestyle="--", label="Prophet forecast"
    )
    plt.title("RetailPulse - Prophet Sales Forecast")
    plt.xlabel("Month")
    plt.ylabel("Sales value")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=160)
    plt.close()

    print("RETAILPULSE - PROPHET FORECAST")
    print("=" * 34)
    print(f"Training months: {len(train)}")
    print(f"Testing months: {len(test)}")
    print(f"MAE: {mae:,.2f}")
    print(f"WAPE: {wape:.2f}%")
    print("\nTest-period results:")
    print(results.to_string(index=False))
    print(f"\nResults saved to: {RESULT_PATH}")
    print(f"Chart saved to: {CHART_PATH}")


if __name__ == "__main__":
    main()
