"""
Program 74: Transaction Outlier Analysis
Project: RetailPulse - AI-Powered Customer Analytics

Methods:
1. Interquartile Range (IQR)
2. Z-score (absolute Z-score > 3)

Important:
- Reads the existing sales_analysis.parquet dataset.
- Does not modify or delete the source data.
- Outlier flags identify records for investigation, not confirmed errors.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

NUMERIC_COLUMNS = ["quantity", "line_value"]
REQUIRED_COLUMNS = [
    "invoice_id",
    "product_id",
    "product_name",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "line_value",
]


def get_iqr_bounds(series):
    """Return IQR lower and upper bounds."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - (1.5 * iqr)
    upper = q3 + (1.5 * iqr)
    return q1, q3, iqr, lower, upper


def main():
    print("=" * 65)
    print("PROGRAM 74: TRANSACTION OUTLIER ANALYSIS")
    print("=" * 65)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input dataset not found: {INPUT_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nLoading: {INPUT_FILE}")
    df = pd.read_parquet(INPUT_FILE)

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Required columns are missing: {missing_columns}")

    original_rows = len(df)

    # Work on a separate analysis copy; never modify the source file.
    analysis = df[REQUIRED_COLUMNS].copy()

    for column in NUMERIC_COLUMNS:
        analysis[column] = pd.to_numeric(
            analysis[column], errors="coerce"
        )

    # Only rows with valid numeric values for both measures are analyzed.
    valid_mask = (
        analysis[NUMERIC_COLUMNS].notna().all(axis=1)
        & np.isfinite(analysis[NUMERIC_COLUMNS]).all(axis=1)
    )
    data = analysis.loc[valid_mask].copy()

    if data.empty:
        raise ValueError("No valid numeric rows are available for analysis.")

    print(f"Source rows: {original_rows:,}")
    print(f"Rows analyzed: {len(data):,}")
    print(f"Rows skipped due to invalid numeric values: "
          f"{original_rows - len(data):,}")

    summary_lines = [
        "RETAILPULSE - PROGRAM 74 OUTLIER ANALYSIS REPORT",
        "=" * 60,
        f"Input file: {INPUT_FILE.relative_to(PROJECT_ROOT)}",
        f"Source rows: {original_rows:,}",
        f"Rows analyzed: {len(data):,}",
        f"Rows skipped due to invalid numeric values: "
        f"{original_rows - len(data):,}",
        "",
        "METHODS",
        "IQR: values below Q1 - 1.5*IQR or above Q3 + 1.5*IQR.",
        "Z-score: absolute Z-score greater than 3.",
        "Z-scores use population standard deviation (ddof=0).",
        "",
        "RESULTS",
    ]

    for column in NUMERIC_COLUMNS:
        values = data[column]

        q1, q3, iqr, lower, upper = get_iqr_bounds(values)
        iqr_flag = (values < lower) | (values > upper)

        mean = values.mean()
        std = values.std(ddof=0)

        if std > 0 and np.isfinite(std):
            z_scores = (values - mean) / std
            z_flag = z_scores.abs() > 3
        else:
            z_scores = pd.Series(0.0, index=values.index)
            z_flag = pd.Series(False, index=values.index)

        data[f"{column}_iqr_outlier"] = iqr_flag
        data[f"{column}_zscore"] = z_scores
        data[f"{column}_zscore_outlier"] = z_flag

        summary_lines.extend([
            "",
            f"Measure: {column}",
            f"Minimum: {values.min():,.4f}",
            f"Median: {values.median():,.4f}",
            f"Mean: {mean:,.4f}",
            f"Maximum: {values.max():,.4f}",
            f"Q1: {q1:,.4f}",
            f"Q3: {q3:,.4f}",
            f"IQR: {iqr:,.4f}",
            f"IQR lower bound: {lower:,.4f}",
            f"IQR upper bound: {upper:,.4f}",
            f"IQR flagged: {int(iqr_flag.sum()):,} "
            f"({iqr_flag.mean() * 100:.2f}%)",
            f"Z-score flagged: {int(z_flag.sum()):,} "
            f"({z_flag.mean() * 100:.2f}%)",
        ])

    flag_columns = [
        "quantity_iqr_outlier",
        "quantity_zscore_outlier",
        "line_value_iqr_outlier",
        "line_value_zscore_outlier",
    ]

    # Keep a transaction if at least one method flags either measure.
    flagged_mask = data[flag_columns].any(axis=1)
    flagged = data.loc[flagged_mask].copy()

    summary_lines.extend([
        "",
        f"Transactions flagged by at least one method: {len(flagged):,}",
        f"Percentage of analyzed transactions flagged: "
        f"{flagged_mask.mean() * 100:.2f}%",
        "",
        "INTERPRETATION AND LIMITATIONS",
        "- Flags are statistical signals, not proof of errors or fraud.",
        "- Large quantities or line values may represent legitimate bulk orders.",
        "- Retail data can be strongly skewed, affecting raw Z-scores.",
        "- Review flagged transactions with business context before taking action.",
        "- No rows were removed from or written back to the source dataset.",
        "- This dataset does not establish whether a transaction is fraudulent.",
    ])

    report_path = OUTPUT_DIR / "transaction_outlier_report.txt"
    report_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    csv_columns = [
        "invoice_id",
        "product_id",
        "product_name",
        "invoice_date",
        "quantity",
        "unit_price",
        "line_value",
        "customer_id",
        "country",
        *flag_columns,
        "quantity_zscore",
        "line_value_zscore",
    ]

    csv_path = OUTPUT_DIR / "transaction_outlier_analysis.csv"
    flagged[csv_columns].to_csv(csv_path, index=False)

    # Draw box plots using a fixed-size sample to keep the chart manageable.
    sample_size = min(20_000, len(data))
    plot_sample = data[NUMERIC_COLUMNS].sample(
        n=sample_size, random_state=42
    )

    chart_path = OUTPUT_DIR / "transaction_outlier_boxplots.png"
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    for axis, column in zip(axes, NUMERIC_COLUMNS):
        axis.boxplot(plot_sample[column].dropna(), showfliers=False)
        axis.set_title(f"{column.replace('_', ' ').title()} Distribution")
        axis.set_ylabel(column.replace("_", " ").title())
        axis.grid(axis="y", alpha=0.3)

    fig.suptitle(
        "RetailPulse Transaction Measures (sample; extreme points hidden)"
    )
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    print("\nAnalysis completed.")
    print(f"Transactions flagged: {len(flagged):,}")
    print(f"\nReport: {report_path.relative_to(PROJECT_ROOT)}")
    print(f"Flagged CSV: {csv_path.relative_to(PROJECT_ROOT)}")
    print(f"Chart: {chart_path.relative_to(PROJECT_ROOT)}")
    print("\nNo source data was changed.")


if __name__ == "__main__":
    main()
