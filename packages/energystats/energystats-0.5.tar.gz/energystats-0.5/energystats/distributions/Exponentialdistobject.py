import numpy as np
from scipy.stats import expon

class ExponentialDistribution:
    def __init__(self, lambdas):
        """
        Initialize the ExponentialDistribution object with rate parameters (lambdas).
        :param lambdas: List or numpy array of rate parameters (λ).
        """
        self.lambdas = np.array(lambdas)  # Vector of rate parameters (λ)
        self.means = 1 / self.lambdas  # Mean = 1 / λ
        self.variances = 1 / (self.lambdas ** 2)  # Variance = 1 / λ^2

    def pdf(self, x):
        """Compute the Probability Density Function (PDF) at x."""
        return self.lambdas * np.exp(-self.lambdas * x)

    def cdf(self, x):
        """Compute the Cumulative Distribution Function (CDF) at x."""
        return 1 - np.exp(-self.lambdas * x)

    def inverse_cdf(self, p):
        """Compute the inverse CDF (quantile function) for a given probability p."""
        return -np.log(1 - p) / self.lambdas

    def generate_random(self, size=1):
        """Generate random numbers from the exponential distribution."""
        return np.random.exponential(scale=1 / self.lambdas, size=(size, len(self.lambdas)))

    def likelihood(self, values):
        """
        Compute the likelihood of a given set of values.
        :param values: List or numpy array of observed values.
        :return: Product of PDF evaluations at the given values.
        """
        pdf_values = self.pdf(values)
        return np.prod(pdf_values, axis=0)

    @staticmethod
    def from_mean(mean):
        """Create an ExponentialDistribution instance from a given mean."""
        lambdas = 1 / np.array(mean)
        return ExponentialDistribution(lambdas)

    def __repr__(self):
        """String representation of the object."""
        return f"ExponentialDistribution(lambdas={self.lambdas})"
