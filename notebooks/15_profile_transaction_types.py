from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "retail_deduplicated.parquet"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "transaction_type_profile.csv"


def main():
    data = pd.read_parquet(DATA_PATH)

    # Preserve the original columns and add diagnostic flags.
    data["is_cancellation_invoice"] = (
        data["invoice_id"].astype(str).str.startswith("C")
    )
    data["has_nonpositive_quantity"] = data["quantity"] <= 0
    data["has_nonpositive_price"] = data["unit_price"] <= 0
    data["line_value"] = data["quantity"] * data["unit_price"]

    conditions = [
        data["is_cancellation_invoice"],
        data["has_nonpositive_quantity"],
        data["has_nonpositive_price"],
    ]
    labels = [
        "Cancellation invoice",
        "Non-positive quantity",
        "Non-positive unit price",
    ]

    data["diagnostic_category"] = "Other / requires review"
    data.loc[~data["is_cancellation_invoice"], "diagnostic_category"] = "Standard invoice"
    data.loc[data["has_nonpositive_quantity"], "diagnostic_category"] = "Non-positive quantity"
    data.loc[data["has_nonpositive_price"], "diagnostic_category"] = "Non-positive unit price"
    data.loc[data["is_cancellation_invoice"], "diagnostic_category"] = "Cancellation invoice"

    summary = (
        data.groupby("diagnostic_category", dropna=False)
        .agg(
            row_count=("invoice_id", "size"),
            invoice_count=("invoice_id", "nunique"),
            quantity_total=("quantity", "sum"),
            line_value_total=("line_value", "sum"),
            missing_customer_rows=("customer_id", lambda s: s.isna().sum()),
        )
        .reset_index()
        .sort_values("row_count", ascending=False)
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_PATH, index=False)

    print("RETAILPULSE - TRANSACTION TYPE PROFILE")
    print("=" * 42)
    print(summary.to_string(index=False))
    print(f"\nProfile saved to: {OUTPUT_PATH}")
    print("\nNo transaction rows were removed.")


if __name__ == "__main__":
    main()
