from pathlib import Path

import joblib
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

train_file = DATA_DIR / "temporal_churn_validation.csv"
test_file = DATA_DIR / "sales_analysis.parquet"

model_file = MODEL_DIR / "chronological_churn_model.joblib"
metrics_file = DATA_DIR / "chronological_churn_metrics.txt"

# Load the earlier training cohort
train_df = pd.read_csv(train_file)

# Build the later cohort using the sales data
sales = pd.read_parquet(test_file)
sales["invoice_date"] = pd.to_datetime(sales["invoice_date"], errors="coerce")
sales["customer_id"] = pd.to_numeric(sales["customer_id"], errors="coerce")
sales = sales.dropna(subset=["customer_id", "invoice_date"]).copy()

# Later cohort feature window: through May 31, 2011
feature_cutoff = pd.Timestamp("2011-05-31 23:59:59")
observation_start = pd.Timestamp("2011-06-01 00:00:00")
observation_end = pd.Timestamp("2011-08-31 23:59:59")

feature_data = sales[sales["invoice_date"] <= feature_cutoff].copy()
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
    (feature_cutoff.normalize() + pd.Timedelta(days=1))
    - test_df["last_purchase"].dt.normalize()
).dt.days

test_df = test_df.drop(columns=["last_purchase"])

future_customer_ids = set(future_data["customer_id"].unique())
test_df["churned"] = (
    ~test_df["customer_id"].isin(future_customer_ids)
).astype(int)

features = ["recency_days", "frequency", "monetary"]

X_train = train_df[features]
y_train = train_df["churned"]

X_test = test_df[features]
y_test = test_df["churned"]

# Train only on the earlier cohort
model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )),
])

model.fit(X_train, y_train)

# Evaluate on the later cohort
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, predictions)
roc_auc = roc_auc_score(y_test, probabilities)
matrix = confusion_matrix(y_test, predictions)
report = classification_report(
    y_test,
    predictions,
    target_names=["Retained (0)", "Churned (1)"],
    zero_division=0,
)

MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(model, model_file)

report_text = "\n".join([
    "RETAILPULSE - CHRONOLOGICAL CHURN EVALUATION",
    "=" * 47,
    f"Training customers: {len(train_df):,}",
    f"Later test customers: {len(test_df):,}",
    f"Later feature cutoff: {feature_cutoff.date()}",
    f"Observation window: {observation_start.date()} to {observation_end.date()}",
    f"Accuracy: {accuracy:.4f}",
    f"ROC-AUC: {roc_auc:.4f}",
    "",
    "Confusion matrix (actual rows, predicted columns):",
    str(matrix),
    "",
    "Classification report:",
    report,
    "",
    "Limitation: this is a historical cohort evaluation. The same customer",
    "may appear in both cohorts, and the dataset covers a limited time span.",
])

metrics_file.write_text(report_text, encoding="utf-8")

print(report_text)
print(f"\nModel saved to: {model_file}")
print(f"Metrics saved to: {metrics_file}")
