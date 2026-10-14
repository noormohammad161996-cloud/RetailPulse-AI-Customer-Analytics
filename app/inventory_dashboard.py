# File: app/inventory_dashboard.py
# Purpose: Interactive Streamlit dashboard for inventory demand analysis.

from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_dashboard_data.csv"
)

st.set_page_config(
    page_title="RetailPulse Inventory Dashboard",
    page_icon="📦",
    layout="wide",
)

st.title("📦 RetailPulse — Inventory Analytics")
st.caption(
    "Explore historical product demand and preliminary inventory "
    "planning estimates."
)

if not DATA_FILE.exists():
    st.error(f"Dashboard dataset not found: {DATA_FILE}")
    st.info("Run Program 52 before starting this dashboard.")
    st.stop()

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df = load_data(str(DATA_FILE))

# Sidebar filters
st.sidebar.header("Filters")

categories = sorted(
    df["inventory_review_category"].dropna().unique().tolist()
)

selected_categories = st.sidebar.multiselect(
    "Inventory review category",
    options=categories,
    default=categories,
)

search_text = st.sidebar.text_input(
    "Search product ID or name"
).strip().lower()

filtered = df[
    df["inventory_review_category"].isin(selected_categories)
].copy()

if search_text:
    filtered = filtered[
        filtered["product_id"].astype(str).str.lower().str.contains(
            search_text, na=False
        )
        | filtered["product_name"].astype(str).str.lower().str.contains(
            search_text, na=False
        )
    ]

# Summary metrics
col1, col2, col3 = st.columns(3)

col1.metric("Products displayed", f"{len(filtered):,}")
col2.metric(
    "Total recorded units",
    f"{filtered['total_recorded_quantity'].sum():,.0f}",
)
col3.metric(
    "High-variability products",
    f"{(filtered['inventory_review_category'] == 'High demand variability').sum():,}",
)

st.divider()

# Category chart
st.subheader("Products by review category")

category_counts = (
    filtered["inventory_review_category"]
    .value_counts()
    .rename_axis("Category")
    .reset_index(name="Products")
)

if not category_counts.empty:
    st.bar_chart(
        category_counts,
        x="Category",
        y="Products",
    )
else:
    st.info("No products match the selected filters.")

# Product table
st.subheader("Product demand and planning estimates")

display_columns = [
    "product_id",
    "product_name",
    "months_with_sales",
    "total_recorded_quantity",
    "average_monthly_demand",
    "demand_cv",
    "expected_lead_time_demand",
    "safety_stock_estimate",
    "reorder_point_estimate",
    "inventory_review_category",
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True,
)

# Product details
st.subheader("Inspect one product")

if not filtered.empty:
    selected_product = st.selectbox(
        "Choose a product",
        options=filtered["product_id"].astype(str).tolist(),
        format_func=lambda product_id: (
            f"{product_id} — "
            f"{filtered.loc[filtered['product_id'].astype(str) == product_id, 'product_name'].iloc[0]}"
        ),
    )

    product = filtered[
        filtered["product_id"].astype(str) == selected_product
    ].iloc[0]

    st.write(f"**Product:** {product['product_name']}")
    st.write(
        f"**Review category:** "
        f"{product['inventory_review_category']}"
    )
    st.write(
        f"**Average monthly recorded demand:** "
        f"{product['average_monthly_demand']:,.2f} units"
    )
    st.write(
        f"**Preliminary reorder-point estimate:** "
        f"{product['reorder_point_estimate']:,.2f} units"
    )

st.warning(
    "These reorder points are preliminary estimates based on "
    "historical sales and assumed lead time/service level. "
    "Actual stock levels, open purchase orders, supplier lead times, "
    "and stockout records are unavailable. Do not use these estimates "
    "as purchase orders without validating the assumptions."
)

# Download filtered results
csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered inventory data (CSV)",
    data=csv_data,
    file_name="retailpulse_inventory_dashboard.csv",
    mime="text/csv",
)

st.caption("RetailPulse | Inventory analysis prototype")
