import numpy as np
from scipy.stats import zscore, norm
from scipy.special import hyp1f1, gamma
# from scipy.spatial import distance_matrix
from scipy.spatial.distance import pdist
import warnings

def normality_statistic(x: np.array) -> np.float64:
    """
    Returns the statistic for the univariate normality test
    """
    x = np.array(x)
    n = len(x)

    y = np.sort(zscore(x, ddof=1)) 
    k = np.arange(1 - n, n, 2)
    
    statistic = 2 * (np.sum(2 * y * norm.cdf(y) + 2 * norm.pdf(y)) - n/np.sqrt(np.pi) - np.mean(k * y))
    
    return statistic





def m_normality_statistic(x: np.array) -> float:
    """
    Computes the E-statistic for the multivariate normality test.

    Parameters:
        x (np.array): Input data array of shape (n_samples, n_features).

    Returns:
        float: E-statistic for the multivariate normality test.
    """

    n, d = x.shape

    # Handle edge cases
    if n < 2:
        raise ValueError("Sample size must be at least 2")
    if d < 1:
        raise ValueError("Number of features must be at least 1")
     # Handle case where data has only one feature (100x1 case)
    if d == 1:
        warnings.warn("Data has only one feature, multivariate normality cannot be computed. will use univariate normal test")
        return normality_statistic(x)  # Return NaN for single feature datasets


    # Step 1: Center and whiten the data
    x_mean = np.mean(x, axis=0)
    z = x - x_mean  # Center the data
    cov_matrix = np.cov(z, rowvar=False)

    # Check covariance matrix validity
    if np.linalg.cond(cov_matrix) > 1e12:
        warnings.warn("Covariance matrix is ill-conditioned or singular.", UserWarning)
        
        # cov_matrix += np.eye(cov_matrix.shape[0]) * 1e-10  # Small regularization term
        # print("Regularization applied to covariance matrix.")
        return np.nan

    
    if np.any(np.diag(cov_matrix) == 0):
        warnings.warn("Covariance matrix is ill-conditioned or singular.", UserWarning)
        return np.nan

    
    

    try:
        eigvals, eigvecs = np.linalg.eigh(cov_matrix)
        # Handle very small eigenvalues to avoid division by zero
        eigvals = np.maximum(eigvals, 1e-10)
        whitening_matrix = eigvecs @ np.diag(1 / np.sqrt(eigvals)) @ eigvecs.T
        y = z @ whitening_matrix
    except Exception as e:
        raise ValueError(f"Whitening failed: {e}")

    if not np.all(np.isfinite(y)):
        warnings.warn("Non-finite values encountered during whitening.", UserWarning)
        return np.nan  # Return NaN if whitening leads to non-finite values

    # Step 2: Constants for the E-statistic
    const = np.exp(np.log(gamma((d + 1) / 2)) - np.log(gamma(d / 2)))
    mean2 = 2 * const

    # Step 3: Compute squared norms and hypergeometric term
    ysq = np.sum(y ** 2, axis=1)
    try:
        mean1 = np.sqrt(2) * const * np.mean(hyp1f1(-0.5, d / 2, -ysq / 2))
    except Exception as e:
        raise ValueError(f"Failed to compute hypergeometric term: {e}")

    # Step 4: Pairwise distances
    try:
        pairwise_dists = pdist(y)
        mean3 = 2 * np.sum(pairwise_dists) / (n ** 2)
    except Exception as e:
        raise ValueError(f"Failed to compute pairwise distances: {e}")

    # Step 5: E-statistic
    e_statistic = n * (2 * mean1 - mean2 - mean3)
    if np.isinf(e_statistic):
        warnings.warn("E-statistic is infinity due to numerical instability.", UserWarning)
        return np.nan  # Return NaN if E-statistic is infinite

    return e_statistic

