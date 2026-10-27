from pathlib import Path

import pandas as pd
import streamlit as st


# ==========================================================
# PROGRAM 80: RETAILPULSE MONITORING DASHBOARD
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

QUALITY_FILE = DATA_DIR / "data_quality_results.csv"
DRIFT_FILE = DATA_DIR / "data_drift_results.csv"
SUMMARY_FILE = DATA_DIR / "quality_drift_summary.csv"
HISTORY_FILE = DATA_DIR / "monitoring_run_history.csv"
ALERT_FILE = DATA_DIR / "monitoring_alert_results.csv"
ALERT_REPORT_FILE = DATA_DIR / "monitoring_alert_report.txt"

st.set_page_config(
    page_title="RetailPulse | Monitoring",
    page_icon="📊",
    layout="wide",
)

st.title("RetailPulse Monitoring Dashboard")
st.caption(
    "Program 80 | Data Quality, Drift Detection, Monitoring History & Alerts"
)


# ----------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------

@st.cache_data
def load_csv(path_string):
    path = Path(path_string)

    if not path.exists():
        return None

    try:
        return pd.read_csv(path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        return None


def normalize_status(series):
    return series.fillna("UNKNOWN").astype(str).str.strip().str.upper()


def show_file_warning(label, path):
    if not path.exists():
        st.warning(f"{label} is missing: {path.relative_to(PROJECT_ROOT)}")


quality_df = load_csv(str(QUALITY_FILE))
drift_df = load_csv(str(DRIFT_FILE))
summary_df = load_csv(str(SUMMARY_FILE))
history_df = load_csv(str(HISTORY_FILE))
alert_df = load_csv(str(ALERT_FILE))


# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------

st.sidebar.header("Dashboard Controls")

if st.sidebar.button("Refresh data", width="stretch"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(
    "Refresh reloads the existing monitoring reports. "
    "It does not rerun Programs 75–79."
)

available_sections = [
    "Overview",
    "Data Quality",
    "Data Drift",
    "Monitoring History",
    "Alert Center",
]

selected_section = st.sidebar.radio(
    "Navigate",
    available_sections,
)


# ----------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------

def get_numeric_column(df, column):
    if df is None or column not in df.columns:
        return pd.Series(dtype="float64")

    return pd.to_numeric(df[column], errors="coerce")


def display_missing_file(message):
    st.info(message)


def display_status_counts(df):
    if df is None or "status" not in df.columns:
        display_missing_file("Quality status data is unavailable.")
        return

    statuses = normalize_status(df["status"])
    counts = statuses.value_counts()

    cols = st.columns(4)

    for col, label in zip(
        cols,
        ["PASS", "WARNING", "FAIL", "UNKNOWN"],
    ):
        col.metric(label, int(counts.get(label, 0)))


def display_alert_table(df):
    if df is None or df.empty:
        display_missing_file("No alert records are available.")
        return

    preferred = [
        column
        for column in [
            "run_timestamp_utc",
            "alert_type",
            "status",
            "message",
        ]
        if column in df.columns
    ]

    if preferred:
        st.dataframe(
            df[preferred],
            width="stretch",
            hide_index=True,
        )
    else:
        st.dataframe(df, width="stretch", hide_index=True)


# ----------------------------------------------------------
# OVERVIEW
# ----------------------------------------------------------

def render_overview():
    st.header("Monitoring Overview")

    if quality_df is None:
        show_file_warning("Data quality results", QUALITY_FILE)

    if drift_df is None:
        show_file_warning("Data drift results", DRIFT_FILE)

    if alert_df is None:
        show_file_warning("Monitoring alerts", ALERT_FILE)

    quality_statuses = (
        normalize_status(quality_df["status"])
        if quality_df is not None and "status" in quality_df.columns
        else pd.Series(dtype="object")
    )

    quality_failures = int((quality_statuses == "FAIL").sum())
    quality_warnings = int((quality_statuses == "WARNING").sum())
    quality_unknown = int(
        (~quality_statuses.isin(["PASS", "WARNING", "FAIL"])).sum()
    )

    psi_values = get_numeric_column(drift_df, "psi")
    valid_psi = psi_values.dropna()

    drift_failures = int((valid_psi >= 0.25).sum())
    drift_warnings = int(
        ((valid_psi >= 0.10) & (valid_psi < 0.25)).sum()
    )

    if quality_failures or drift_failures:
        overall_status = "FAIL"
    elif quality_warnings or quality_unknown or drift_warnings:
        overall_status = "WARNING"
    elif quality_df is None or drift_df is None:
        overall_status = "UNKNOWN"
    else:
        overall_status = "PASS"

    latest_run = "Not available"

    if (
        history_df is not None
        and not history_df.empty
        and "run_timestamp_utc" in history_df.columns
    ):
        latest_run = str(history_df["run_timestamp_utc"].iloc[-1])

    if (
        alert_df is not None
        and not alert_df.empty
        and "run_timestamp_utc" in alert_df.columns
    ):
        latest_run = str(alert_df["run_timestamp_utc"].iloc[-1])

    status_color = {
        "PASS": "normal",
        "WARNING": "off",
        "FAIL": "inverse",
        "UNKNOWN": "off",
    }[overall_status]

    st.caption(f"Current dashboard assessment: {overall_status}")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Quality Checks",
        len(quality_df) if quality_df is not None else "N/A",
    )

    c2.metric(
        "Quality Warnings",
        quality_warnings,
    )

    c3.metric(
        "Drift Features",
        len(drift_df) if drift_df is not None else "N/A",
    )

    c4.metric(
        "High Drift Features",
        drift_failures,
    )

    st.caption(f"Latest recorded monitoring run: {latest_run}")

    if overall_status == "FAIL":
        st.error("Monitoring requires urgent investigation.")
    elif overall_status == "WARNING":
        st.warning("Some monitoring checks require investigation.")
    elif overall_status == "PASS":
        st.success("Available monitoring checks passed.")
    else:
        st.info("Insufficient data to determine monitoring status.")

    st.subheader("Data Quality Status")
    display_status_counts(quality_df)

    st.subheader("Feature Drift")

    if drift_df is not None and {"feature", "psi"}.issubset(drift_df.columns):
        chart_df = drift_df[["feature", "psi"]].copy()
        chart_df["psi"] = pd.to_numeric(chart_df["psi"], errors="coerce")
        chart_df = chart_df.dropna(subset=["psi"])

        if not chart_df.empty:
            st.bar_chart(chart_df.set_index("feature")["psi"])

            st.caption(
                "PSI thresholds: below 0.10 = low, "
                "0.10 to below 0.25 = moderate, "
                "0.25 or above = large shift."
            )
        else:
            st.info("No valid PSI values are available.")
    else:
        st.info("Drift data needs feature and psi columns.")

    st.subheader("Latest Alerts")
    display_alert_table(alert_df)


# ----------------------------------------------------------
# DATA QUALITY
# ----------------------------------------------------------

def render_quality():
    st.header("Data Quality Monitoring")

    if quality_df is None:
        show_file_warning("Data quality results", QUALITY_FILE)
        return

    if "status" in quality_df.columns:
        display_status_counts(quality_df)

    st.subheader("Quality Check Details")

    if "status" in quality_df.columns:
        statuses = normalize_status(quality_df["status"])

        status_filter = st.multiselect(
            "Filter by status",
            options=sorted(statuses.unique().tolist()),
            default=sorted(statuses.unique().tolist()),
        )

        filtered_df = quality_df.loc[statuses.isin(status_filter)]
    else:
        filtered_df = quality_df

    st.dataframe(
        filtered_df,
        width="stretch",
        hide_index=True,
    )

    if summary_df is not None:
        st.subheader("Quality and Drift Summary")
        st.dataframe(
            summary_df,
            width="stretch",
            hide_index=True,
        )


# ----------------------------------------------------------
# DATA DRIFT
# ----------------------------------------------------------

def render_drift():
    st.header("Data Drift Analysis")

    if drift_df is None:
        show_file_warning("Data drift results", DRIFT_FILE)
        return

    if not {"feature", "psi"}.issubset(drift_df.columns):
        st.error("The drift CSV must contain feature and psi columns.")
        st.dataframe(drift_df, width="stretch")
        return

    display_df = drift_df.copy()
    display_df["psi"] = pd.to_numeric(
        display_df["psi"],
        errors="coerce",
    )

    def classify_psi(value):
        if pd.isna(value) or value < 0:
            return "INVALID"
        if value >= 0.25:
            return "FAIL"
        if value >= 0.10:
            return "WARNING"
        return "PASS"

    display_df["monitoring_status"] = display_df["psi"].apply(classify_psi)

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
    )

    chart_df = display_df.dropna(subset=["psi"])

    if not chart_df.empty:
        st.subheader("Population Stability Index (PSI)")
        st.bar_chart(chart_df.set_index("feature")["psi"])

    st.info(
        "PSI thresholds are heuristic. A drift alert does not by itself "
        "prove business impact or model degradation."
    )


