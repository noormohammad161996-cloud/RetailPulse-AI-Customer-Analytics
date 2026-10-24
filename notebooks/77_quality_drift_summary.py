from pathlib import Path

import pandas as pd


# ==========================================================
# PROGRAM 77: DATA QUALITY AND DRIFT SUMMARY
# RetailPulse - AI-Powered Customer Analytics Platform
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

QUALITY_FILE = DATA_DIR / "data_quality_results.csv"
DRIFT_FILE = DATA_DIR / "data_drift_results.csv"

SUMMARY_FILE = DATA_DIR / "quality_drift_summary.csv"
REPORT_FILE = DATA_DIR / "quality_drift_summary_report.txt"


def main():
    print("=" * 65)
    print("PROGRAM 77: DATA QUALITY AND DRIFT SUMMARY")
    print("=" * 65)

    # ------------------------------------------------------
    # 1. Validate input files
    # ------------------------------------------------------

    for file in [QUALITY_FILE, DRIFT_FILE]:
        if not file.exists():
            raise FileNotFoundError(
                f"Required input file not found: {file}"
            )

    quality = pd.read_csv(QUALITY_FILE)
    drift = pd.read_csv(DRIFT_FILE)

    required_quality = {
        "check_name",
        "status",
        "affected_rows",
        "details",
    }

    required_drift = {
        "feature",
        "psi",
        "psi_interpretation",
        "ks_p_value",
        "ks_significant_at_0_05",
    }

    if not required_quality.issubset(quality.columns):
        raise ValueError(
            "Quality results are missing required columns."
        )

    if not required_drift.issubset(drift.columns):
        raise ValueError(
            "Drift results are missing required columns."
        )

    if quality.empty:
        raise ValueError("Quality results contain no checks.")

    if drift.empty:
        raise ValueError("Drift results contain no features.")

    print(f"\nQuality checks loaded: {len(quality)}")
    print(f"Drift features loaded: {len(drift)}")

    # ------------------------------------------------------
    # 2. Summarize quality checks
    # ------------------------------------------------------

    quality["status"] = (
        quality["status"].astype(str).str.upper().str.strip()
    )

    status_counts = quality["status"].value_counts()

    pass_count = int(status_counts.get("PASS", 0))
    warning_count = int(status_counts.get("WARNING", 0))
    fail_count = int(status_counts.get("FAIL", 0))

    unknown_count = int(
        len(quality) - pass_count - warning_count - fail_count
    )

    if fail_count > 0 or unknown_count > 0:
        quality_status = "FAIL"
    elif warning_count > 0:
        quality_status = "WARNING"
    else:
        quality_status = "PASS"

    # ------------------------------------------------------
    # 3. Summarize drift metrics
    # ------------------------------------------------------

    drift["psi"] = pd.to_numeric(
        drift["psi"], errors="coerce"
    )

    drift["ks_p_value"] = pd.to_numeric(
        drift["ks_p_value"], errors="coerce"
    )

    drift["ks_significant_at_0_05"] = (
        drift["ks_significant_at_0_05"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False})
    )

    invalid_psi = int(drift["psi"].isna().sum())
    invalid_ks = int(drift["ks_p_value"].isna().sum())
    invalid_significance = int(
        drift["ks_significant_at_0_05"].isna().sum()
    )

    if invalid_psi or invalid_ks or invalid_significance:
        raise ValueError(
            "Drift results contain missing or invalid metrics."
        )

    # Common PSI heuristic: below 0.10 indicates little shift.
    drift["psi_band"] = drift["psi"].apply(
        lambda value: (
            "Little shift"
            if value < 0.10
            else "Moderate shift"
            if value < 0.25
            else "Large shift"
        )
    )

    drift["ks_result"] = drift[
        "ks_significant_at_0_05"
    ].map(
        {
            True: "Statistically significant",
            False: "Not statistically significant",
        }
    )

    little_shift_count = int(
        (drift["psi_band"] == "Little shift").sum()
    )
    moderate_shift_count = int(
        (drift["psi_band"] == "Moderate shift").sum()
    )
    large_shift_count = int(
        (drift["psi_band"] == "Large shift").sum()
    )
    significant_count = int(
        drift["ks_significant_at_0_05"].sum()
    )

    # ------------------------------------------------------
    # 4. Create a combined monitoring summary
    # ------------------------------------------------------

    summary_rows = [
        {
            "category": "Data quality",
            "metric": "Total quality checks",
            "value": len(quality),
            "status": quality_status,
            "details": "Checks loaded from Program 76 results.",
        },
        {
            "category": "Data quality",
            "metric": "Passed checks",
            "value": pass_count,
            "status": "INFO",
            "details": "Checks with PASS status.",
        },
        {
            "category": "Data quality",
            "metric": "Warning checks",
            "value": warning_count,
            "status": "WARNING" if warning_count else "PASS",
            "details": "Checks requiring investigation.",
        },
        {
            "category": "Data quality",
            "metric": "Failed checks",
            "value": fail_count,
            "status": "FAIL" if fail_count else "PASS",
            "details": "Checks marked FAIL.",
        },
        {
            "category": "Data quality",
            "metric": "Unknown status checks",
            "value": unknown_count,
            "status": "FAIL" if unknown_count else "PASS",
            "details": "Statuses not recognized by this summary.",
        },
        {
            "category": "Data drift",
            "metric": "Features analyzed",
            "value": len(drift),
            "status": "INFO",
            "details": "Features loaded from Program 75 results.",
        },
        {
            "category": "Data drift",
            "metric": "Features with little PSI shift",
            "value": little_shift_count,
            "status": "INFO",
            "details": "PSI below 0.10.",
        },
        {
            "category": "Data drift",
            "metric": "Features with moderate PSI shift",
            "value": moderate_shift_count,
            "status": "INFO",
            "details": "PSI from 0.10 to below 0.25.",
        },
        {
            "category": "Data drift",
            "metric": "Features with large PSI shift",
            "value": large_shift_count,
            "status": "INFO",
            "details": "PSI at or above 0.25.",
        },
        {
            "category": "Data drift",
            "metric": "KS significant features",
            "value": significant_count,
            "status": "INFO",
            "details": "KS p-value below 0.05.",
        },
    ]

    summary = pd.DataFrame(summary_rows)

    summary.to_csv(SUMMARY_FILE, index=False)

    # ------------------------------------------------------
    # 5. Generate readable report
    # ------------------------------------------------------

    with REPORT_FILE.open("w", encoding="utf-8") as report:
        report.write("RETAILPULSE MONITORING SUMMARY\n")
        report.write("=" * 65 + "\n\n")

        report.write("DATA QUALITY\n")
        report.write("-" * 65 + "\n")
        report.write(f"Total checks: {len(quality)}\n")
        report.write(f"Passed: {pass_count}\n")
        report.write(f"Warnings: {warning_count}\n")
        report.write(f"Failures: {fail_count}\n")
        report.write(f"Unknown statuses: {unknown_count}\n")
        report.write(f"Quality status: {quality_status}\n\n")

        report.write("DATA DRIFT\n")
        report.write("-" * 65 + "\n")
        report.write(f"Features analyzed: {len(drift)}\n")
        report.write(
            f"Features with little PSI shift: "
            f"{little_shift_count}\n"
        )
        report.write(
            f"Features with moderate PSI shift: "
            f"{moderate_shift_count}\n"
        )
        report.write(
            f"Features with large PSI shift: "
            f"{large_shift_count}\n"
        )
        report.write(
            f"KS significant features: {significant_count}\n\n"
        )

        report.write("FEATURE-LEVEL RESULTS\n")
        report.write("-" * 65 + "\n")

        for _, row in drift.iterrows():
            report.write(f"Feature: {row['feature']}\n")
            report.write(f"  PSI: {row['psi']:.4f}\n")
            report.write(f"  PSI band: {row['psi_band']}\n")
            report.write(
                f"  KS p-value: {row['ks_p_value']:.6g}\n"
            )
            report.write(f"  KS result: {row['ks_result']}\n\n")

        report.write("INTERPRETATION\n")
        report.write("-" * 65 + "\n")
        report.write(
            "PSI bands are common heuristics, not universal rules.\n"
        )
        report.write(
            "Statistical significance does not by itself prove "
            "meaningful business impact or model degradation.\n"
        )
        report.write(
            "This program summarizes existing outputs; it does not "
            "recalculate the original quality or drift analyses.\n"
        )
        report.write(
            "No source dataset or input report was modified.\n"
        )

    # ------------------------------------------------------
    # 6. Display summary
    # ------------------------------------------------------

    print("\nDATA QUALITY")
    print(f"PASS: {pass_count}")
    print(f"WARNING: {warning_count}")
    print(f"FAIL: {fail_count}")
    print(f"Overall quality status: {quality_status}")

    print("\nDATA DRIFT")
    print(f"Features analyzed: {len(drift)}")
    print(f"Little PSI shift: {little_shift_count}")
    print(f"Moderate PSI shift: {moderate_shift_count}")
    print(f"Large PSI shift: {large_shift_count}")
    print(f"KS significant features: {significant_count}")

    print(f"\nCSV summary: {SUMMARY_FILE}")
    print(f"Text report: {REPORT_FILE}")
    print("\nOriginal inputs were not modified.")


if __name__ == "__main__":
    main()
