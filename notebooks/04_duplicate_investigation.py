
from pathlib import Path
import pandas as pd

# Locate the project dataset
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"


def main():
    sheets = pd.read_excel(DATA_PATH, sheet_name=None)
    frames = []

    for sheet_name, df in sheets.items():
        df.columns = df.columns.str.strip()
        df["source_sheet"] = sheet_name
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)

    invoice_text = data["Invoice"].astype(str).str.strip()
    is_cancellation = invoice_text.str.upper().str.startswith("C")
    nonpositive_quantity = data["Quantity"] <= 0
    nonpositive_price = data["Price"] <= 0
    missing_customer = data["Customer ID"].isna()

    business_columns = [
        "Invoice", "StockCode", "Description", "Quantity",
        "InvoiceDate", "Price", "Customer ID", "Country"
    ]

    # Keep every row that belongs to a duplicate group
    duplicate = data.duplicated(
        subset=business_columns,
        keep=False
    )

    print("RETAILPULSE - DUPLICATE INVESTIGATION")
    print(f"\nTotal rows: {len(data):,}")
    print(f"Rows in duplicate groups: {duplicate.sum():,}")
    print(f"Rows with cancellation-style IDs: {is_cancellation.sum():,}")
    print(f"Rows with quantity <= 0: {nonpositive_quantity.sum():,}")
    print(f"Rows with price <= 0: {nonpositive_price.sum():,}")
    print(f"Rows with missing customer ID: {missing_customer.sum():,}")

    print("\nCancellation IDs AND nonpositive quantities:")
    print(f"{(is_cancellation & nonpositive_quantity).sum():,}")

    print("\nMissing customer IDs AND duplicate groups:")
    print(f"{(missing_customer & duplicate).sum():,}")

    print("\nDuplicate-group examples:")
    print(
        data.loc[duplicate, business_columns]
        .head(10)
        .to_string(index=False)
    )

    print("\nInvestigation completed. No data was changed.")


if __name__ == "__main__":
    main()
