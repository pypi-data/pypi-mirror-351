import numpy as np
from estats.tests.poisson_tests import poisson_e_test, poisson_m_test

def test_poisson_tests():
    # Case 1: Standard case with correct Poisson distribution and moderate lambda
    sample = np.random.poisson(3, size=50)
    lambda_val = 3
    print("\n--- Standard Case ---")
    e_stat, e_p_value = poisson_e_test(sample, lambda_val, R=500)
    print("Poisson E-Test Statistic:", e_stat)
    print("Poisson E-Test p-value:", e_p_value)
    m_stat = poisson_m_test(sample, lambda_val)
    print("Poisson M-Test Statistic:", m_stat)
    assert e_p_value > 0.05, "Expected high p-value for a correct Poisson sample."
    assert m_stat > 0, "M-test statistic should be positive."

    # Case 2: Small sample size
    sample = np.random.poisson(3, size=5)
    lambda_val = 3
    print("\n--- Small Sample Size ---")
    e_stat, e_p_value = poisson_e_test(sample, lambda_val, R=500)
    print("Poisson E-Test Statistic:", e_stat)
    print("Poisson E-Test p-value:", e_p_value)
    m_stat = poisson_m_test(sample, lambda_val)
    print("Poisson M-Test Statistic:", m_stat)
    # For very small samples, results may vary due to high variability

    # Case 3: Large sample size
    sample = np.random.poisson(3, size=1000)
    lambda_val = 3
    print("\n--- Large Sample Size ---")
    e_stat, e_p_value = poisson_e_test(sample, lambda_val, R=500)
    print("Poisson E-Test Statistic:", e_stat)
    print("Poisson E-Test p-value:", e_p_value)
    m_stat = poisson_m_test(sample, lambda_val)
    print("Poisson M-Test Statistic:", m_stat)
    assert e_p_value > 0.05, "Expected high p-value for a large correct Poisson sample."
    assert m_stat > 0, "M-test statistic should be positive for a large sample."

    # Case 4: Test with a different hypothesized lambda
    lambda_val = 5  # Different from sample mean
    print("\n--- Different Hypothesized Lambda ---")
    e_stat, e_p_value = poisson_e_test(sample, lambda_val, R=500)
    print("Poisson E-Test Statistic:", e_stat)
    print("Poisson E-Test p-value:", e_p_value)
    m_stat = poisson_m_test(sample, lambda_val)
    print("Poisson M-Test Statistic:", m_stat)
    assert e_p_value < 0.05, "Expected low p-value for a mismatched Poisson mean."

    # Case 5: Non-Poisson data (Uniform distribution) to check robustness
    sample = np.random.randint(0, 10, size=50)
    lambda_val = 3
    print("\n--- Non-Poisson Data (Uniform Distribution) ---")
    e_stat, e_p_value = poisson_e_test(sample, lambda_val, R=500)
    print("Poisson E-Test Statistic:", e_stat)
    print("Poisson E-Test p-value:", e_p_value)
    m_stat = poisson_m_test(sample, lambda_val)
    print("Poisson M-Test Statistic:", m_stat)
    assert e_p_value < 0.05, "Expected low p-value for non-Poisson data."

    # Case 6: Edge case with lambda=0 (rare events)
    sample = np.random.poisson(0, size=50)
    lambda_val = 0
    print("\n--- Edge Case with Lambda=0 ---")
    e_stat, e_p_value = poisson_e_test(sample, lambda_val, R=500)
    print("Poisson E-Test Statistic:", e_stat)
    print("Poisson E-Test p-value:", e_p_value)
    m_stat = poisson_m_test(sample, lambda_val)
    print("Poisson M-Test Statistic:", m_stat)
    assert e_p_value > 0.05, "Expected high p-value for lambda=0."

if __name__ == "__main__":
    test_poisson_tests()
