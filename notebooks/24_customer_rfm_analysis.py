from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "customer_rfm.csv"


def main():
    data = pd.read_parquet(INPUT_PATH)

    # Customer-level analysis requires a known customer ID.
    identified = data.dropna(subset=["customer_id"]).copy()

    identified["line_value"] = (
        identified["quantity"] * identified["unit_price"]
    )

    # Use the day after the latest transaction as the reference date.
    reference_date = (
        identified["invoice_date"].max().normalize()
        + pd.Timedelta(days=1)
    )

    rfm = (
        identified.groupby("customer_id")
        .agg(
            last_purchase=("invoice_date", "max"),
            frequency=("invoice_id", "nunique"),
            monetary=("line_value", "sum"),
        )
        .reset_index()
    )

    rfm["recency_days"] = (
        reference_date - rfm["last_purchase"].dt.normalize()
    ).dt.days

    rfm = rfm[
        [
            "customer_id",
            "recency_days",
            "frequency",
            "monetary",
            "last_purchase",
        ]
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rfm.to_csv(OUTPUT_PATH, index=False)

    print("RETAILPULSE - CUSTOMER RFM ANALYSIS")
    print("=" * 39)
    print(f"Identified customers: {len(rfm):,}")
    print(f"Reference date: {reference_date.date()}")
    print(f"Average recency (days): {rfm['recency_days'].mean():.2f}")
    print(f"Average invoice frequency: {rfm['frequency'].mean():.2f}")
    print(f"Average monetary value: {rfm['monetary'].mean():,.2f}")

    print("\nTop 10 customers by monetary value:")
    print(
        rfm.sort_values("monetary", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print(f"\nRFM data saved to: {OUTPUT_PATH}")
    print("RFM is a descriptive profile, not yet a customer segmentation model.")


if __name__ == "__main__":
    main()
