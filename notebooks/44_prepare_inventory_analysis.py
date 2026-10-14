
# File: notebooks/44_prepare_inventory_analysis.py
# Purpose: Inspect the existing sales dataset before inventory analysis.

from pathlib import Path
import pandas as pd

# Project root: retailpulse-zidio
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"

print("=" * 65)
print("RETAILPULSE - INVENTORY DATASET INSPECTION")
print("=" * 65)

# 1. Check whether the dataset exists
if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}\n"
        "Please check the file path."
    )

# 2. Load the existing sales dataset
df = pd.read_parquet(DATA_FILE)

print(f"\nDataset file: {DATA_FILE}")
print(f"Total rows: {len(df):,}")
print(f"Total columns: {len(df.columns)}")

# 3. Inspect column names and data types
print("\n--- COLUMN NAMES AND DATA TYPES ---")
print(df.dtypes.to_string())

# 4. Inspect missing values
print("\n--- MISSING VALUES ---")
missing = df.isnull().sum()
missing = missing[missing > 0]

if missing.empty:
    print("No missing values found.")
else:
    print(missing.to_string())

# 5. Display sample records
print("\n--- FIRST 5 RECORDS ---")
print(df.head().to_string(index=False))

# 6. Identify columns needed for inventory analysis
print("\n--- INVENTORY-RELATED COLUMNS ---")

column_lookup = {str(col).strip().lower(): col for col in df.columns}

possible_columns = {
    "product code": ["stockcode", "stock_code", "product_id"],
    "product description": ["description", "product_name"],
    "quantity sold": ["quantity", "qty"],
    "unit price": ["price", "unitprice", "unit_price"],
    "invoice number": ["invoice", "invoiceno", "invoice_no"],
    "transaction date": ["invoicedate", "invoice_date", "date"],
    "sales value": ["line_value", "sales", "revenue"],
}

found = {}

for label, candidates in possible_columns.items():
    match = next(
        (column_lookup[name] for name in candidates
         if name in column_lookup),
        None
    )
    found[label] = match
    print(f"{label}: {match if match is not None else 'NOT FOUND'}")

# 7. Inspect transaction date range
date_col = found["transaction date"]

if date_col:
    dates = pd.to_datetime(df[date_col], errors="coerce")
    valid_dates = dates.dropna()

    print("\n--- TRANSACTION DATE RANGE ---")
    if not valid_dates.empty:
        print(f"First transaction: {valid_dates.min()}")
        print(f"Last transaction:  {valid_dates.max()}")
    else:
        print("No valid transaction dates found.")

# 8. Inspect product-level sales
product_col = found["product code"]
quantity_col = found["quantity sold"]
price_col = found["unit price"]
invoice_col = found["invoice number"]
description_col = found["product description"]

required = [product_col, quantity_col, price_col]

if all(column is not None for column in required):
    print("\n--- PRODUCT-LEVEL SALES SUMMARY ---")

    product_data = df.copy()
    product_data[quantity_col] = pd.to_numeric(
        product_data[quantity_col], errors="coerce"
    )
    product_data[price_col] = pd.to_numeric(
        product_data[price_col], errors="coerce"
    )

    product_data["_calculated_sales"] = (
        product_data[quantity_col] * product_data[price_col]
    )

    group_columns = [product_col]
    if description_col:
        group_columns.append(description_col)

    aggregation = {
        "quantity_sold": (quantity_col, "sum"),
        "sales_value": ("_calculated_sales", "sum"),
        "average_unit_price": (price_col, "mean"),
        "transaction_rows": (quantity_col, "size"),
    }

    if invoice_col:
        aggregation["unique_invoices"] = (invoice_col, "nunique")

    product_summary = (
        product_data.groupby(group_columns, dropna=False)
        .agg(**aggregation)
        .reset_index()
        .sort_values("quantity_sold", ascending=False)
    )

    print(f"Unique product groups: {len(product_summary):,}")
    print("\nTop 10 products by quantity sold:")
    print(product_summary.head(10).to_string(index=False))

    # Save the inspection summary for the next stage
    output_file = (
        PROJECT_ROOT / "data" / "processed"
        / "inventory_product_inspection.csv"
    )
    product_summary.to_csv(output_file, index=False)
    print(f"\nProduct summary saved to: {output_file}")

else:
    print(
        "\nProduct-level summary skipped because one or more "
        "required columns were not found."
    )

print("\n" + "=" * 65)
print("DATASET INSPECTION COMPLETED")
print("=" * 65)
