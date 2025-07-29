import numpy as np

def energy_distance(x, y):
    """
    Calculate the sample energy distance between two samples x and y.
    Parameters:
        x (np.ndarray): Sample from distribution X.
        y (np.ndarray): Sample from distribution Y.
    Returns:
        float: The calculated energy distance.
    """
    n, m = len(x), len(y)
    A = np.sum([np.abs(xi - yj) for xi in x for yj in y]) / (n * m)
    B = np.sum([np.abs(xi - xj) for xi in x for xj in x]) / (n ** 2)
    C = np.sum([np.abs(yi - yj) for yi in y for yj in y]) / (m ** 2)
    
    # Calculate and return the energy distance statistic
    return 2 * A - B - C

def two_sample_energy_test(x, y, R = 1000):
    """
    Perform a two-sample energy test to determine if two samples come from the same distribution.
    Parameters:
        x (np.ndarray): Sample from distribution X.
        y (np.ndarray): Sample from distribution Y.
        R (int): Number of permutations to generate the null distribution.
    Returns:
        float: Test statistic value.
        float: p-value from the permutation test.
    """
    n, m = len(x), len(y)
    combined = np.concatenate([x, y])
    observed_stat = (n * m / (n + m)) * energy_distance(x, y)

    # Permutation test
    permuted_stats = []
    for _ in range(R):
        np.random.shuffle(combined)
        perm_x = combined[:n]
        perm_y = combined[n:]
        permuted_stat = (n * m / (n + m)) * energy_distance(perm_x, perm_y)
        permuted_stats.append(permuted_stat)

    p_value = np.mean([stat >= observed_stat for stat in permuted_stats])

    return observed_stat, p_value
