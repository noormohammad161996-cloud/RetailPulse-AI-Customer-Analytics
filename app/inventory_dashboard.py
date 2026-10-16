# File: app/inventory_dashboard.py
# Purpose: RetailPulse inventory dashboard with interactive category filters,
# reliable reset behavior, product search, detailed views, and CSV export.

from pathlib import Path

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# 1. Configuration and data loading
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_dashboard_with_risk_review.csv"
)

st.set_page_config(
    page_title="RetailPulse Inventory Dashboard",
    page_icon="📦",
    layout="wide",
)

st.title("📦 RetailPulse — Inventory Analytics")
st.caption(
    "Explore historical product demand, demand variability, "
    "and preliminary inventory planning estimates."
)

if not DATA_FILE.exists():
    st.error(f"Dashboard dataset not found: {DATA_FILE}")
    st.info(
        "Run Program 52 to prepare the dashboard data and "
        "Program 73 to merge the risk-review categories."
    )
    st.stop()


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load dashboard data while keeping product IDs as strings."""
    return pd.read_csv(path, dtype={"product_id": str})


df = load_data(str(DATA_FILE))

required_columns = [
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
    "risk_review_category",
]
missing_columns = [column for column in required_columns if column not in df.columns]
if missing_columns:
    st.error("Missing required columns: " + ", ".join(missing_columns))
    st.info("Check the outputs from Programs 52 and 73.")
    st.stop()

if df.empty:
    st.warning("The dashboard dataset contains no products.")
    st.stop()

text_columns = [
    "product_id",
    "product_name",
    "inventory_review_category",
    "risk_review_category",
]
for column in text_columns:
    df[column] = df[column].fillna("").astype(str)

numeric_columns = [
    "months_with_sales",
    "total_recorded_quantity",
    "average_monthly_demand",
    "demand_cv",
    "expected_lead_time_demand",
    "safety_stock_estimate",
    "reorder_point_estimate",
]
for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")


# ---------------------------------------------------------
# 2. Sidebar filters
# Use checkboxes, so categories are visible and clickable.
# ---------------------------------------------------------
st.sidebar.header("Filters")
st.sidebar.caption("Tick the categories you want to include.")

if "reset_filters_trigger" not in st.session_state:
    st.session_state["reset_filters_trigger"] = 0
reset_generation = st.session_state["reset_filters_trigger"]

inventory_categories = sorted(
    category
    for category in df["inventory_review_category"].unique()
    if category.strip()
)
risk_categories = sorted(
    category
    for category in df["risk_review_category"].unique()
    if category.strip()
)

# Store checkbox values under widget-owned keys. Do not assign to these
# keys after widgets are created; Streamlit forbids that operation.
st.sidebar.subheader("Inventory review category")
selected_inventory_categories = [
    category
    for index, category in enumerate(inventory_categories)
    if st.sidebar.checkbox(
        category,
        value=True,
        key=f"inventory_category_{reset_generation}_{index}",
    )
]

st.sidebar.divider()
st.sidebar.subheader("Demand risk-review category")
selected_risk_categories = [
    category
    for index, category in enumerate(risk_categories)
    if st.sidebar.checkbox(
        category,
        value=True,
        key=f"risk_category_{reset_generation}_{index}",
    )
]

st.sidebar.divider()
search_text = st.sidebar.text_input(
    "Search product ID or name",
    placeholder="e.g. 10080 or cactus",
    key=f"product_search_{reset_generation}",
).strip().lower()

# Reset is performed by changing a separate trigger key. The category
# widgets are initialized from this trigger on the next rerun, rather
# than mutating widget-owned session-state keys after creation.
if st.sidebar.button("Reset all filters", key="reset_all_filters_button"):
    st.session_state["reset_filters_trigger"] += 1
    st.rerun()

# Apply category filters.
filtered = df[
    df["inventory_review_category"].isin(selected_inventory_categories)
    & df["risk_review_category"].isin(selected_risk_categories)
].copy()

if search_text:
    id_match = filtered["product_id"].str.lower().str.contains(
        search_text, regex=False, na=False
    )
    name_match = filtered["product_name"].str.lower().str.contains(
        search_text, regex=False, na=False
    )
    filtered = filtered[id_match | name_match]


# ---------------------------------------------------------
# 3. Summary metrics
# ---------------------------------------------------------
st.subheader("Inventory overview")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Products displayed", f"{len(filtered):,}")
col2.metric(
    "Total recorded units",
    f"{filtered['total_recorded_quantity'].sum():,.0f}",
)
col3.metric(
    "High-variability products",
    f"{(filtered['risk_review_category'] == 'High demand variability').sum():,}",
)
col4.metric(
    "Products with limited history",
    f"{(filtered['risk_review_category'] == 'Insufficient sales history').sum():,}",
)

st.caption(
    "Recorded units represent historical transaction quantities, "
    "not current inventory on hand."
)
st.divider()


# ---------------------------------------------------------
# 4. Category charts
# ---------------------------------------------------------
st.subheader("Products by inventory review category")
inventory_counts = (
    filtered["inventory_review_category"]
    .value_counts()
    .rename_axis("Category")
    .reset_index(name="Products")
)
if not inventory_counts.empty:
    inventory_counts = inventory_counts.sort_values("Products", ascending=True)
    st.bar_chart(
        inventory_counts.set_index("Category"),
        horizontal=True,
        width="stretch",
    )
else:
    st.info("No products match the selected inventory filters.")

st.subheader("Products by demand risk-review category")
risk_counts = (
    filtered["risk_review_category"]
    .value_counts()
    .rename_axis("Risk review category")
    .reset_index(name="Products")
)
if not risk_counts.empty:
    risk_counts = risk_counts.sort_values("Products", ascending=True)
    st.bar_chart(
        risk_counts.set_index("Risk review category"),
        horizontal=True,
        width="stretch",
    )
else:
    st.info("No products match the selected risk-review filters.")


# ---------------------------------------------------------
# 5. Product table
# ---------------------------------------------------------
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
    "risk_review_category",
]

if not filtered.empty:
    st.dataframe(
        filtered[display_columns],
        width="stretch",
        hide_index=True,
        column_config={
            "product_id": st.column_config.TextColumn("Product ID"),
            "product_name": st.column_config.TextColumn("Product name"),
            "months_with_sales": st.column_config.NumberColumn(
                "Months with sales", format="%d"
            ),
            "total_recorded_quantity": st.column_config.NumberColumn(
                "Total recorded units", format="%.0f"
            ),
            "average_monthly_demand": st.column_config.NumberColumn(
                "Avg. monthly demand", format="%.2f"
            ),
            "demand_cv": st.column_config.NumberColumn("Demand CV", format="%.2f"),
            "expected_lead_time_demand": st.column_config.NumberColumn(
                "Lead-time demand", format="%.2f"
            ),
            "safety_stock_estimate": st.column_config.NumberColumn(
                "Approx. safety stock", format="%.2f"
            ),
            "reorder_point_estimate": st.column_config.NumberColumn(
                "Preliminary reorder point", format="%.2f"
            ),
        },
    )
else:
    st.info(
        "No products match the current filters. Select more categories "
        "or clear the search."
    )


# ---------------------------------------------------------
# 6. Individual product inspection
# ---------------------------------------------------------
st.subheader("Inspect one product")
if not filtered.empty:
    product_options = (
        filtered[["product_id", "product_name"]]
        .drop_duplicates(subset=["product_id"])
        .sort_values("product_id")
        .reset_index(drop=True)
    )

    selected_product = st.selectbox(
        "Choose a product",
        options=product_options["product_id"].tolist(),
        format_func=lambda product_id: (
            f"{product_id} — "
            f"{product_options.loc[product_options['product_id'] == product_id, 'product_name'].iloc[0]}"
        ),
    )
    product = filtered[filtered["product_id"] == selected_product].iloc[0]
    left, right = st.columns(2)

    with left:
        st.write(f"**Product ID:** {product['product_id']}")
        st.write(f"**Product name:** {product['product_name']}")
        st.write(f"**Inventory review category:** {product['inventory_review_category']}")
        st.write(f"**Demand risk-review category:** {product['risk_review_category']}")
        months = product["months_with_sales"]
        months_text = f"{months:.0f}" if pd.notna(months) else "Unknown"
        st.write(f"**Months with recorded sales:** {months_text}")

    with right:
        details = [
            ("Average monthly recorded demand", "average_monthly_demand", "units"),
            ("Demand coefficient of variation", "demand_cv", ""),
            ("Expected lead-time demand", "expected_lead_time_demand", "units"),
            ("Approximate safety stock", "safety_stock_estimate", "units"),
            ("Preliminary reorder point", "reorder_point_estimate", "units"),
        ]
        for label, column, unit in details:
            value = product[column]
            formatted = f"{value:,.2f}" if pd.notna(value) else "Unavailable"
            suffix = f" {unit}" if unit and pd.notna(value) else ""
            st.write(f"**{label}:** {formatted}{suffix}")

    if product["risk_review_category"] == "Insufficient sales history":
        st.warning(
            "This product has limited recorded sales history. Treat its "
            "demand and reorder-point estimates cautiously."
        )
    elif product["risk_review_category"] == "High demand variability":
        st.warning(
            "This product has high variability relative to its average "
            "recorded demand. Review the historical pattern and validate "
            "the estimate before making decisions."
        )
else:
    st.info("Adjust the sidebar filters to inspect a product.")


# ---------------------------------------------------------
# 7. CSV export
# ---------------------------------------------------------
st.subheader("Export results")
csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered inventory data (CSV)",
    data=csv_data,
    file_name="retailpulse_inventory_risk_review.csv",
    mime="text/csv",
    width="stretch",
)

st.caption(
    "RetailPulse | Inventory analytics prototype | "
    "Risk categories are preliminary review flags."
)
st.warning(
    "Planning limitations: reorder points are preliminary estimates based "
    "on historical sales and assumed lead time/service level. Actual stock "
    "levels, open purchase orders, supplier lead times, and stockout records "
    "are unavailable. Risk categories are screening rules, not confirmed "
    "stockout probabilities. Validate assumptions before purchasing decisions."
)
