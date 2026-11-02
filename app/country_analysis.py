
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# RetailPulse - Country Analysis Dashboard
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "sales_analysis.parquet"

st.set_page_config(
    page_title="RetailPulse | Country Analysis",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 RetailPulse — Country Analysis")
st.caption("Country-wise retail sales, customer and order performance")


# --------------------------------------------------
# Load Data
# --------------------------------------------------

@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    df = pd.read_parquet(DATA_FILE)

    required = [
        "country",
        "invoice_id",
        "customer_id",
        "quantity",
        "line_value"
    ]

    missing = [
        column for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df["country"] = (
        df["country"]
        .fillna("Unknown")
        .astype(str)
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df["line_value"] = pd.to_numeric(
        df["line_value"],
        errors="coerce"
    )

    return df


try:
    df = load_data()

except Exception as error:
    st.error(f"Unable to load country analysis data: {error}")
    st.stop()


# --------------------------------------------------
# Country-level Aggregation
# --------------------------------------------------

country_summary = (
    df.groupby("country")
    .agg(
        orders=("invoice_id", "nunique"),
        customers=("customer_id", "nunique"),
        quantity_sold=("quantity", "sum"),
        revenue=("line_value", "sum"),
        transaction_rows=("invoice_id", "size")
    )
    .reset_index()
)

country_summary = country_summary.sort_values(
    "revenue",
    ascending=False
)

all_countries = sorted(
    country_summary["country"].unique()
)


# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------

st.sidebar.header("Analysis Filters")

st.sidebar.caption(
    "Choose countries to filter the complete dashboard. "
    "Leave the selection empty to show all countries."
)

selected_countries = st.sidebar.multiselect(
    "Select countries",
    options=all_countries,
    default=[],
    placeholder="Choose one or more countries"
)

# Empty selection displays all countries.
if selected_countries:

    filtered = country_summary[
        country_summary["country"].isin(
            selected_countries
        )
    ].copy()

else:

    filtered = country_summary.copy()


filtered = filtered.sort_values(
    "revenue",
    ascending=False
)


# --------------------------------------------------
# KPI Metrics
# --------------------------------------------------

st.subheader("Country Performance Overview")

# Sum country-level values for the selected countries.
total_revenue = filtered["revenue"].sum()
total_orders = filtered["orders"].sum()
total_quantity = filtered["quantity_sold"].sum()

country_count = filtered["country"].nunique()

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Countries Selected",
    f"{country_count:,}"
)

k2.metric(
    "Recorded Revenue",
    f"{total_revenue:,.2f}"
)

k3.metric(
    "Distinct Orders",
    f"{total_orders:,}"
)

k4.metric(
    "Quantity Sold",
    f"{total_quantity:,.0f}"
)

st.caption(
    "Revenue is calculated as the sum of historical "
    "transaction line values. It is not a measure of "
    "current inventory or profit."
)

st.divider()


# --------------------------------------------------
# Revenue Analysis
# --------------------------------------------------

st.subheader("Top 10 Countries by Recorded Revenue")

top_countries = (
    filtered.head(10)
    .set_index("country")
)

if not top_countries.empty:
    st.bar_chart(
        top_countries["revenue"],
        height=400
    )
else:
    st.info("No country data available.")


# --------------------------------------------------
# Order Analysis
# --------------------------------------------------

st.subheader("Country-wise Order Comparison")

order_chart = (
    filtered.sort_values(
        "orders",
        ascending=False
    )
    .head(10)
    .set_index("country")
)

if not order_chart.empty:
    st.bar_chart(
        order_chart["orders"],
        height=400
    )
else:
    st.info("No order data available.")

st.divider()


# --------------------------------------------------
# Country Performance Details
# --------------------------------------------------

st.subheader("Country Performance Details")

display_columns = [
    "country",
    "orders",
    "customers",
    "quantity_sold",
    "revenue",
    "transaction_rows"
]

display_data = filtered[
    display_columns
].copy()

display_data = display_data.rename(
    columns={
        "country": "Country",
        "orders": "Distinct Orders",
        "customers": "Distinct Customers",
        "quantity_sold": "Quantity Sold",
        "revenue": "Recorded Revenue",
        "transaction_rows": "Transaction Rows"
    }
)

st.dataframe(
    display_data,
    width="stretch",
    hide_index=True
)


# --------------------------------------------------
# Individual Country Inspection
# --------------------------------------------------

st.subheader("Inspect an Individual Country")

# This selector uses all countries independently
# of the sidebar filter.
selected_country = st.selectbox(
    "Choose a country",
    options=all_countries,
    index=(
        all_countries.index("United Kingdom")
        if "United Kingdom" in all_countries
        else 0
    )
)

country_detail = country_summary.loc[
    country_summary["country"] == selected_country
].iloc[0]

a, b, c, d = st.columns(4)

a.metric(
    "Recorded Revenue",
    f"{country_detail['revenue']:,.2f}"
)

b.metric(
    "Distinct Orders",
    f"{country_detail['orders']:,}"
)

c.metric(
    "Distinct Customers",
    f"{country_detail['customers']:,}"
)

d.metric(
    "Quantity Sold",
    f"{country_detail['quantity_sold']:,.0f}"
)


# --------------------------------------------------
# CSV Export
# --------------------------------------------------

st.divider()

st.subheader("Export Country Analysis")

csv_data = display_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Country Analysis (CSV)",
    data=csv_data,
    file_name="retailpulse_country_analysis.csv",
    mime="text/csv",
    width="stretch"
)


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.caption(
    "RetailPulse | Country Analysis | "
    "Based on historical retail transactions"
)
