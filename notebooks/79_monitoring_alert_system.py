from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


# ==========================================================
# PROGRAM 79: MONITORING ALERT SYSTEM
# RetailPulse - AI-Powered Customer Analytics Platform
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

QUALITY_FILE = DATA_DIR / "data_quality_results.csv"
DRIFT_FILE = DATA_DIR / "data_drift_results.csv"

ALERT_REPORT = DATA_DIR / "monitoring_alert_report.txt"
ALERT_CSV = DATA_DIR / "monitoring_alert_results.csv"

# PSI thresholds: commonly used heuristics
PSI_WARNING_THRESHOLD = 0.10
PSI_FAIL_THRESHOLD = 0.25


def load_csv(file_path):
    """Load a required CSV file or raise a clear error."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}\n"
            "Run the relevant earlier monitoring program first."
        )

    return pd.read_csv(file_path)


def create_alert(alert_type, status, message):
    """Return one standardized alert record."""

    return {
        "alert_type": alert_type,
        "status": status,
        "message": message,
    }


def evaluate_quality(quality_df):
    """Evaluate quality check statuses."""

    required_columns = {"check_name", "status"}

    if not required_columns.issubset(quality_df.columns):
        raise ValueError(
            "Quality results must contain these columns: "
            f"{sorted(required_columns)}"
        )

    alerts = []

    statuses = (
        quality_df["status"]
        .fillna("UNKNOWN")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    fail_count = int((statuses == "FAIL").sum())
    warning_count = int((statuses == "WARNING").sum())
    unknown_count = int(
        (~statuses.isin(["PASS", "WARNING", "FAIL"])).sum()
    )

    if fail_count > 0:
        alerts.append(
            create_alert(
                "DATA_QUALITY",
                "FAIL",
                f"{fail_count} quality check(s) failed.",
            )
        )

    elif unknown_count > 0:
        alerts.append(
            create_alert(
                "DATA_QUALITY",
                "WARNING",
                f"{unknown_count} quality check(s) have unknown statuses.",
            )
        )

    elif warning_count > 0:
        alerts.append(
            create_alert(
                "DATA_QUALITY",
                "WARNING",
                f"{warning_count} quality check(s) require investigation.",
            )
        )

    else:
        alerts.append(
            create_alert(
                "DATA_QUALITY",
                "PASS",
                "All quality checks passed.",
            )
        )

    return alerts


def evaluate_drift(drift_df):
    """Evaluate PSI values for drift alerts."""

    required_columns = {"feature", "psi"}

    if not required_columns.issubset(drift_df.columns):
        raise ValueError(
            "Drift results must contain these columns: "
            f"{sorted(required_columns)}"
        )

    alerts = []

    psi_values = pd.to_numeric(drift_df["psi"], errors="coerce")

    invalid_count = int(
        (psi_values.isna() | ~psi_values.map(
            lambda value: value == value
        )).sum()
    )

    # A missing or invalid PSI value must not be treated as healthy.
    if invalid_count > 0:
        alerts.append(
            create_alert(
                "DATA_DRIFT",
                "WARNING",
                f"{invalid_count} feature(s) have missing or invalid PSI values.",
            )
        )

    valid_drift = drift_df.loc[psi_values.notna()].copy()
    valid_drift["psi"] = psi_values.loc[psi_values.notna()]

    # Negative PSI values are invalid for this monitoring rule.
    negative_count = int((valid_drift["psi"] < 0).sum())

    if negative_count > 0:
        alerts.append(
            create_alert(
                "DATA_DRIFT",
                "WARNING",
                f"{negative_count} feature(s) have negative PSI values.",
            )
        )

    for _, row in valid_drift.iterrows():
        feature = str(row["feature"])
        psi = float(row["psi"])

        if psi < 0:
            continue

        if psi >= PSI_FAIL_THRESHOLD:
            alerts.append(
                create_alert(
                    f"DRIFT:{feature}",
                    "FAIL",
                    f"{feature} has large data drift (PSI={psi:.4f}).",
                )
            )

        elif psi >= PSI_WARNING_THRESHOLD:
            alerts.append(
                create_alert(
                    f"DRIFT:{feature}",
                    "WARNING",
                    f"{feature} has moderate data drift (PSI={psi:.4f}).",
                )
            )

        else:
            alerts.append(
                create_alert(
                    f"DRIFT:{feature}",
                    "PASS",
                    f"{feature} has low data drift (PSI={psi:.4f}).",
                )
            )

    if len(drift_df) == 0:
        alerts.append(
            create_alert(
                "DATA_DRIFT",
                "WARNING",
                "No drift features were available to evaluate.",
            )
        )

    return alerts


def determine_overall_status(alerts):
    """Calculate overall monitoring status."""

    statuses = [alert["status"] for alert in alerts]

    if "FAIL" in statuses:
        return "FAIL"

    if "WARNING" in statuses:
        return "WARNING"

    return "PASS"


def main():
    print("=" * 60)
    print("RETAILPULSE - MONITORING ALERT SYSTEM")
    print("=" * 60)

    quality_df = load_csv(QUALITY_FILE)
    drift_df = load_csv(DRIFT_FILE)

    alerts = []
    alerts.extend(evaluate_quality(quality_df))
    alerts.extend(evaluate_drift(drift_df))

    overall_status = determine_overall_status(alerts)
    run_timestamp = datetime.now(timezone.utc).isoformat()

    alert_df = pd.DataFrame(alerts)
    alert_df.insert(0, "run_timestamp_utc", run_timestamp)

    ALERT_CSV.parent.mkdir(parents=True, exist_ok=True)
    alert_df.to_csv(ALERT_CSV, index=False)

    report_lines = [
        "=" * 60,
        "RETAILPULSE - MONITORING ALERT REPORT",
        "=" * 60,
        f"Run timestamp (UTC): {run_timestamp}",
        f"Overall status: {overall_status}",
        f"Quality checks evaluated: {len(quality_df)}",
        f"Drift features evaluated: {len(drift_df)}",
        "",
        "ALERT DETAILS",
        "-" * 60,
    ]

    for alert in alerts:
        report_lines.append(
            f"[{alert['status']}] "
            f"{alert['alert_type']}: {alert['message']}"
        )

    report_lines.extend([
        "",
        "PSI THRESHOLDS",
        f"PASS: PSI < {PSI_WARNING_THRESHOLD}",
        (
            f"WARNING: {PSI_WARNING_THRESHOLD} <= PSI "
            f"< {PSI_FAIL_THRESHOLD}"
        ),
        f"FAIL: PSI >= {PSI_FAIL_THRESHOLD}",
        "",
        "Note: PSI thresholds are heuristic monitoring rules.",
        "An alert indicates a condition to investigate, not proof",
        "of model failure or business impact.",
        "=" * 60,
    ])

    report_text = "\n".join(report_lines) + "\n"
    ALERT_REPORT.write_text(report_text, encoding="utf-8")

    print(report_text)
    print(f"CSV output: {ALERT_CSV}")
    print(f"Text report: {ALERT_REPORT}")


if __name__ == "__main__":
    main()
