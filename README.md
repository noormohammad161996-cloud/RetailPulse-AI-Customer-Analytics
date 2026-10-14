# RetailPulse — AI-Powered Customer Analytics & Demand Forecasting

## Access the Streamlit Dashboard

Start the dashboard from your project root:

```bash
python -m streamlit run app/inventory_dashboard.py
```

Once the application is running, open either URL from your machine:

- **Local URL:** [http://localhost:8501/](http://localhost:8501/)
- **Network URL:** [http://172.21.93.221:8501/](http://172.21.93.221:8501/)

> **Note:** The dashboard must be running for these URLs to work. The network URL may change when your WSL environment restarts, and access from other devices depends on network and firewall configuration.

## Project Overview

RetailPulse is a retail analytics project that uses historical transaction data to analyze sales trends, segment customers, estimate customer churn risk, evaluate demand forecasting methods, and support inventory planning.

The project uses the UCI Online Retail II dataset.

## Objectives

- Explore and clean retail transaction data.
- Analyze monthly sales trends.
- Forecast monthly sales using baseline, seasonal-naive, and Prophet models.
- Segment customers using RFM analysis and K-Means clustering.
- Train and evaluate a customer churn classification model.
- Estimate product demand variability and preliminary reorder points.
- Display inventory analysis through a Streamlit dashboard.

## Technology Stack

- **Language:** Python
- **Data analysis:** pandas, NumPy
- **Visualization:** Matplotlib, Seaborn
- **Machine learning:** scikit-learn
- **Forecasting:** Prophet
- **Dashboard:** Streamlit
- **Data formats:** CSV, Parquet, Excel
- **Development environment:** VS Code and Ubuntu/WSL

## Dataset

**Source:** UCI Online Retail II

**Raw file:** `data/raw/online_retail_ii.xlsx`

The workbook contains two sheets covering retail transactions from December 2009 to December 2011. The project identifies and removes verified overlap between the sheets.

The sales-analysis dataset contains 1,019,654 rows after preliminary filtering.

## Work Completed

### 1. Data Preparation and Analysis

- Inspected dataset quality and missing values.
- Reviewed cancellation-style invoices and invalid quantities or prices.
- Combined the source sheets and removed verified overlapping records.
- Prepared a sales-analysis dataset.
- Generated monthly sales summaries.

### 2. Sales Forecasting

Compared three forecasting models on five test months, July–November 2011.

| Model | MAE | WAPE |
|---|---:|---:|
| Seasonal naive | 62,871.47 | 6.04% |
| Prophet | 255,233.78 | 24.53% |
| Mean baseline | 294,272.76 | 28.29% |

The seasonal-naive model performed best in this preliminary comparison. More validation is required before using it in production.

- Forecast chart: `data/processed/forecast_model_comparison.png`
- Evaluation report: `data/processed/forecast_evaluation_report.txt`

### 3. Customer Analytics

- Calculated customer recency, frequency, and monetary value (RFM).
- Created rule-based customer segments.
- Compared rule-based segments with K-Means clusters.
- Evaluated K-Means cluster counts using silhouette scores.

The highest silhouette score among the tested cluster counts was obtained with two clusters. The original target of six to eight segments has not yet been achieved by this K-Means evaluation.

### 4. Churn Prediction

- Created customer features and future-period churn labels.
- Trained a logistic regression classifier.
- Evaluated classification thresholds and chronological performance.
- Saved model artifacts and evaluation reports.

The chronological evaluation achieved a ROC-AUC of approximately 0.809. Limitations include customer overlap between cohorts and limited historical data.

### 5. Inventory Analysis

- Aggregated product demand by month.
- Added calendar months with no recorded sales.
- Estimated preliminary reorder points using assumed lead time and service level.
- Flagged products with limited history or high demand variability.
- Built a Streamlit dashboard for inventory exploration.

These estimates are based on simplified assumptions. The source dataset does not provide actual stock levels or supplier lead times, so the results should not be treated as confirmed inventory recommendations.

## Important Limitations

- Historical results do not guarantee future forecasting accuracy.
- The forecast comparison currently covers only five test months.
- The dataset ends in December 2011 and does not represent current retail conditions.
- Some transactions do not have customer IDs.
- No recorded sales in a month do not necessarily mean true demand was zero.
- Inventory estimates rely on simplified assumptions and are not production-ready.
- Project targets are goals, not achieved results unless supported by measured evaluation.

## Project Status

Data preparation, exploratory analysis, preliminary forecasting comparisons, customer segmentation, churn evaluation, inventory analysis, and the Streamlit inventory dashboard have been implemented.

Further work should focus on stronger validation, documentation, testing, and production readiness.

## Author

Developed as part of a data science internship project with Zidio Development.
