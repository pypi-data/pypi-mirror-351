import unittest
import numpy as np
from estats.tests.disco_decomposition import disco_decomposition

class TestDiscoDecomposition(unittest.TestCase):

    def test_standard_case(self):
        # Standard case with two distinct groups
        group1 = np.random.normal(0, 1, (20, 2))
        group2 = np.random.normal(5, 1, (20, 2))
        result = disco_decomposition([group1, group2], alpha=1, R=500)
        print("Standard Case Result:", result)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_identical_groups(self):
        # Two identical groups should result in a high p-value
        group1 = np.random.normal(0, 1, (20, 2))
        group2 = group1.copy()
        result = disco_decomposition([group1, group2], alpha=1, R=500)
        print("Identical Groups Result:", result)
        self.assertGreater(result["p-value"], 0.05, "Expected high p-value for identical groups")

    def test_single_point_groups(self):
        # Groups with a single point each should have zero within-sample dispersion
        group1 = np.array([[0, 0]])
        group2 = np.array([[1, 1]])
        result = disco_decomposition([group1, group2], alpha=1, R=500)
        print("Single Point Groups Result:", result)
        self.assertAlmostEqual(result["W_alpha"], 0, "Expected W_alpha to be 0 for single-point groups")
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_varied_group_sizes(self):
        # Different group sizes
        group1 = np.random.normal(0, 1, (10, 2))
        group2 = np.random.normal(5, 1, (30, 2))
        result = disco_decomposition([group1, group2], alpha=1, R=500)
        print("Varied Group Sizes Result:", result)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_large_sample(self):
        # Large dataset with permutation test
        group1 = np.random.normal(0, 1, (100, 2))
        group2 = np.random.normal(5, 1, (100, 2))
        result = disco_decomposition([group1, group2], alpha=1, R=100)
        print("Large Sample Result:", result)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_alpha_zero(self):
        # alpha = 0 should yield identical T_alpha and W_alpha due to uniform weighting
        group1 = np.random.normal(0, 1, (20, 2))
        group2 = np.random.normal(5, 1, (20, 2))
        result = disco_decomposition([group1, group2], alpha=0, R=500)
        print("Alpha Zero Result:", result)
        self.assertAlmostEqual(result["T_alpha"], result["W_alpha"], "T_alpha should equal W_alpha for alpha = 0")
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")
        
    def test_three_groups(self):
        # Test with three groups with distinct means
        group1 = np.random.normal(0, 1, (15, 2))
        group2 = np.random.normal(5, 1, (15, 2))
        group3 = np.random.normal(10, 1, (15, 2))
        result = disco_decomposition([group1, group2, group3], alpha=1, R=500)
        print("Three Groups Result:", result)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_high_dimensional_data(self):
        # High-dimensional data (e.g., 50D) to test scalability
        group1 = np.random.normal(0, 1, (20, 50))
        group2 = np.random.normal(5, 1, (20, 50))
        result = disco_decomposition([group1, group2], alpha=1, R=100)
        print("High Dimensional Data Result:", result)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_alpha_variants(self):
        # Test different alpha values including fractional and negative
        group1 = np.random.normal(0, 1, (20, 2))
        group2 = np.random.normal(5, 1, (20, 2))
        for alpha in [0.5, 1, 2, -1]:
            result = disco_decomposition([group1, group2], alpha=alpha, R=100)
            print(f"Alpha {alpha} Result:", result)
            self.assertTrue(0 <= result["p-value"] <= 1, f"p-value should be between 0 and 1 for alpha={alpha}")

    def test_no_variance(self):
        # Groups with identical points to test zero dispersion
        group1 = np.ones((10, 2))
        group2 = np.ones((10, 2))
        result = disco_decomposition([group1, group2], alpha=1, R=100)
        print("No Variance Result:", result)
        self.assertAlmostEqual(result["T_alpha"], 0, "Expected T_alpha to be 0 for identical points")
        self.assertAlmostEqual(result["W_alpha"], 0, "Expected W_alpha to be 0 for identical points")
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")


if __name__ == "__main__":
    unittest.main()
