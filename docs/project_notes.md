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

- **Interquartile Range (IQR):** Flags values below Q1 − 1.5 × IQR or above Q3 + 1.5 × IQR.
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

## 12. Program 75: Data Drift Detection

### Objective

Compare numerical feature distributions across two historical periods to identify potential data drift in retail transactions.

### Input Dataset

- File: `data/processed/sales_analysis.parquet`
- Features: `quantity`, `unit_price`, and `line_value`
- Reference period: January 1–June 30, 2011
- Comparison period: July 1–November 30, 2011
- Reference rows: 198,451
- Comparison rows: 265,062

December 2011 was excluded because the month is incomplete.

### Methods

- **Population Stability Index (PSI):** Compares distribution proportions using reference-period quantile bins.
- **Kolmogorov–Smirnov (KS) two-sample test:** Compares the empirical distributions of numerical values. A p-value below 0.05 is marked statistically significant.

### Results

| Feature | Reference mean | Comparison mean | PSI | KS p-value |
|---|---:|---:|---:|---:|
| Quantity | 10.7968 | 10.4589 | 0.0019 | 2.96703e-16 |
| Unit price | 3.9798 | 3.6980 | 0.0186 | 2.35288e-201 |
| Line value | 20.1698 | 19.6234 | 0.0092 | 9.11176e-102 |

All PSI values are below 0.10, indicating little distribution shift under the common PSI heuristic. All three KS tests are statistically significant at the 0.05 level. With large samples, statistical significance can occur even when distribution differences are small.

### Generated Outputs

- `data/processed/data_drift_report.txt` — methods, results, and limitations.
- `data/processed/data_drift_results.csv` — feature-level comparison metrics.

### Interpretation and Limitations

- Drift signals do not prove that model performance has degraded.
- PSI thresholds are common heuristics, not universal rules.
- Changes may reflect seasonality, promotions, or customer behavior.
- The analysis does not train, evaluate, or modify a prediction model.
- The source dataset is not modified.

## 13. Program 76: Data Quality Monitoring

### Objective

Monitor the quality of the processed retail sales dataset using automated validation checks. The program generates a text report and a CSV containing individual check results.

### Input Dataset

- File: `data/processed/sales_analysis.parquet`
- Total rows: 1,019,654
- Total columns: 10

### Quality Checks

- Required columns are present.
- Missing values in required columns are counted.
- Exact duplicate rows are detected.
- Numeric validity of quantity, unit price, and line value is checked.
- Quantity and unit price must be positive.
- Invoice dates must be valid.
- Line value is compared with quantity multiplied by unit price, allowing a tolerance of 0.01.

### Results

- Total checks: 15
- PASS: 14
- WARNING: 1
- FAIL: 0
- Overall status: WARNING
- Exact duplicate rows detected: 11,741

No missing values were found in the six required columns. The numeric checks, positive-value checks, invoice-date check, and line-value consistency check passed.

### Generated Outputs

- `data/processed/data_quality_report.txt` — readable quality summary and individual check details.
- `data/processed/data_quality_results.csv` — structured results with check name, status, affected row count, and details.

### Interpretation and Limitations

- Duplicate rows are flagged for investigation and are not automatically deleted.
- A warning does not automatically mean the dataset is unusable.
- The checks cover selected quality rules and do not guarantee that every business issue has been detected.
- The source dataset is read only and is not modified.

## 14. Program 77: Data Quality and Drift Summary

### Objective

Combine the existing data quality and data drift results into a single monitoring summary without rerunning the underlying analyses.

### Input Files

- `data/processed/data_quality_results.csv` — quality check results from Program 76.
- `data/processed/data_drift_results.csv` — drift metrics from Program 75.

### Data Quality Summary

- Total checks: 15
- Passed checks: 14
- Warning checks: 1
- Failed checks: 0
- Overall quality status: WARNING

The warning relates to exact duplicate rows identified by Program 76. Those rows require investigation and are not automatically deleted.

### Data Drift Summary

- Features analyzed: 3
- Features with PSI below 0.10: 3
- Features with PSI from 0.10 to below 0.25: 0
- Features with PSI at or above 0.25: 0
- Features with statistically significant KS tests: 3

The features analyzed are `quantity`, `unit_price`, and `line_value`. Their PSI values are below 0.10, while their KS tests are statistically significant at the 0.05 level.

### Generated Outputs

- `data/processed/quality_drift_summary.csv` — structured summary of quality and drift metrics.
- `data/processed/quality_drift_summary_report.txt` — readable monitoring report with feature-level results and interpretation notes.

### Interpretation and Limitations

- PSI bands are common heuristics, not universal rules.
- Statistical significance does not by itself prove meaningful business impact or model degradation.
- This program summarizes existing outputs; it does not recalculate the original quality or drift analyses.
- Source data and input reports are not modified.

## 15. Program 78: Monitoring Run History

### Objective

Record quality and data drift monitoring metrics in a historical CSV file so that monitoring results can be compared across successive runs.

### Input Files

- `data/processed/data_quality_results.csv` — quality check results from Program 76.
- `data/processed/data_drift_results.csv` — drift metrics from Program 75.

### Recorded Metrics

- UTC run timestamp
- Total quality checks and counts of PASS, WARNING, FAIL, and unknown statuses
- Overall quality status
- Number of drift features analyzed
- Counts of features in each PSI shift band
- Number of features with statistically significant KS tests

### Initial Run Results

- Monitoring runs recorded: 1
- Quality checks: 15
- PASS: 14
- WARNING: 1
- FAIL: 0
- Unknown statuses: 0
- Overall quality status: WARNING
- Drift features: 3
- Features with PSI below 0.10: 3
- Features with PSI from 0.10 to below 0.25: 0
- Features with PSI at or above 0.25: 0
- KS significant features: 3

### Generated Output

- `data/processed/monitoring_run_history.csv` — monitoring history maintained by this program.

Each successful run appends a new record while preserving existing history rows. The program validates the existing history schema before writing.

### Interpretation and Limitations

- The history records summaries of the existing quality and drift outputs; it does not rerun those analyses.
- Repeated runs using unchanged input reports create additional history records, not independent evidence of changing data quality.
- PSI bands are common heuristics, and statistically significant KS results do not by themselves prove model degradation.
- The original input reports are not modified.
