# File: notebooks/60_review_evaluation_metrics.py
# Purpose: Review the basic evaluation metrics used in machine learning.

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# Actual customer outcomes:
# 1 = churned, 0 = retained
y_true = [1, 1, 0, 0, 1, 0, 1, 0]

# Model-predicted outcomes
y_pred = [1, 0, 0, 0, 1, 1, 1, 0]

print("=" * 50)
print("CLASSIFICATION EVALUATION METRICS")
print("=" * 50)

print("Accuracy:", round(accuracy_score(y_true, y_pred), 4))
print("Precision:", round(precision_score(y_true, y_pred), 4))
print("Recall:", round(recall_score(y_true, y_pred), 4))
print("F1-score:", round(f1_score(y_true, y_pred), 4))

print("\nConfusion Matrix:")
print(confusion_matrix(y_true, y_pred))

print("\nDetailed Classification Report:")
print(classification_report(y_true, y_pred, zero_division=0))
