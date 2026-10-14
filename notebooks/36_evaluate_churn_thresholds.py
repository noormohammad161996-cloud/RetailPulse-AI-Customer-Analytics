from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

data_file = DATA_DIR / "customer_churn_dataset.csv"
model_file = MODEL_DIR / "churn_logistic_regression.joblib"
output_file = DATA_DIR / "churn_threshold_comparison.csv"

# Load the same dataset and reproduce the original test split
df = pd.read_csv(data_file)

features = ["recency_days", "frequency", "monetary"]
X = df[features]
y = df["churned"]

_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

# Load the trained pipeline
model = joblib.load(model_file)

# Get predicted probabilities for churn
probabilities = model.predict_proba(X_test)[:, 1]

results = []

for threshold in [0.30, 0.40, 0.50, 0.60, 0.70]:
    predictions = (probabilities >= threshold).astype(int)

    results.append({
        "threshold": threshold,
        "precision": precision_score(
            y_test, predictions, zero_division=0
        ),
        "recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "f1_score": f1_score(
            y_test, predictions, zero_division=0
        ),
        "customers_flagged": int(predictions.sum()),
    })

results_df = pd.DataFrame(results)
results_df.to_csv(output_file, index=False)

print("RETAILPULSE - CHURN THRESHOLD EVALUATION")
print("=======================================")
print(f"ROC-AUC: {roc_auc_score(y_test, probabilities):.4f}")
print("\nThreshold comparison:")
print(results_df.round(4).to_string(index=False))
print(f"\nResults saved to: {output_file}")

print(
    "\nNote: This is an exploratory comparison on the existing test set. "
    "Choose the final threshold using business costs and separate validation."
)
