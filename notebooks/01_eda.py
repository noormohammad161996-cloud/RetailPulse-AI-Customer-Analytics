from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"


def inspect_sheet(sheet_name):
    print("\n" + "=" * 60)
    print(f"INSPECTING SHEET: {sheet_name}")
    print("=" * 60)

    df = pd.read_excel(DATA_PATH, sheet_name=sheet_name)

    print(f"\nRows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst 5 records:")
    print(df.head().to_string())

    print("\nData types:")
    print(df.dtypes.to_string())

    print("\nMissing values:")
    print(df.isnull().sum().to_string())

    print(f"\nDuplicate rows: {df.duplicated().sum():,}")

    return df


def main():
    print("RETAILPULSE - EXPLORATORY DATA ANALYSIS")

    excel_file = pd.ExcelFile(DATA_PATH)
    print("\nAvailable worksheets:", excel_file.sheet_names)

    for sheet_name in excel_file.sheet_names:
        inspect_sheet(sheet_name)

    print("\nInitial dataset inspection completed.")


if __name__ == "__main__":
    main()