from estats.tests.Dirichletdistobject import DirichletDistribution
import numpy as np

# Initialize a Dirichlet distribution with concentration parameters [2, 3, 4]
alphas = np.array([2.0, 3.0, 4.0])
dirichlet_dist = DirichletDistribution(alphas)

# Print mean and variance
print("Mean:", dirichlet_dist.mean())
print("Variance:", dirichlet_dist.variance())

# Generate 5 random samples
samples = dirichlet_dist.generate_random(size=5)
print("Random Samples:\n", samples)

# Compute the PDF for a given point
x = np.array([0.2, 0.3, 0.5])
print("PDF at x:", dirichlet_dist.pdf(x))

# Compute the log-likelihood of a dataset
dataset = np.array([[0.2, 0.3, 0.5], [0.1, 0.6, 0.3]])
print("Log-Likelihood:", dirichlet_dist.log_likelihood(dataset))

# Estimate parameters from data and create a new distribution
estimated_dist = DirichletDistribution.from_data(dataset)
print("Estimated Alphas:", estimated_dist.alphas)
