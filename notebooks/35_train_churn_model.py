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

input_file = DATA_DIR / "customer_churn_dataset.csv"
metrics_file = DATA_DIR / "churn_model_metrics.txt"
model_file = MODEL_DIR / "churn_logistic_regression.joblib"

# Load the validated dataset
df = pd.read_csv(input_file)

features = ["recency_days", "frequency", "monetary"]
X = df[features]
y = df["churned"]

# Keep the class proportions similar in train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

# Scaling and model training happen inside the pipeline
model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )),
])

model.fit(X_train, y_train)

# Evaluate on unseen test rows
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

# Save the model
MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(model, model_file)

# Save metrics
results = [
    "RETAILPULSE - LOGISTIC REGRESSION CHURN MODEL",
    "=" * 48,
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
    "Important limitation:",
    "This is an initial historical model using a single cutoff and",
    "observation window. Its performance must be validated on later",
    "time periods before claiming production readiness.",
]

metrics_file.write_text("\n".join(results), encoding="utf-8")

print("\n".join(results))
print(f"\nModel saved to: {model_file}")
print(f"Metrics saved to: {metrics_file}")
