import unittest
import numpy as np
import matplotlib.pyplot as plt
from estats.k_groups_clustering import KGroupsClustering

class TestKGroupsClusteringChallenging(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)

    def test_overlapping_clusters(self):
        # Generate overlapping clusters
        data = np.vstack([
            np.random.normal(0, 1, (100, 2)),
            np.random.normal(1, 1, (100, 2))
        ])
        model = KGroupsClustering(n_clusters=2, alpha=1, max_iter=100)
        model.fit(data)
        
        # Visualize the clustering result
        plt.figure(figsize=(8, 6))
        plt.title("Overlapping Clusters")
        for i in range(2):
            plt.scatter(data[model.labels_ == i, 0], data[model.labels_ == i, 1], label=f"Cluster {i+1}")
        plt.scatter(model.cluster_centers_[:, 0], model.cluster_centers_[:, 1], c='red', marker='X', s=200, label="Centers")
        plt.legend()
        plt.show()

    def test_different_densities(self):
        # Generate clusters with different densities
        data = np.vstack([
            np.random.normal(0, 0.5, (50, 2)),     # Dense cluster
            np.random.normal(5, 2, (200, 2))       # Spread-out cluster
        ])
        model = KGroupsClustering(n_clusters=2, alpha=1, max_iter=100)
        model.fit(data)

        # Visualize the clustering result
        plt.figure(figsize=(8, 6))
        plt.title("Clusters with Different Densities")
        for i in range(2):
            plt.scatter(data[model.labels_ == i, 0], data[model.labels_ == i, 1], label=f"Cluster {i+1}")
        plt.scatter(model.cluster_centers_[:, 0], model.cluster_centers_[:, 1], c='red', marker='X', s=200, label="Centers")
        plt.legend()
        plt.show()

    def test_non_spherical_clusters(self):
        # Generate non-spherical clusters (elongated shapes)
        theta = np.linspace(0, 2 * np.pi, 100)
        cluster1 = np.column_stack((np.cos(theta), 2 * np.sin(theta))) + np.random.normal(0, 0.1, (100, 2))
        cluster2 = np.column_stack((3 + np.cos(theta), 2 * np.sin(theta))) + np.random.normal(0, 0.1, (100, 2))
        data = np.vstack([cluster1, cluster2])

        model = KGroupsClustering(n_clusters=2, alpha=1, max_iter=100)
        model.fit(data)

        # Visualize the clustering result
        plt.figure(figsize=(8, 6))
        plt.title("Non-Spherical Clusters")
        for i in range(2):
            plt.scatter(data[model.labels_ == i, 0], data[model.labels_ == i, 1], label=f"Cluster {i+1}")
        plt.scatter(model.cluster_centers_[:, 0], model.cluster_centers_[:, 1], c='red', marker='X', s=200, label="Centers")
        plt.legend()
        plt.show()

    def test_with_noise_and_outliers(self):
        # Generate two clusters with additional noise points
        data = np.vstack([
            np.random.normal(0, 1, (50, 2)),
            np.random.normal(5, 1, (50, 2)),
            np.random.uniform(-10, 10, (20, 2))  # Noise/outliers
        ])
        model = KGroupsClustering(n_clusters=2, alpha=1, max_iter=100)
        model.fit(data)

        # Visualize the clustering result
        plt.figure(figsize=(8, 6))
        plt.title("Clusters with Noise and Outliers")
        for i in range(2):
            plt.scatter(data[model.labels_ == i, 0], data[model.labels_ == i, 1], label=f"Cluster {i+1}")
        plt.scatter(model.cluster_centers_[:, 0], model.cluster_centers_[:, 1], c='red', marker='X', s=200, label="Centers")
        plt.legend()
        plt.show()

    def test_high_dimensional_data_with_close_clusters(self):
        # High-dimensional data with clusters close to each other
        data = np.vstack([
            np.random.normal(0, 1, (100, 10)),
            np.random.normal(1, 1, (100, 10))  # Clusters are close in high-dimensional space
        ])
        model = KGroupsClustering(n_clusters=2, alpha=1, max_iter=100)
        model.fit(data)

        # Evaluate clustering result
        unique_labels = len(np.unique(model.labels_))
        self.assertEqual(unique_labels, 2, "Should identify 2 clusters in high-dimensional data with close clusters")

if __name__ == "__main__":
    unittest.main()
