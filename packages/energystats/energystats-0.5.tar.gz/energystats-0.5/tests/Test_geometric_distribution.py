import numpy as np
from scipy.stats import geom
from estats.tests.Geometric_tests import (
    geometric_expected_distance,
    expected_pairwise_distance,
    geometric_energy_test,
    longest_run,
    test_iid_sequence
)

def test_geometric_expected_distance():
    print("\nTesting geometric_expected_distance:")
    # Standard case
    p = 0.5
    k = 3
    result = geometric_expected_distance(p, k)
    expected = k + (1 - p) / p - 2 * (1 - p) / p * (1 - (1 - p)**k)
    assert np.isclose(result, expected, atol=1e-6), f"Expected {expected}, got {result}"

    # Edge case: p = 1 (all trials are successes on the first attempt)
    p = 1.0
    k = 0
    result = geometric_expected_distance(p, k)
    assert result == 0, f"Expected 0, got {result}"

    # Edge case: small probability p -> 0
    p = 0.01
    k = 5
    result = geometric_expected_distance(p, k)
    assert result > 0, "Expected a positive distance for p approaching 0"

def test_expected_pairwise_distance():
    print("\nTesting expected_pairwise_distance:")
    # Standard case
    p = 0.5
    result = expected_pairwise_distance(p)
    q = 1 - p
    expected = 2 * q / (1 - q**2)
    assert np.isclose(result, expected, atol=1e-6), f"Expected {expected}, got {result}"

    # Edge case: p = 1
    p = 1.0
    result = expected_pairwise_distance(p)
    assert result == 0, f"Expected 0, got {result}"

    # Edge case: p close to 0
    p = 0.01
    result = expected_pairwise_distance(p)
    assert result > 0, "Expected a positive pairwise distance for p close to 0"

def test_geometric_energy_test():
    print("\nTesting geometric_energy_test:")
    # Standard case with matching geometric distribution
    p = 0.5
    sample = np.random.geometric(p, size=50)
    test_stat, p_value = geometric_energy_test(sample, p)
    assert p_value > 0.05, "Expected high p-value for correct geometric distribution"

    # Case with non-geometric data
    sample = np.random.poisson(5, size=50)  # Poisson distribution, not geometric
    test_stat, p_value = geometric_energy_test(sample, p)
    assert p_value < 0.05, "Expected low p-value for incorrect distribution"

    # Edge case: single element in sample
    sample = np.array([1])
    test_stat, p_value = geometric_energy_test(sample, p)
    assert np.isfinite(test_stat), "Expected finite test statistic for single element"
    assert 0 <= p_value <= 1, "Expected valid p-value in [0, 1] for single element"

    # Edge case: large sample size
    sample = np.random.geometric(p, size=1000)
    test_stat, p_value = geometric_energy_test(sample, p)
    assert np.isfinite(test_stat), "Expected finite test statistic for large sample"
    assert 0 <= p_value <= 1, "Expected valid p-value in [0, 1] for large sample"

def test_longest_run():
    print("\nTesting longest_run:")
    # Standard case
    sequence = [1, 1, 0, 0, 0, 1, 1, 1]
    result = longest_run(sequence)
    assert result == 3, f"Expected longest run of 3, got {result}"

    # Edge case: all elements the same (longest run equals length)
    sequence = [1] * 10
    result = longest_run(sequence)
    assert result == 10, f"Expected longest run of 10, got {result}"

    # Edge case: alternating sequence
    sequence = [1, 0] * 5
    result = longest_run(sequence)
    assert result == 1, f"Expected longest run of 1, got {result}"

    # Edge case: empty sequence
    sequence = []
    result = longest_run(sequence)
    assert result == 0, f"Expected longest run of 0, got {result}"

def test_test_iid_sequence():
    print("\nTesting test_iid_sequence:")
    # Standard case: IID Bernoulli sequence
    p = 0.5
    sequence = np.random.binomial(1, p, size=100)
    observed_run, expected_run, iid_p_value = test_iid_sequence(sequence, p)
    assert observed_run > 0, "Expected observed run length greater than 0"
    assert np.isclose(expected_run, np.log2(len(sequence)), atol=1e-6), f"Expected run length around {np.log2(len(sequence))}, got {expected_run}"
    assert 0 <= iid_p_value <= 1, "Expected valid p-value in [0, 1]"

    # Case: non-random sequence (all identical values)
    sequence = [1] * 50
    observed_run, expected_run, iid_p_value = test_iid_sequence(sequence, p)
    assert observed_run == 50, f"Expected longest run of 50, got {observed_run}"
    assert iid_p_value < 0.05, "Expected low p-value for non-random sequence"

    # Edge case: very short sequence
    sequence = [1, 0]
    observed_run, expected_run, iid_p_value = test_iid_sequence(sequence, p)
    assert observed_run == 1, f"Expected longest run of 1, got {observed_run}"
    assert 0 <= iid_p_value <= 1, "Expected valid p-value in [0, 1] for short sequence"

    # Edge case: empty sequence
    sequence = []
    try:
        observed_run, expected_run, iid_p_value = test_iid_sequence(sequence, p)
        assert False, "Expected an exception for empty sequence"
    except ValueError:
        pass

if __name__ == "__main__":
    test_geometric_expected_distance()
    test_expected_pairwise_distance()
    test_geometric_energy_test()
    test_longest_run()
    test_test_iid_sequence()
