from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.pipeline import Pipeline

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

data_file = DATA_DIR / "temporal_churn_validation.csv"
model_file = MODEL_DIR / "chronological_churn_model.joblib"
output_file = DATA_DIR / "chronological_churn_confusion_matrix.png"

# Load the later cohort's feature data and labels.
# These values must match the data used for the chronological evaluation.
sales_file = DATA_DIR / "sales_analysis.parquet"
sales = pd.read_parquet(sales_file)

sales["invoice_date"] = pd.to_datetime(sales["invoice_date"], errors="coerce")
sales["customer_id"] = pd.to_numeric(sales["customer_id"], errors="coerce")
sales = sales.dropna(subset=["customer_id", "invoice_date"]).copy()

cutoff = pd.Timestamp("2011-05-31 23:59:59")
observation_start = pd.Timestamp("2011-06-01 00:00:00")
observation_end = pd.Timestamp("2011-08-31 23:59:59")

feature_data = sales[sales["invoice_date"] <= cutoff].copy()
future_data = sales[
    (sales["invoice_date"] >= observation_start)
    & (sales["invoice_date"] <= observation_end)
].copy()

feature_data["line_value"] = feature_data["quantity"] * feature_data["unit_price"]

test_df = (
    feature_data.groupby("customer_id")
    .agg(
        last_purchase=("invoice_date", "max"),
        frequency=("invoice_id", "nunique"),
        monetary=("line_value", "sum"),
    )
    .reset_index()
)

test_df["recency_days"] = (
    (cutoff.normalize() + pd.Timedelta(days=1))
    - test_df["last_purchase"].dt.normalize()
).dt.days

test_df = test_df.drop(columns=["last_purchase"])

future_customer_ids = set(future_data["customer_id"].unique())
test_df["churned"] = (
    ~test_df["customer_id"].isin(future_customer_ids)
).astype(int)

features = ["recency_days", "frequency", "monetary"]
X_test = test_df[features]
y_test = test_df["churned"]

model = joblib.load(model_file)
predictions = model.predict(X_test)

matrix = confusion_matrix(y_test, predictions)

fig, ax = plt.subplots(figsize=(7, 6))
display = ConfusionMatrixDisplay(
    confusion_matrix=matrix,
    display_labels=["Retained", "Churned"],
)
display.plot(ax=ax, values_format=",", colorbar=False)

ax.set_title("RetailPulse - Chronological Churn Evaluation")
plt.tight_layout()
plt.savefig(output_file, dpi=200, bbox_inches="tight")
plt.close()

print("CHRONOLOGICAL CHURN CONFUSION MATRIX CREATED")
print("============================================")
print(f"Test customers: {len(test_df):,}")
print(f"Chart saved to: {output_file}")
print("\nConfusion matrix:")
print(matrix)
