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
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

input_file = DATA_DIR / "temporal_churn_validation.csv"
model_file = MODEL_DIR / "temporal_churn_logistic_regression.joblib"
metrics_file = DATA_DIR / "temporal_churn_model_metrics.txt"

df = pd.read_csv(input_file)

features = ["recency_days", "frequency", "monetary"]
X = df[features]
y = df["churned"]

# Split the earlier cohort for a baseline evaluation.
# This is a random split within the earlier cohort, not a later-period test.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )),
])

model.fit(X_train, y_train)

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
    "RETAILPULSE - EARLIER COHORT CHURN MODEL",
    "=" * 42,
    f"Customers: {len(df):,}",
    f"Training rows: {len(X_train):,}",
    f"Test rows: {len(X_test):,}",
    f"Accuracy: {accuracy:.4f}",
    f"ROC-AUC: {roc_auc:.4f}",
    "",
    "Confusion matrix (actual rows, predicted columns):",
    str(matrix),
    "",
    "Classification report:",
    report,
    "",
    "Evaluation note:",
    "This is a random holdout within the earlier historical cohort.",
    "It is not a forward-in-time test of the later 2011 period.",
])

metrics_file.write_text(report_text, encoding="utf-8")

print(report_text)
print(f"\nModel saved to: {model_file}")
print(f"Metrics saved to: {metrics_file}")
