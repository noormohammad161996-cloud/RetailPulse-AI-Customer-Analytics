from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

CSV_PATH = OUTPUT_DIR / "monthly_sales_summary.csv"
CHART_PATH = OUTPUT_DIR / "monthly_sales_trend.png"


def main():
    data = pd.read_parquet(INPUT_PATH)

    data["line_value"] = data["quantity"] * data["unit_price"]
    data["month"] = data["invoice_date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        data.groupby("month")
        .agg(
            sales_value=("line_value", "sum"),
            quantity_sold=("quantity", "sum"),
            invoice_count=("invoice_id", "nunique"),
            identified_customers=("customer_id", "nunique"),
            transaction_rows=("invoice_id", "size"),
        )
        .reset_index()
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(CSV_PATH, index=False)

    plt.figure(figsize=(12, 6))
    plt.plot(
        monthly["month"],
        monthly["sales_value"],
        marker="o",
    )
    plt.title("RetailPulse - Monthly Sales Value")
    plt.xlabel("Month")
    plt.ylabel("Sales value (dataset currency units)")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=160)
    plt.close()

    print("RETAILPULSE - MONTHLY SALES ANALYSIS")
    print("=" * 40)
    print(f"Months analyzed: {len(monthly)}")
    print(f"Total sales value: {monthly['sales_value'].sum():,.2f}")
    print(f"Highest sales month: {monthly.loc[monthly['sales_value'].idxmax(), 'month']:%Y-%m}")
    print(f"Lowest sales month: {monthly.loc[monthly['sales_value'].idxmin(), 'month']:%Y-%m}")

    print("\nMonthly summary:")
    print(monthly.to_string(index=False))

    print(f"\nCSV saved to: {CSV_PATH}")
    print(f"Chart saved to: {CHART_PATH}")


if __name__ == "__main__":
    main()
