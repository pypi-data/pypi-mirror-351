import unittest
from estats.tests.Bernoulli_test import energy_goodness_of_fit_bernoulli
import numpy as np 

class TestBernoulliGoodnessOfFit(unittest.TestCase):

    def test_standard_case(self):
        sample = np.random.binomial(1, 0.5, 100)
        result = energy_goodness_of_fit_bernoulli(sample=sample, R=500)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_all_ones(self):
        sample = np.ones(100)
        result = energy_goodness_of_fit_bernoulli(sample=sample, R=500)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_all_zeros(self):
        sample = np.zeros(100)
        result = energy_goodness_of_fit_bernoulli(sample=sample, R=500)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_empty_sample(self):
        with self.assertRaises(ValueError):
            energy_goodness_of_fit_bernoulli(sample=[])

    def test_large_sample_size(self):
        sample = np.random.binomial(1, 0.5, 10000)
        result = energy_goodness_of_fit_bernoulli(sample=sample, R=100)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_precomputed_n_h_p(self):
        n = 100
        h = 50
        p_bar = 0.5
        result = energy_goodness_of_fit_bernoulli(n=n, h=h, p_bar=p_bar, R=500)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    # New tests for edge cases
    def test_extreme_p_high(self):
        sample = np.random.binomial(1, 0.99, 100)  # p close to 1
        result = energy_goodness_of_fit_bernoulli(sample=sample, R=500)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_extreme_p_low(self):
        sample = np.random.binomial(1, 0.01, 100)  # p close to 0
        result = energy_goodness_of_fit_bernoulli(sample=sample, R=500)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_minimal_sample_size_one(self):
        sample = np.array([1])
        result = energy_goodness_of_fit_bernoulli(sample=sample, R=100)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_minimal_sample_size_zero(self):
        sample = np.array([0])
        result = energy_goodness_of_fit_bernoulli(sample=sample, R=100)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_p_bar_edge_case_0(self):
        n = 100
        h = 0  # All zeroes, so p_bar should be 0
        p_bar = 0.0
        result = energy_goodness_of_fit_bernoulli(n=n, h=h, p_bar=p_bar, R=500)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

    def test_p_bar_edge_case_1(self):
        n = 100
        h = 100  # All ones, so p_bar should be 1
        p_bar = 1.0
        result = energy_goodness_of_fit_bernoulli(n=n, h=h, p_bar=p_bar, R=500)
        self.assertTrue(0 <= result["p-value"] <= 1, "p-value should be between 0 and 1")

if __name__ == "__main__":
    unittest.main()
