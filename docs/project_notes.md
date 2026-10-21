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
## 11. Program 74: Transaction Outlier Analysis

### Objective
Analyze unusual transaction quantities and line values in the prepared retail sales dataset. The program identifies statistically unusual records for further investigation without deleting or modifying source data.

### Input Dataset
- File: `data/processed/sales_analysis.parquet`
- Rows analyzed: 1,019,654
- Rows skipped due to invalid numeric values: 0
- Measures analyzed: `quantity` and `line_value`

### Methods
- **Interquartile Range (IQR):** Flags values below Q1 - 1.5 × IQR or above Q3 + 1.5 × IQR.
- **Z-score:** Flags values whose absolute Z-score exceeds 3. Population standard deviation is used (`ddof=0`).

### Results
- Transactions flagged by at least one method: 99,939 (9.80%).
- Quantity IQR flags: 53,630 (5.26%).
- Quantity Z-score flags: 1,560 (0.15%).
- Line-value IQR flags: 84,005 (8.24%).
- Line-value Z-score flags: 1,555 (0.15%).
- Maximum recorded quantity: 80,995.
- Maximum recorded line value: 168,469.60.

The combined flagged count represents the union of records flagged by any method, so a record flagged by multiple methods is counted once.

### Generated Outputs
- `data/processed/transaction_outlier_report.txt` — summary statistics, thresholds, counts, and limitations.
- `data/processed/transaction_outlier_analysis.csv` — flagged records and their outlier indicators and Z-scores.
- `data/processed/transaction_outlier_boxplots.png` — boxplots for the analyzed measures.

### Validation
- Python syntax compilation passed.
- Program completed successfully against the prepared dataset.
- Output CSV contained 99,939 rows and 15 columns.
- All four outlier-flag totals matched the report.
- The boxplot image was verified as a valid PNG measuring 1902 × 948 pixels.
- Invoice IDs were checked with a string data type; no missing invoice IDs were found in the output.

### Interpretation and Limitations
- Statistical flags are investigation signals, not proof of incorrect transactions or fraud.
- Large quantities or line values may represent legitimate bulk orders.
- Strongly skewed retail data can affect raw Z-score behavior.
- Business context is needed before excluding or correcting any flagged records.
- The program does not establish whether transactions are fraudulent.
- The source dataset is not modified by this analysis.
