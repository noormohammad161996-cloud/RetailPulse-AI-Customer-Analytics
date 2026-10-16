# RetailPulse — AI-Powered Customer Analytics & Demand Forecasting

**RetailPulse** is a retail analytics project developed as part of a data science internship with Zidio Development. It uses historical retail transaction data to explore sales trends, customer behavior, churn risk, demand forecasting, and inventory planning.

## Dashboard Preview

The project includes an interactive Streamlit dashboard for exploring historical product demand and preliminary inventory planning estimates.

![RetailPulse Inventory Analytics Dashboard](docs/Images/inventory-dashboard.png)

*Dashboard preview: inventory overview, category filters, product search, demand analysis, and planning estimates.*

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Dataset](#dataset)
- [Sales Forecasting](#sales-forecasting)
- [Customer Analytics](#customer-analytics)
- [Churn Prediction](#churn-prediction)
- [Inventory Analytics Dashboard](#inventory-analytics-dashboard)
- [Installation and Setup](#installation-and-setup)
- [Project Structure](#project-structure)
- [Limitations](#limitations)
- [Project Status](#project-status)
- [Author](#author)

## Project Overview

RetailPulse explores how data science can support retail decision-making through:

- Exploratory data analysis and data quality checks.
- Monthly sales analysis and forecasting.
- Customer segmentation using RFM analysis and K-Means.
- Customer churn classification and evaluation.
- Product demand variability analysis.
- Preliminary inventory planning estimates.
- Interactive dashboard development with Streamlit.

## Key Features

- Data preparation and transaction quality analysis.
- Comparison of baseline, seasonal-naive, and Prophet forecasting models.
- Customer segmentation and churn evaluation.
- Product-level demand and variability metrics.
- Interactive inventory category filters and product search.
- Product detail inspection and filtered CSV export.
- Reproducible Python scripts and project documentation.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Data analysis | pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Machine learning | scikit-learn |
| Forecasting | Prophet |
| Dashboard | Streamlit |
| Data formats | CSV, Parquet, Excel |
| Development | VS Code, Ubuntu/WSL |
| Version control | Git, GitHub |

## Dataset

**Source:** UCI Online Retail II dataset.

**Raw workbook:** `data/raw/online_retail_ii.xlsx`

The source workbook contains two sheets of historical retail transactions covering December 2009 through December 2011, with overlapping records between the sheets.

The project identifies and removes verified overlap before preparing the analysis datasets.

The preliminary sales-analysis dataset contains **1,019,654 rows** after filtering transaction records.

The data is historical and does not represent current retail market conditions.

## Sales Forecasting

Three forecasting approaches were compared on five test months, July–November 2011.

| Model | MAE | WAPE |
|---|---:|---:|
| Seasonal naive | 62,871.47 | 6.04% |
| Prophet | 255,233.78 | 24.53% |
| Mean baseline | 294,272.76 | 28.29% |

**Finding:** The seasonal-naive model performed best among these three models in the current five-month comparison.

These results are preliminary. A broader evaluation across multiple forecast horizons and time periods is required before drawing production-level conclusions.

**Related outputs:**

- Forecast comparison chart: `data/processed/forecast_model_comparison.png`
- Forecast evaluation report: `data/processed/forecast_evaluation_report.txt`
- Detailed metrics: `data/processed/forecast_detailed_metrics.csv`

## Customer Analytics

The customer analytics workflow includes:

- Recency, Frequency, and Monetary (RFM) feature calculation.
- Rule-based customer segmentation.
- K-Means clustering and cluster visualization.
- Comparison of segmentation approaches.
- Silhouette-score evaluation for tested cluster counts.

The highest silhouette score among the tested K-Means cluster counts was approximately **0.4188 for two clusters**. The original goal of six to eight segments has not yet been achieved by this evaluation.

## Churn Prediction

The churn workflow includes customer feature preparation, future-period churn labels, logistic regression, threshold analysis, and chronological evaluation.

A chronological evaluation achieved a ROC-AUC of approximately **0.809**.

This is an initial result, not a production guarantee. Evaluation limitations include customer overlap between cohorts and limited historical observations.

## Inventory Analytics Dashboard

The Streamlit dashboard provides an interactive view of historical product demand and preliminary inventory planning estimates.

### Dashboard features

- **Inventory overview:** Products displayed, total recorded units, high-variability products, and products with limited sales history.
- **Inventory review filters:** Filter products by inventory review category.
- **Demand risk-review filters:** Filter products by demand risk-review category.
- **Product search:** Search using a product ID or product name.
- **Product inspection:** Review average monthly recorded demand, demand coefficient of variation, months with recorded sales, estimated lead-time demand, approximate safety stock, and preliminary reorder point.
- **Charts and tables:** Explore product category distributions and product-level planning metrics.
- **CSV export:** Download the currently filtered inventory analysis data.
- **Reset all filters:** Restore the default filter selections and clear the search.

### Current inventory analysis

The current dashboard displays **4,916 products** across 24 monthly periods from December 2009 through November 2011. December 2011 is excluded from this monthly analysis because the source month is incomplete.

### Run the dashboard

From the project root, activate your virtual environment and run:

```bash
python -m streamlit run app/inventory_dashboard.py
```

Open the local URL printed in your terminal, normally:

`http://localhost:8501`

The dashboard must be running for the local URL to work.

## Installation and Setup

### Prerequisites

- Python installed.
- Git installed.
- VS Code or another Python editor.
- Access to the project files and prepared datasets.

### 1. Clone the repository

```bash
git clone https://github.com/noormohammad161996-cloud/RetailPulse-AI-Customer-Analytics.git
cd RetailPulse-AI-Customer-Analytics
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Ubuntu/WSL:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the dashboard

```bash
python -m streamlit run app/inventory_dashboard.py
```

**Note:** The dashboard expects its prepared input data to exist at the paths configured in the application. Ensure the required processed datasets are available before launching it.

## Project Structure

```text
RetailPulse-AI-Customer-Analytics/
├── app/
│   └── inventory_dashboard.py
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── images/
│   │   └── inventory-dashboard.png
│   └── project_notes.md
├── models/
├── notebooks/
├── requirements.txt
└── README.md
```

This is a representative structure. Some generated data and model artifacts may be excluded from GitHub by `.gitignore`.

## Limitations

- The forecast comparison currently covers only five test months.
- Historical forecast performance does not guarantee future accuracy.
- The source data ends in December 2011 and is not representative of current retail conditions.
- Some transactions have missing customer IDs.
- No recorded sales in a month do not necessarily indicate zero true demand.
- Actual stock-on-hand levels, open purchase orders, supplier lead times, and confirmed stockout records are unavailable.
- Inventory lead-time demand, safety stock, and reorder points use simplified assumptions.
- Inventory risk categories are preliminary review flags, not confirmed stockout probabilities.
- Project targets are goals, not achieved results unless supported by measured evaluation.

## Project Status

Implemented components include data preparation, exploratory analysis, preliminary sales forecasting comparisons, RFM customer segmentation, churn model evaluation, inventory demand analysis, and an interactive Streamlit dashboard.

The dashboard's category filters, product search, product inspection, reset behavior, and CSV download have passed manual functional checks.

Further work should focus on stronger validation, automated testing, documentation, and improvements to model reliability and inventory assumptions.

## Author

Developed as part of a data science internship project with **Zidio Development**.

**GitHub:** [RetailPulse — AI Customer Analytics](https://github.com/noormohammad161996-cloud/RetailPulse-AI-Customer-Analytics)
