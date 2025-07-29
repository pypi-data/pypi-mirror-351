import numpy as np
from estats.tests.distribution_tests import m_normality_statistic

def test_mvnorm_statistic():
    test_cases = [
        # Normal distributions with various shapes and sizes
        {"name": "Normal data (100x5)", "data": np.random.normal(0, 1, size=(100, 5))},
        {"name": "Normal data (500x10)", "data": np.random.normal(0, 1, size=(500, 10))},
        {"name": "Normal data (50x50)", "data": np.random.normal(0, 1, size=(50, 50))},
        {"name": "Large normal data (10000x20)", "data": np.random.normal(0, 1, size=(10000, 20))},
        
        # Non-normal distributions (uniform, binomial, etc.)
        {"name": "Uniform data (100x5)", "data": np.random.uniform(-5, 5, size=(100, 5))},
        {"name": "Uniform data (500x10)", "data": np.random.uniform(-10, 10, size=(500, 10))},
        {"name": "Large uniform data (10000x20)", "data": np.random.uniform(-20, 20, size=(10000, 20))},
        
        # Edge cases with very small or very high dimensional data
        {"name": "Edge Case: Single observation (1x5)", "data": np.random.normal(0, 1, size=(1, 5))},
        {"name": "Edge Case: Single dimension (100x1)", "data": np.random.normal(0, 1, size=(100, 1))},
        {"name": "Edge Case: Small dataset (2x2)", "data": np.random.normal(0, 1, size=(2, 2))},
        
        # Multimodal distributions (Gaussian mixture, bimodal)
        {"name": "Bimodal data (100x5)", "data": np.concatenate([np.random.normal(-5, 1, (50, 5)), np.random.normal(5, 1, (50, 5))])},
        {"name": "Gaussian Mixture (100x5)", "data": np.vstack([np.random.normal(0, 1, (50, 5)), np.random.normal(5, 1, (50, 5))])},
        
        # Skewed data
        {"name": "Skewed data (100x5)", "data": np.random.chisquare(2, size=(100, 5))},
        
        # Large dataset with varied shapes
        {"name": "Large skewed data (10000x20)", "data": np.random.chisquare(2, size=(10000, 20))},
        
        # Identical data (all values the same)
        {"name": "Identical data (100x5)", "data": np.full((100, 5), 7)},
        
        # High-dimensional data
        {"name": "High-dimensional normal data (100x50)", "data": np.random.normal(0, 1, size=(100, 50))},
        {"name": "High-dimensional uniform data (100x50)", "data": np.random.uniform(-5, 5, size=(100, 50))},
        
        # Very high-dimensional data (large number of dimensions)
        {"name": "Very high-dimensional data (100x100)", "data": np.random.normal(0, 1, size=(100, 100))}
    ]

    for case in test_cases:
        try:
            statistic = m_normality_statistic(case["data"])
            print(f"Statistic for {case['name']}: {statistic}")
            print('*'*100)
        except Exception as e:
            print(f"Failed to compute statistic for {case['name']}: {e}")
            print('*'*100)


# Run the updated test cases
test_mvnorm_statistic()
