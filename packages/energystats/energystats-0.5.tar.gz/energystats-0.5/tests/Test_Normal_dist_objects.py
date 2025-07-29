from estats.estats.distributions.Normaldistobject import NormalDistribution
import numpy as np 

if __name__ == "__main__":
    # Univariate normal distribution
    univariate_dist = NormalDistribution(mean = 0, variance = 1)
    print("Univariate PDF at x=0:", univariate_dist.pdf(0))
    print("Univariate Random Samples:", univariate_dist.generate_random(5))

    # Multivariate normal distribution
    mean_vector = [0, 0]
    variance_vector = [1, 1]
    multivariate_dist = NormalDistribution(mean_vector, variance_vector)
    print("Multivariate PDF at [0, 0]:", multivariate_dist.pdf([0, 0]))
    print("Multivariate Random Samples:\n", multivariate_dist.generate_random(3))

    # Estimate parameters from data
    data = np.random.normal(0, 1, size=(100, 2))
    estimated_dist = NormalDistribution.from_data(data)
    print("Estimated Mean:", estimated_dist.mean)
    print("Estimated Variance:", estimated_dist.variance)