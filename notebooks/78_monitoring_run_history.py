from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


# ==========================================================
# PROGRAM 78: MONITORING RUN HISTORY
# RetailPulse - AI-Powered Customer Analytics Platform
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

QUALITY_FILE = DATA_DIR / "data_quality_results.csv"
DRIFT_FILE = DATA_DIR / "data_drift_results.csv"

HISTORY_FILE = DATA_DIR / "monitoring_run_history.csv"


def main():
    print("=" * 65)
    print("PROGRAM 78: MONITORING RUN HISTORY")
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

    required_quality = {"check_name", "status", "affected_rows"}
    required_drift = {
        "feature",
        "psi",
        "ks_p_value",
        "ks_significant_at_0_05",
    }

    if not required_quality.issubset(quality.columns):
        raise ValueError("Quality results have unexpected columns.")

    if not required_drift.issubset(drift.columns):
        raise ValueError("Drift results have unexpected columns.")

    if quality.empty or drift.empty:
        raise ValueError("Monitoring input results cannot be empty.")

    # ------------------------------------------------------
    # 2. Calculate quality metrics
    # ------------------------------------------------------

    statuses = quality["status"].astype(str).str.upper().str.strip()

    pass_count = int((statuses == "PASS").sum())
    warning_count = int((statuses == "WARNING").sum())
    fail_count = int((statuses == "FAIL").sum())

    unknown_count = int(
    (~statuses.isin(["PASS", "WARNING", "FAIL"])).sum()
)

    if fail_count > 0 or unknown_count > 0:
        quality_status = "FAIL"
    elif warning_count > 0:
        quality_status = "WARNING"
    else:
        quality_status = "PASS"

    # ------------------------------------------------------
    # 3. Calculate drift metrics
    # ------------------------------------------------------

    psi = pd.to_numeric(drift["psi"], errors="coerce")
    ks_p_values = pd.to_numeric(
        drift["ks_p_value"], errors="coerce"
    )

    if psi.isna().any() or ks_p_values.isna().any():
        raise ValueError("Drift metrics contain invalid values.")

    significance = (
        drift["ks_significant_at_0_05"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False})
    )

    if significance.isna().any():
        raise ValueError("KS significance flags contain invalid values.")

    little_shift_count = int((psi < 0.10).sum())
    moderate_shift_count = int(((psi >= 0.10) & (psi < 0.25)).sum())
    large_shift_count = int((psi >= 0.25).sum())
    significant_ks_count = int(significance.sum())

    # ------------------------------------------------------
    # 4. Create the current monitoring record
    # ------------------------------------------------------

    run_time = datetime.now(timezone.utc).isoformat(timespec="seconds")

    current_run = pd.DataFrame(
        [
            {
                "run_timestamp_utc": run_time,
                "quality_checks": len(quality),
                "quality_pass": pass_count,
                "quality_warning": warning_count,
                "quality_fail": fail_count,
                "quality_unknown": unknown_count,
                "quality_status": quality_status,
                "drift_features": len(drift),
                "psi_little_shift": little_shift_count,
                "psi_moderate_shift": moderate_shift_count,
                "psi_large_shift": large_shift_count,
                "ks_significant_features": significant_ks_count,
            }
        ]
    )

    # ------------------------------------------------------
    # 5. Append to history, preserving existing records
    # ------------------------------------------------------

    if HISTORY_FILE.exists():
        previous = pd.read_csv(HISTORY_FILE)

        expected_columns = current_run.columns.tolist()

        if previous.columns.tolist() != expected_columns:
            raise ValueError(
                "Existing history file has an unexpected schema. "
                "It was not changed."
            )

        history = pd.concat(
            [previous, current_run],
            ignore_index=True,
        )
    else:
        history = current_run.copy()

    history.to_csv(HISTORY_FILE, index=False)

    # ------------------------------------------------------
    # 6. Display run and history summary
    # ------------------------------------------------------

    print(f"\nRun timestamp (UTC): {run_time}")
    print(f"Quality status: {quality_status}")
    print(f"Quality checks: {len(quality)}")
    print(f"PASS: {pass_count}")
    print(f"WARNING: {warning_count}")
    print(f"FAIL: {fail_count}")
    print(f"Unknown: {unknown_count}")

    print(f"\nDrift features: {len(drift)}")
    print(f"PSI little shift: {little_shift_count}")
    print(f"PSI moderate shift: {moderate_shift_count}")
    print(f"PSI large shift: {large_shift_count}")
    print(f"KS significant features: {significant_ks_count}")

    print(f"\nTotal monitoring runs recorded: {len(history)}")
    print(f"History file: {HISTORY_FILE}")
    print("\nInput quality and drift reports were not modified.")


if __name__ == "__main__":
    main()
