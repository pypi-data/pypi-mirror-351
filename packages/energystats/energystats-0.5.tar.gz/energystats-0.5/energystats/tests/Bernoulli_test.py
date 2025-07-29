import numpy as np

def compute_statistic_T(n, h, p_bar):
    """
    Computes the statistic T for the Bernoulli goodness-of-fit test.
    Parameters:
        n (int): Total number of samples.
        h (int): Number of successes (1s) in the sample.
        p_bar (float): Estimate for the success probability p.
    Returns:
        float: The test statistic T.
    """
    term_1 = (2 / n) * (h * (1 - p_bar) + (n - h) * p_bar)
    term_2 = -2 * p_bar * (1 - p_bar)
    term_3 = -2 * h * (n - h) / n**2
    T = term_1 + term_2 + term_3
    return T

def energy_goodness_of_fit_bernoulli(sample=None, n=None, h=None, p_bar=None, R=1000):
    """
    Conducts the energy goodness-of-fit test for a Bernoulli distribution.
    Parameters:
        sample (list or np.ndarray, optional): A sample of 0s and 1s.
        n (int, optional): Total number of samples.
        h (int, optional): Number of successes (1s) in the sample.
        p_bar (float, optional): Estimate for the success probability p.
        R (int): Number of resampling permutations.
    Returns:
        dict: Test statistic and p-value.
    """

    # If sample is provided, calculate n, h, and p_bar from it
    if sample is not None:
        n = len(sample)
        if n == 0:
            raise ValueError("Sample is empty. Cannot compute goodness-of-fit test.")
        
        h = np.sum(sample)
        p_bar = h / n
    elif n is None or h is None or p_bar is None:
        raise ValueError("Provide either 'sample' or 'n', 'h', and 'p_bar'.")

    # Compute the observed statistic T
    observed_statistic = compute_statistic_T(n, h, p_bar)

    # Generate R simulated samples from Bernoulli(p_bar) and compute T for each
    simulated_statistics = []
    for _ in range(R):
        simulated_sample = np.random.binomial(1, p_bar, n)
        h_simulated = np.sum(simulated_sample)
        simulated_statistics.append(compute_statistic_T(n, h_simulated, p_bar))

    # Compute p-value as proportion of simulated T's >= observed T
    p_value = np.mean([sim_stat >= observed_statistic for sim_stat in simulated_statistics])

    return {"T": observed_statistic, "p-value": p_value}