# ----------------------------------------------------------
# MONITORING HISTORY
# ----------------------------------------------------------

def render_history():
    st.header("Monitoring Run History")

    if history_df is None:
        show_file_warning("Monitoring history", HISTORY_FILE)
        return

    if history_df.empty:
        st.info("No monitoring runs have been recorded yet.")
        return

    st.metric("Recorded Runs", len(history_df))

    if "run_timestamp_utc" in history_df.columns:
        st.dataframe(
            history_df.sort_values(
                "run_timestamp_utc",
                ascending=False,
            ),
            width="stretch",
            hide_index=True,
        )
    else:
        st.dataframe(
            history_df,
            width="stretch",
            hide_index=True,
        )

    possible_columns = [
        column
        for column in [
            "pass_count",
            "warning_count",
            "fail_count",
        ]
        if column in history_df.columns
    ]

    if possible_columns:
        st.subheader("Quality Results Across Runs")

        chart_df = history_df[possible_columns].apply(
            pd.to_numeric,
            errors="coerce",
        )

        if "run_timestamp_utc" in history_df.columns:
            chart_df.index = history_df["run_timestamp_utc"].astype(str)

        st.line_chart(chart_df)


# ----------------------------------------------------------
# ALERT CENTER
# ----------------------------------------------------------

