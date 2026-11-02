
import streamlit as st

# --------------------------------------------------
# RetailPulse - Main Application
# --------------------------------------------------

st.set_page_config(
    page_title="RetailPulse Analytics Platform",
    page_icon="📊",
    layout="wide"
)

# Define application pages
inventory_page = st.Page(
    "inventory_dashboard.py",
    title="Inventory Analysis",
    icon="📦",
    default=True
)

country_page = st.Page(
    "country_analysis.py",
    title="Country Analysis",
    icon="🌍"
)

# Create sidebar navigation
navigation = st.navigation(
    {
        "RetailPulse Analytics": [
            inventory_page,
            country_page
        ]
    },
    position="sidebar"
)

# Run selected page
navigation.run()
