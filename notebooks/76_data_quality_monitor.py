from pathlib import Path

import pandas as pd


# ==========================================================
# PROGRAM 76: DATA QUALITY MONITORING
# RetailPulse - AI-Powered Customer Analytics Platform
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sales_analysis.parquet"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

REPORT_FILE = OUTPUT_DIR / "data_quality_report.txt"
RESULTS_FILE = OUTPUT_DIR / "data_quality_results.csv"

REQUIRED_COLUMNS = [
    "invoice_id",
    "product_id",
    "quantity",
    "invoice_date",
    "unit_price",
    "line_value",
]

NUMERIC_COLUMNS = ["quantity", "unit_price", "line_value"]


def main():
    print("=" * 65)
    print("PROGRAM 76: DATA QUALITY MONITORING")
    print("=" * 65)

    # ------------------------------------------------------
    # 1. Validate input file
    # ------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nLoading dataset: {INPUT_FILE.name}")

    df = pd.read_parquet(INPUT_FILE)

    print(f"Dataset rows: {len(df):,}")
    print(f"Dataset columns: {len(df.columns)}")

    # ------------------------------------------------------
    # 2. Check required columns
    # ------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    checks = []

    def add_check(name, status, affected_rows, details):
        checks.append(
            {
                "check_name": name,
                "status": status,
                "affected_rows": int(affected_rows),
                "details": details,
            }
        )

    add_check(
        "Required columns",
        "FAIL" if missing_columns else "PASS",
        len(missing_columns),
        (
            "Missing columns: " + ", ".join(missing_columns)
            if missing_columns
            else "All required columns are present."
        ),
    )

    if missing_columns:
        results = pd.DataFrame(checks)
        results.to_csv(RESULTS_FILE, index=False)

        with REPORT_FILE.open("w", encoding="utf-8") as report:
            report.write("RETAILPULSE DATA QUALITY REPORT\n")
            report.write("=" * 45 + "\n")
            report.write(f"Input file: {INPUT_FILE.name}\n")
            report.write(f"Rows: {len(df):,}\n")
            report.write(f"Columns: {len(df.columns)}\n\n")
            report.write("Missing required columns:\n")
            report.write(", ".join(missing_columns) + "\n\n")
            report.write("Overall status: FAIL\n")

        print("\nRequired columns are missing.")
        print(f"CSV results: {RESULTS_FILE}")
        print(f"Text report: {REPORT_FILE}")
        print("Overall status: FAIL")
        return

    # ------------------------------------------------------
    # 3. Check missing values
    # ------------------------------------------------------

    for column in REQUIRED_COLUMNS:
        missing_count = int(df[column].isna().sum())

        add_check(
            f"Missing values: {column}",
            "WARNING" if missing_count > 0 else "PASS",
            missing_count,
            f"{missing_count:,} missing values in {column}.",
        )

    # ------------------------------------------------------
    # 4. Check duplicate rows
    # ------------------------------------------------------

    duplicate_count = int(df.duplicated().sum())

    add_check(
        "Exact duplicate rows",
        "WARNING" if duplicate_count > 0 else "PASS",
        duplicate_count,
        f"{duplicate_count:,} exact duplicate rows detected.",
    )

    # ------------------------------------------------------
    # 5. Check numeric values
    # ------------------------------------------------------

    for column in NUMERIC_COLUMNS:
        values = pd.to_numeric(df[column], errors="coerce")

        invalid_count = int(
            (values.isna() | ~values.map(
                lambda value: pd.notna(value)
            )).sum()
        )

        # Separate non-numeric/missing values from invalid signs.
        invalid_numeric_count = int(
            (
                df[column].notna()
                & values.isna()
            ).sum()
        )

        add_check(
            f"Numeric validity: {column}",
            "WARNING"
            if invalid_numeric_count > 0
            else "PASS",
            invalid_numeric_count,
            (
                f"{invalid_numeric_count:,} non-numeric values "
                f"detected in {column}."
            ),
        )

        if column in ["quantity", "unit_price"]:
            invalid_sign_count = int((values <= 0).sum())

            add_check(
                f"Positive values: {column}",
                "FAIL" if invalid_sign_count > 0 else "PASS",
                invalid_sign_count,
                (
                    f"{invalid_sign_count:,} values are zero "
                    "or negative."
                ),
            )

    # ------------------------------------------------------
    # 6. Check invoice dates
    # ------------------------------------------------------

    parsed_dates = pd.to_datetime(
        df["invoice_date"],
        errors="coerce",
    )

    invalid_dates = int(parsed_dates.isna().sum())

    add_check(
        "Valid invoice dates",
        "FAIL" if invalid_dates > 0 else "PASS",
        invalid_dates,
        f"{invalid_dates:,} missing or unparseable invoice dates.",
    )

    # ------------------------------------------------------
    # 7. Check line-value consistency
    # ------------------------------------------------------

    quantity = pd.to_numeric(df["quantity"], errors="coerce")
    unit_price = pd.to_numeric(df["unit_price"], errors="coerce")
    line_value = pd.to_numeric(df["line_value"], errors="coerce")

    valid_values = (
        quantity.notna()
        & unit_price.notna()
        & line_value.notna()
    )

    expected_line_value = quantity * unit_price

    inconsistent_count = int(
        (
            valid_values
            & ~(
                (line_value - expected_line_value).abs()
                <= 0.01
            )
        ).sum()
    )

    add_check(
        "Line-value consistency",
        "WARNING" if inconsistent_count > 0 else "PASS",
        inconsistent_count,
        (
            f"{inconsistent_count:,} rows differ from "
            "quantity multiplied by unit price by more than 0.01."
        ),
    )

    # ------------------------------------------------------
    # 8. Create results
    # ------------------------------------------------------

    results = pd.DataFrame(checks)

    if (results["status"] == "FAIL").any():
        overall_status = "FAIL"
    elif (results["status"] == "WARNING").any():
        overall_status = "WARNING"
    else:
        overall_status = "PASS"

    # ------------------------------------------------------
    # 9. Save CSV results
    # ------------------------------------------------------

    results.to_csv(RESULTS_FILE, index=False)

    # ------------------------------------------------------
    # 10. Save text report
    # ------------------------------------------------------

    with REPORT_FILE.open("w", encoding="utf-8") as report:
        report.write("RETAILPULSE DATA QUALITY REPORT\n")
        report.write("=" * 65 + "\n\n")

        report.write(f"Input file: {INPUT_FILE.name}\n")
        report.write(f"Total rows: {len(df):,}\n")
        report.write(f"Total columns: {len(df.columns)}\n")
        report.write(
            f"Date range: {parsed_dates.min()} to "
            f"{parsed_dates.max()}\n\n"
        )

        report.write("QUALITY CHECK RESULTS\n")
        report.write("-" * 65 + "\n")

        for check in checks:
            report.write(
                f"[{check['status']}] {check['check_name']}\n"
            )
            report.write(
                f"  Affected rows/items: "
                f"{check['affected_rows']:,}\n"
            )
            report.write(f"  Details: {check['details']}\n\n")

        report.write("-" * 65 + "\n")
        report.write(f"OVERALL STATUS: {overall_status}\n")
        report.write(
            "\nNote: Warnings require investigation; they do not "
            "automatically mean the data is unusable.\n"
        )
        report.write(
            "The source dataset was read only and was not modified.\n"
        )

    # ------------------------------------------------------
    # 11. Display summary
    # ------------------------------------------------------

    print("\nQUALITY CHECK SUMMARY")
    print("-" * 65)

    for check in checks:
        print(
            f"{check['status']:7} | "
            f"{check['check_name']}: "
            f"{check['affected_rows']:,}"
        )

    print("-" * 65)
    print(f"OVERALL STATUS: {overall_status}")
    print(f"\nCSV results: {RESULTS_FILE}")
    print(f"Text report: {REPORT_FILE}")
    print("\nSource dataset was not modified.")


if __name__ == "__main__":
    main()
