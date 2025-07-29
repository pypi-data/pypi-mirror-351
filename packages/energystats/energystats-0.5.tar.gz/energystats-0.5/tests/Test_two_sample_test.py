import numpy as np
from estats.tests.Two_sample_test import two_sample_energy_test

def test_two_sample_test():
    # Generate two similar samples
    x = np.random.normal(0, 1, 100)
    y = np.random.normal(0, 1, 100)

    # Run the test (expecting a high p-value since distributions are similar)
    observed_stat, p_value = two_sample_energy_test(x, y, R=500)
    print("Test Statistic:", observed_stat)
    print("p-value:", p_value)
    assert p_value > 0.05, "Failed: High p-value expected for similar distributions."

    # Generate two different samples
    x = np.random.normal(0, 1, 100)
    y = np.random.normal(1, 1, 100)

    # Run the test (expecting a low p-value since distributions differ)
    observed_stat, p_value = two_sample_energy_test(x, y, R=500)
    print("Test Statistic:", observed_stat)
    print("p-value:", p_value)
    assert p_value < 0.05, "Failed: Low p-value expected for different distributions."

if __name__ == "__main__":
    test_two_sample_test()