def render_alerts():
    st.header("Monitoring Alert Center")

    if alert_df is None:
        show_file_warning("Alert results", ALERT_FILE)
    else:
        display_alert_table(alert_df)

        if "status" in alert_df.columns:
            statuses = normalize_status(alert_df["status"])

            if (statuses == "FAIL").any():
                st.error("One or more monitoring alerts have failed.")
            elif (statuses == "WARNING").any():
                st.warning("One or more monitoring warnings need attention.")
            else:
                st.success("No FAIL or WARNING statuses in the loaded alert records.")

    if ALERT_REPORT_FILE.exists():
        with st.expander("Read the complete alert report"):
            try:
                report_text = ALERT_REPORT_FILE.read_text(
                    encoding="utf-8"
                )
                st.text(report_text)
            except OSError as exc:
                st.error(f"Could not read alert report: {exc}")
    else:
        show_file_warning("Alert text report", ALERT_REPORT_FILE)


# ----------------------------------------------------------
# PAGE ROUTING
# ----------------------------------------------------------

if selected_section == "Overview":
    render_overview()
elif selected_section == "Data Quality":
    render_quality()
elif selected_section == "Data Drift":
    render_drift()
elif selected_section == "Monitoring History":
    render_history()
elif selected_section == "Alert Center":
    render_alerts()

st.divider()
st.caption(
    "RetailPulse Program 80 | Reads existing reports only. "
    "Use Programs 75–79 to refresh underlying monitoring results."
)
