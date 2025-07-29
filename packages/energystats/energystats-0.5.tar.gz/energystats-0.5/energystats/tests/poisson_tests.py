import numpy as np
from scipy.special import gammaincc, i0, i1

def poisson_expected_distance(lambda_val):
    """
    Calculate the expected distance E|X - X'| for a Poisson distributed X with mean lambda.
    Uses equation E|X - X'| = 2*lambda*exp(-2*lambda) * (I0(2*lambda) + I1(2*lambda)),
    where I0 and I1 are modified Bessel functions of the first kind.
    Parameters:
        lambda_val (float): Mean of the Poisson distribution.
    Returns:
        float: The expected distance E|X - X'|.
    """
    return 2 * lambda_val * np.exp(-2 * lambda_val) * (i0(2 * lambda_val) + i1(2 * lambda_val))

def energy_test_statistic(sample, lambda_val):
    """
    Compute the energy test statistic for a sample from a Poisson distribution.
    Parameters:
        sample (np.ndarray): Array of observed counts.
        lambda_val (float): Hypothesized mean of the Poisson distribution.
    Returns:
        float: The energy test statistic value.
    """
    n = len(sample)
    observed_distance_sum = np.mean([np.abs(x - lambda_val) for x in sample])
    expected_distance = poisson_expected_distance(lambda_val)
    intra_sample_distance = np.mean([np.abs(xi - xj) for xi in sample for xj in sample]) / n
    
    return n * (2 * observed_distance_sum - expected_distance - intra_sample_distance)

def m_test_statistic(sample, lambda_val):
    """
    Compute the M-test statistic based on mean distances for a sample from a Poisson distribution.
    Parameters:
        sample (np.ndarray): Array of observed counts.
        lambda_val (float): Hypothesized mean of the Poisson distribution.
    Returns:
        float: The M-test statistic value.
    """
    # Handle edge case for lambda_val = 0
    if lambda_val == 0:
        return 0.0  # Return 0 since all values should theoretically match lambda = 0 in this case

    k_vals = np.arange(max(sample) + 1)
    mean_distances = np.array([np.mean([np.abs(k - xi) for xi in sample]) for k in k_vals])
    expected_mean_distances = 2 * k_vals * gammaincc(k_vals, lambda_val) + lambda_val - k_vals - 2 * k_vals * np.exp(-lambda_val)
    
    return np.sum((mean_distances - expected_mean_distances) ** 2)

def poisson_e_test(sample, lambda_val, R=1000):
    """
    Perform the Poisson E-test (energy test) with permutation resampling.
    Parameters:
        sample (np.ndarray): Array of observed counts.
        lambda_val (float): Hypothesized mean of the Poisson distribution.
        R (int): Number of resampling permutations.
    Returns:
        float: E-test statistic.
        float: p-value from the permutation test.
    """
    observed_stat = energy_test_statistic(sample, lambda_val)
    permuted_stats = []
    
    for _ in range(R):
        perm_sample = np.random.poisson(lambda_val, size=len(sample))
        permuted_stats.append(energy_test_statistic(perm_sample, lambda_val))
    
    p_value = np.mean([stat >= observed_stat for stat in permuted_stats])
    return observed_stat, p_value

def poisson_m_test(sample, lambda_val):
    """
    Perform the Poisson M-test based on mean distances.
    Parameters:
        sample (np.ndarray): Array of observed counts.
        lambda_val (float): Hypothesized mean of the Poisson distribution.
    Returns:
        float: M-test statistic.
    """
    return m_test_statistic(sample, lambda_val)
