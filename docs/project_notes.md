# RetailPulse — Inventory Analytics Project Notes

## 1. Project Overview

RetailPulse is a retail analytics project that uses historical transaction data to study product demand, demand variability, customer behavior, and sales forecasting.

The Inventory Analytics Dashboard provides an interactive interface for exploring product-level demand and preliminary inventory planning estimates.

## 2. Dashboard Features

- **Inventory overview:** Displays the number of products, total historically recorded units, high-variability products, and products with limited sales history.
- **Inventory review category filters:** Filter products using inventory review classifications.
- **Demand risk-review filters:** Filter products using demand risk classifications.
- **Product search:** Search by product ID or product name.
- **Product details:** Inspect an individual product's recorded demand, coefficient of variation (CV), months with recorded sales, estimated lead-time demand, safety stock, and preliminary reorder point.
- **Visualizations:** Compare the number of products in different review categories.
- **Filtered CSV export:** Download the currently filtered inventory analysis results.
- **Reset all filters:** Restore the dashboard's default filter selections and clear the product search.

## 3. Technology Stack

- Python
- Pandas
- Streamlit
- Data visualization through Streamlit charts
- CSV for exporting filtered results
- Git and GitHub for version control

## 4. Data and Scope

The analysis uses historical retail transaction data. Monthly product demand is summarized using the available sales history.

The current inventory analysis includes 4,916 products and 24 monthly periods from December 2009 through November 2011. December 2011 is excluded because the source data for that month is incomplete.

The dashboard reports historical recorded units, not current stock on hand.

## 5. Inventory Planning Method

The dashboard presents preliminary inventory planning estimates, including:

- Average monthly recorded demand
- Demand coefficient of variation
- Expected demand during the assumed supplier lead time
- Approximate safety stock
- Preliminary reorder point

These values depend on assumptions about supplier lead time and service level. They are analytical estimates and should not be treated as confirmed purchasing instructions.

## 6. Testing and Validation

The following dashboard behaviors were manually tested:

- Inventory overview loads and displays summary metrics.
- Inventory review category filters update the displayed results.
- Demand risk-review category filters update the displayed results.
- Product search filters products by ID or name.
- Selecting a product displays its details.
- Reset all filters restores the default view without the previous Streamlit session-state error.
- Filtered CSV export downloads successfully.

These are manual functional checks, not a complete automated test suite.

## 7. Known Limitations

- Current stock-on-hand quantities are unavailable.
- Open purchase orders and supplier lead-time records are unavailable.
- Stockout events are not confirmed by the source data.
- Zero recorded sales do not necessarily mean zero actual demand.
- Reorder points depend on assumed planning parameters.
- Demand risk categories are review flags, not confirmed stockout probabilities.

## 8. Run the Dashboard

From the project root, activate the project's virtual environment if necessary, then run:

```bash
python -m streamlit run app/inventory_dashboard.py
```

Open the local URL printed in the terminal, normally:

`http://localhost:8501`

## 9. Next Improvements

- Add automated tests for filter, search, reset, and export behavior.
- Validate inventory assumptions using real stock and supplier data if available.
- Improve the dashboard's layout and product-level visualizations.
- Document data preparation and forecasting evaluation.
- Keep the project README and GitHub repository synchronized with tested code.

## 10. Project Status

The Inventory Analytics Dashboard is a working prototype. Its filters, product search, product inspection, reset behavior, and CSV export have passed manual checks. Further validation is required before its inventory estimates can be used for real operational decisions.