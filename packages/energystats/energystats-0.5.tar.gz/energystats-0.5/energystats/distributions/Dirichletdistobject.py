import numpy as np
from scipy.stats import dirichlet
from typing import Union

class DirichletDistribution:
    def __init__(self, alphas: Union[np.ndarray, list[float]]):
        """
        Initialize a DirichletDistribution object.

        Parameters:
        - alphas: Concentration parameters, a 1D numpy array or list of positive floats.
        """
        self.alphas = np.asarray(alphas, dtype=float)

        if np.any(self.alphas <= 0):
            raise ValueError("All alpha values must be positive.")
        
        self.dimension = self.alphas.shape[0]

    def pdf(self, x: np.ndarray) -> float:
        """
        Compute the Probability Density Function (PDF) at x.

        Parameters:
        - x: A 1D array representing a valid probability vector (sums to 1, all values > 0).
        """
        if not np.allclose(np.sum(x), 1.0) or np.any(x <= 0):
            raise ValueError("Input vector must sum to 1 and contain only positive values.")
        return dirichlet.pdf(x, self.alphas)

    def mean(self) -> np.ndarray:
        """
        Compute the mean of the Dirichlet distribution.
        """
        return self.alphas / np.sum(self.alphas)

    def variance(self) -> np.ndarray:
        """
        Compute the variance of each component of the Dirichlet distribution.
        """
        alpha_0 = np.sum(self.alphas)
        return (self.alphas * (alpha_0 - self.alphas)) / (alpha_0 ** 2 * (alpha_0 + 1))

    def generate_random(self, size: int = 1) -> np.ndarray:
        """
        Generate random samples from the Dirichlet distribution.

        Parameters:
        - size: Number of random samples to generate.
        """
        return np.random.dirichlet(self.alphas, size=size)

    def log_likelihood(self, data: np.ndarray) -> float:
        """
        Compute the log-likelihood of a dataset given the current Dirichlet parameters.

        Parameters:
        - data: A 2D array where each row is a probability vector.
        """
        if data.shape[1] != self.dimension:
            raise ValueError("Data dimension must match the number of alphas.")
        return np.sum([np.log(self.pdf(row)) for row in data])

    @staticmethod
    def from_data(data: np.ndarray) -> "DirichletDistribution":
        """
        Estimate the alphas from data using the method of moments and create a DirichletDistribution instance.

        Parameters:
        - data: A 2D array where each row is a probability vector.
        """
        mean = np.mean(data, axis=0)
        alpha_0 = np.mean(mean * (1 - mean)) / (np.var(data, axis=0, ddof=1).mean())
        alphas = mean * alpha_0
        return DirichletDistribution(alphas)

    def __repr__(self):
        return f"DirichletDistribution(alphas={self.alphas})"
