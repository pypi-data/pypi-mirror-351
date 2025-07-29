import numpy as np
from scipy.special import gammaincc

def geometric_expected_distance(p, k):
    """
    Calculate the expected distance E|k - X| for a geometric distribution with parameter p.
    Parameters:
        p (float): Probability of success in the geometric distribution.
        k (int): Value for which to compute the expected distance.
    Returns:
        float: Expected distance E|k - X|.
    """
    q = 1 - p
    theta = (1 - p) / p
    F_k_minus_1 = 1 - q**k  # CDF of Geometric at (k - 1) for Geometric(p)
    
    return k + theta - 2 * theta * F_k_minus_1

def expected_pairwise_distance(p):
    """
    Calculate E|X - X'| for two independent geometric random variables with parameter p.
    Parameters:
        p (float): Probability of success in the geometric distribution.
    Returns:
        float: Expected distance E|X - X'|.
    """
    q = 1 - p
    return 2 * q / (1 - q**2)

def geometric_energy_test(sample, p, R=1000):
    """
    Perform the energy goodness-of-fit test for a geometric distribution.
    Parameters:
        sample (np.ndarray): Observed sample from the distribution.
        p (float): Hypothesized parameter of the geometric distribution.
        R (int): Number of permutations for resampling.
    Returns:
        float: Test statistic for the geometric distribution.
        float: p-value from permutation test.
    """
    n = len(sample)
    observed_distance_sum = np.mean([np.abs(k - np.mean(sample)) for k in sample])
    expected_distance = geometric_expected_distance(p, np.mean(sample))
    intra_sample_distance = np.mean([np.abs(xi - xj) for xi in sample for xj in sample]) / n
    
    test_stat = n * (2 * observed_distance_sum - expected_distance - intra_sample_distance)
    
    perm_stats = []
    for _ in range(R):
        perm_sample = np.random.geometric(p, size=n)
        perm_stats.append(n * (2 * np.mean(np.abs(perm_sample - np.mean(perm_sample))) - 
                               expected_distance - 
                               np.mean([np.abs(xi - xj) for xi in perm_sample for xj in perm_sample]) / n))
    
    p_value = np.mean([stat >= test_stat for stat in perm_stats])
    
    return test_stat, p_value

def longest_run(sequence):
    """
    Calculate the longest run of consecutive identical values (0s or 1s) in a 0-1 sequence.
    Parameters:
        sequence (list or np.ndarray): Binary sequence of 0s and 1s.
    Returns:
        int: Length of the longest run.
    """
    if len(sequence) == 0:
        return 0  # Return 0 for an empty sequence
    
    max_run = current_run = 1
    for i in range(1, len(sequence)):
        if sequence[i] == sequence[i - 1]:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    return max_run

def test_iid_sequence(sequence, p, R=1000):
    """
    Test if a 0-1 sequence resembles an IID sequence with Bernoulli(p) trials.
    Parameters:
        sequence (list or np.ndarray): Binary sequence of 0s and 1s.
        p (float): Hypothesized success probability for Bernoulli trials.
        R (int): Number of simulations for permutation testing.
    Returns:
        float: Longest run in observed sequence.
        float: Expected longest run in a random sequence of similar length.
        float: p-value for independence test.
    """
    n = len(sequence)
    if n == 0:
        raise ValueError("The input sequence is empty. Cannot calculate longest run.")

    observed_longest_run = longest_run(sequence)
    expected_longest_run = np.log2(n)
    
    perm_longest_runs = []
    for _ in range(R):
        perm_sequence = np.random.binomial(1, p, size=n)
        perm_longest_runs.append(longest_run(perm_sequence))
    
    p_value = np.mean([run >= observed_longest_run for run in perm_longest_runs])
    
    return observed_longest_run, expected_longest_run, p_value