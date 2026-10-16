# File: notebooks/61_review_regression_metrics.py
# Purpose: Calculate regression metrics using actual and predicted values.

import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

# Example sales values (not actual RetailPulse results)
actual_sales = np.array([100, 150, 200, 250, 300])
predicted_sales = np.array([110, 140, 190, 260, 290])

mae = mean_absolute_error(actual_sales, predicted_sales)
mse = mean_squared_error(actual_sales, predicted_sales)
rmse = np.sqrt(mse)
r2 = r2_score(actual_sales, predicted_sales)

print("=" * 50)
print("REGRESSION EVALUATION METRICS")
print("=" * 50)

print("Actual sales:   ", actual_sales)
print("Predicted sales:", predicted_sales)

print("\nEvaluation results:")
print(f"MAE:  {mae:.2f}")
print(f"MSE:  {mse:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R-squared: {r2:.4f}")

print("\nInterpretation:")
print("- MAE: Average absolute prediction error.")
print("- MSE: Average squared prediction error.")
print("- RMSE: Error in the same units as sales.")
print("- R-squared: Fit relative to predicting the mean.")
print("\nRegression metrics calculation completed.")
