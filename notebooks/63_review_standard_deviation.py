# File: notebooks/63_review_standard_deviation.py
# Purpose: Learn standard deviation and compare manual calculations with NumPy.

import numpy as np

# Example: recorded monthly demand for one product.
# These are teaching values, not data from a real RetailPulse product.
demand = [10, 12, 14, 16, 18]

values = np.array(demand, dtype=float)

# Mean
mean_value = sum(demand) / len(demand)

# Population variance and standard deviation
population_variance = sum(
    (x - mean_value) ** 2 for x in demand
) / len(demand)

population_std = population_variance ** 0.5

# Sample variance and standard deviation
sample_variance = sum(
    (x - mean_value) ** 2 for x in demand
) / (len(demand) - 1)

sample_std = sample_variance ** 0.5

print("=" * 55)
print("STANDARD DEVIATION REVIEW")
print("=" * 55)

print("Monthly demand:", demand)
print(f"Mean: {mean_value:.2f}")

print("\nManual calculations:")
print(f"Population variance: {population_variance:.4f}")
print(f"Population standard deviation: {population_std:.4f}")
print(f"Sample variance: {sample_variance:.4f}")
print(f"Sample standard deviation: {sample_std:.4f}")

print("\nNumPy calculations:")
print(f"Population std (ddof=0): {np.std(values, ddof=0):.4f}")
print(f"Sample std (ddof=1): {np.std(values, ddof=1):.4f}")

print("\nInterpretation:")
print("- A larger standard deviation means more variation in demand.")
print("- Population std uses N in the variance denominator.")
print("- Sample std uses N - 1 in the variance denominator.")
print("\nStandard deviation review completed.")
