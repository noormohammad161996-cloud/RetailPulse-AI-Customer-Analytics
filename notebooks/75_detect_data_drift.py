from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


# --------------------------------------------------
# PROGRAM 75: DATA DRIFT DETECTION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

REPORT_FILE = OUTPUT_DIR / "data_drift_report.txt"
RESULTS_FILE = OUTPUT_DIR / "data_drift_results.csv"

FEATURES = ["quantity", "unit_price", "line_value"]

REFERENCE_START = "2011-01-01"
REFERENCE_END = "2011-06-30 23:59:59"

CURRENT_START = "2011-07-01"
CURRENT_END = "2011-11-30 23:59:59"

PSI_BINS = 10


def calculate_psi(reference, current, bins=10):
    """Calculate Population Stability Index using reference quantile bins."""
    reference = np.asarray(reference, dtype=float)
    current = np.asarray(current, dtype=float)

    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))

    if len(edges) < 2:
        return 0.0

    # Extend the outer edges so current values outside the reference
    # range are included in the first or last bin.
    edges[0] = -np.inf
    edges[-1] = np.inf

    reference_counts, _ = np.histogram(reference, bins=edges)
    current_counts, _ = np.histogram(current, bins=edges)

    reference_pct = reference_counts / len(reference)
    current_pct = current_counts / len(current)

    # Small smoothing prevents log(0) when a bin has no observations.
    epsilon = 1e-6
    reference_pct = np.clip(reference_pct, epsilon, None)
    current_pct = np.clip(current_pct, epsilon, None)

    return float(
        np.sum(
            (current_pct - reference_pct)
            * np.log(current_pct / reference_pct)
        )
    )


def interpret_psi(value):
    """Return a commonly used PSI interpretation, not a formal test."""
    if value < 0.10:
        return "Little distribution shift"
    if value < 0.25:
        return "Moderate distribution shift"
    return "Large distribution shift"


def main():
    print("=" * 65)
    print("PROGRAM 75: DATA DRIFT DETECTION")
    print("=" * 65)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input dataset not found: {INPUT_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nLoading: {INPUT_FILE.relative_to(PROJECT_ROOT)}")

    df = pd.read_parquet(INPUT_FILE, columns=["invoice_date"] + FEATURES)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")

    for feature in FEATURES:
        df[feature] = pd.to_numeric(df[feature], errors="coerce")

    reference_start = pd.Timestamp(REFERENCE_START)
    reference_end = pd.Timestamp(REFERENCE_END)
    current_start = pd.Timestamp(CURRENT_START)
    current_end = pd.Timestamp(CURRENT_END)

    reference = df.loc[
        df["invoice_date"].between(reference_start, reference_end)
    ].copy()

    current = df.loc[
        df["invoice_date"].between(current_start, current_end)
    ].copy()

    print(f"Reference period: {REFERENCE_START} to {REFERENCE_END}")
    print(f"Comparison period: {CURRENT_START} to {CURRENT_END}")
    print(f"Reference rows: {len(reference):,}")
    print(f"Comparison rows: {len(current):,}")

    if reference.empty or current.empty:
        raise ValueError("Reference or comparison period contains no rows.")

    results = []
    report_lines = [
        "RETAILPULSE - PROGRAM 75 DATA DRIFT REPORT",
        "=" * 60,
        f"Input: {INPUT_FILE.relative_to(PROJECT_ROOT)}",
        f"Reference period: {REFERENCE_START} to {REFERENCE_END}",
        f"Comparison period: {CURRENT_START} to {CURRENT_END}",
        f"Reference rows: {len(reference):,}",
        f"Comparison rows: {len(current):,}",
        "",
        "METHODS",
        "- PSI: compares feature distribution proportions using reference quantile bins.",
        "- KS two-sample test: compares empirical distributions of numerical values.",
        "- KS p-values are statistical signals, not measures of business importance.",
        "",
        "RESULTS",
    ]

    for feature in FEATURES:
        ref_values = reference[feature].dropna().to_numpy(dtype=float)
        cur_values = current[feature].dropna().to_numpy(dtype=float)

        if len(ref_values) == 0 or len(cur_values) == 0:
            print(f"Skipping {feature}: no valid values in one period.")
            continue

        psi = calculate_psi(ref_values, cur_values, PSI_BINS)
        ks_result = ks_2samp(ref_values, cur_values)

        row = {
            "feature": feature,
            "reference_count": len(ref_values),
            "comparison_count": len(cur_values),
            "reference_mean": float(np.mean(ref_values)),
            "comparison_mean": float(np.mean(cur_values)),
            "reference_median": float(np.median(ref_values)),
            "comparison_median": float(np.median(cur_values)),
            "psi": psi,
            "psi_interpretation": interpret_psi(psi),
            "ks_statistic": float(ks_result.statistic),
            "ks_p_value": float(ks_result.pvalue),
            "ks_significant_at_0_05": bool(ks_result.pvalue < 0.05),
        }
        results.append(row)

        report_lines.extend([
            "",
            f"Feature: {feature}",
            f"Reference mean: {row['reference_mean']:.4f}",
            f"Comparison mean: {row['comparison_mean']:.4f}",
            f"Reference median: {row['reference_median']:.4f}",
            f"Comparison median: {row['comparison_median']:.4f}",
            f"PSI: {psi:.4f}",
            f"PSI interpretation: {row['psi_interpretation']}",
            f"KS statistic: {ks_result.statistic:.4f}",
            f"KS p-value: {ks_result.pvalue:.6g}",
            f"KS significant at 0.05: {ks_result.pvalue < 0.05}",
        ])

        print(
            f"\n{feature}: PSI={psi:.4f} | "
            f"KS p-value={ks_result.pvalue:.6g}"
        )

    if not results:
        raise ValueError("No features could be compared.")

    report_lines.extend([
        "",
        "LIMITATIONS",
        "- Detected drift does not automatically mean model performance has degraded.",
        "- Statistical significance can occur with very large datasets even for small shifts.",
        "- PSI interpretation thresholds are common heuristics, not universal rules.",
        "- Sales distributions can change due to seasonality, promotions, or customer behavior.",
        "- This analysis does not train, evaluate, or alter a prediction model.",
        "- December 2011 is excluded because the month is incomplete.",
        "- The source dataset is not modified.",
        "",
    ])

    pd.DataFrame(results).to_csv(RESULTS_FILE, index=False)
    REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")

    print("\nAnalysis completed.")
    print(f"Report: {REPORT_FILE.relative_to(PROJECT_ROOT)}")
    print(f"CSV: {RESULTS_FILE.relative_to(PROJECT_ROOT)}")
    print("\nNo source data was changed.")


if __name__ == "__main__":
    main()
