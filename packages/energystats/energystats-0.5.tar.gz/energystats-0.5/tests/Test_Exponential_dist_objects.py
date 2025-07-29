from estats.estats.distributions.Exponentialdistobject import ExponentialDistribution

# Initialize an ExponentialDistribution object with λ = [1, 2, 3]
exp_dist = ExponentialDistribution([1, 2, 3])

# Compute the PDF at x = 1.0
print(exp_dist.pdf(1.0))  # Output: [0.36787944 0.27067057 0.22313016]

# Compute the CDF at x = 1.0
print(exp_dist.cdf(1.0))  # Output: [0.63212056 0.86466472 0.95021293]

# Compute the inverse CDF (quantile) for p = 0.5
print(exp_dist.inverse_cdf(0.5))  # Output: [0.69314718 0.34657359 0.23104906]

# Generate 5 random samples
print(exp_dist.generate_random(size=5))

# Compute the likelihood of some values
values = [1.0, 0.5, 2.0]
print(exp_dist.likelihood(values))  # Output: Product of the PDF evaluations

# Create an instance from a mean value
exp_from_mean = ExponentialDistribution.from_mean([1.0, 0.5])
print(exp_from_mean)
