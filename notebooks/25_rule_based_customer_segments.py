
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "customer_rfm.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "customer_segments.csv"
SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "customer_segment_summary.csv"


def assign_segment(row):
    # These are initial business rules, not learned ML labels.
    if row["recency_days"] <= 30 and row["frequency"] >= 10:
        return "Recent Loyal Customers"

    if row["recency_days"] <= 60 and row["monetary"] >= 5000:
        return "Recent High-Value Customers"

    if row["recency_days"] > 180 and row["frequency"] >= 3:
        return "At-Risk Past Customers"

    if row["frequency"] == 1:
        return "One-Time Customers"

    return "Other Customers"


def main():
    rfm = pd.read_csv(INPUT_PATH)

    rfm["segment"] = rfm.apply(assign_segment, axis=1)

    summary = (
        rfm.groupby("segment")
        .agg(
            customer_count=("customer_id", "nunique"),
            average_recency_days=("recency_days", "mean"),
            average_frequency=("frequency", "mean"),
            average_monetary=("monetary", "mean"),
            total_monetary=("monetary", "sum"),
        )
        .reset_index()
        .sort_values("customer_count", ascending=False)
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rfm.to_csv(OUTPUT_PATH, index=False)
    summary.to_csv(SUMMARY_PATH, index=False)

    print("RETAILPULSE - RULE-BASED CUSTOMER SEGMENTS")
    print("=" * 45)
    print(f"Customers segmented: {len(rfm):,}")
    print(f"Number of segments: {rfm['segment'].nunique()}")

    print("\nSegment summary:")
    print(summary.round(2).to_string(index=False))

    print(f"\nCustomer segments saved to: {OUTPUT_PATH}")
    print(f"Segment summary saved to: {SUMMARY_PATH}")
    print("\nNote: These are initial business rules, not K-Means results.")


if __name__ == "__main__":
    main()
