import numpy as np
from scipy.stats import norm, multivariate_normal
from typing import Union

class NormalDistribution:
    def __init__(self, mean: Union[float, np.ndarray], variance: Union[float, np.ndarray]):
        """
        Initialize a NormalDistribution object for univariate or multivariate normal distribution.

        Parameters:
        - mean: Mean value(s), either a float or 1D numpy array for vector variables.
        - variance: Variance value(s), either a float or 1D numpy array for vector variables.
        """
        self.mean = np.asarray(mean)
        self.variance = np.asarray(variance)
        self.dimension = self.mean.shape[0] if self.mean.ndim > 0 else 1  # Handle both scalar and vector cases.

        if self.dimension > 1 and self.variance.shape[0] != self.dimension:
            raise ValueError("Mean and variance must have the same dimension for vector variables.")

    def pdf(self, x: Union[float, np.ndarray]) -> float:
        """Compute the Probability Density Function (PDF) at x."""
        if self.dimension == 1:
            return norm.pdf(x, self.mean, np.sqrt(self.variance))
        else:
            cov = np.diag(self.variance)
            return multivariate_normal.pdf(x, mean=self.mean, cov=cov)

    def cdf(self, x: Union[float, np.ndarray]) -> float:
        """Compute the Cumulative Distribution Function (CDF) at x."""
        if self.dimension == 1:
            return norm.cdf(x, self.mean, np.sqrt(self.variance))
        else:
            raise NotImplementedError("CDF is not implemented for multivariate normal.")

    def inv_cdf(self, p: float) -> Union[float, np.ndarray]:
        """Compute the inverse CDF (quantile function) for probability p."""
        if self.dimension == 1:
            return norm.ppf(p, self.mean, np.sqrt(self.variance))
        else:
            raise NotImplementedError("Inverse CDF is not implemented for multivariate normal.")

    def generate_random(self, size: int = 1) -> np.ndarray:
        """Generate random samples from the distribution."""
        if self.dimension == 1:
            return np.random.normal(self.mean, np.sqrt(self.variance), size)
        else:
            cov = np.diag(self.variance)
            return np.random.multivariate_normal(self.mean, cov, size)

    def log_likelihood(self, data: np.ndarray) -> float:
        """Compute the log-likelihood of the given data."""
        if self.dimension == 1:
            return np.sum(norm.logpdf(data, self.mean, np.sqrt(self.variance)))
        else:
            cov = np.diag(self.variance)
            return np.sum(multivariate_normal.logpdf(data, mean=self.mean, cov=cov))

    @staticmethod
    def from_data(data: np.ndarray) -> "NormalDistribution":
        """Estimate mean and variance from data and create a NormalDistribution instance."""
        mean = np.mean(data, axis=0)
        variance = np.var(data, axis=0, ddof=1)
        return NormalDistribution(mean, variance)

    @staticmethod
    def likelihood(data: np.ndarray, mean: np.ndarray, variance: np.ndarray) -> float:
        """Compute the likelihood of the data given mean and variance."""
        dist = NormalDistribution(mean, variance)
        return np.exp(dist.log_likelihood(data))
