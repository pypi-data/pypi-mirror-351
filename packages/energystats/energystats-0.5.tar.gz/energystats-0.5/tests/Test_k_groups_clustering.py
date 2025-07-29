import unittest
import numpy as np
import matplotlib.pyplot as plt
from estats.k_groups_clustering import KGroupsClustering
from sklearn.cluster import KMeans

class TestKGroupsClustering(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        # Create synthetic data for testing with more clusters and varying sizes
        self.data_2d = np.vstack([
            np.random.normal(0, 1, (50, 2)),
            np.random.normal(5, 1, (50, 2)),
            np.random.normal(-5, 1, (50, 2)),
            np.random.normal(10, 1, (50, 2)),
            np.random.normal(-10, 1, (50, 2))
        ])

    def test_multiple_clusters(self):
        # Test with a variety of cluster counts
        for n_clusters in [3, 5, 8, 10]:
            model = KGroupsClustering(n_clusters=n_clusters, alpha=1, max_iter=100, tolerance=1e-3)
            model.fit(self.data_2d)
            self.assertEqual(len(np.unique(model.labels_)), n_clusters, f"Should have {n_clusters} clusters")

    def test_kmeans_comparison(self):
        # Compare K-Groups and K-means for clustering similarity
        k_clusters = 5
        k_groups_model = KGroupsClustering(n_clusters=k_clusters, alpha=2)  # Alpha=2 for K-means-like behavior
        k_groups_model.fit(self.data_2d)
        
        kmeans_model = KMeans(n_clusters=k_clusters, random_state=42)
        kmeans_model.fit(self.data_2d)

        # Visual comparison of K-Groups and K-means clustering
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # K-Groups clustering visualization
        ax1.set_title("K-Groups Clustering (alpha=2)")
        for i in range(k_clusters):
            ax1.scatter(self.data_2d[k_groups_model.labels_ == i, 0], self.data_2d[k_groups_model.labels_ == i, 1], label=f"Cluster {i+1}")
        ax1.scatter(k_groups_model.cluster_centers_[:, 0], k_groups_model.cluster_centers_[:, 1], c='red', marker='X', s=200, label="Centers")
        ax1.legend()

        # K-means clustering visualization
        ax2.set_title("K-Means Clustering")
        for i in range(k_clusters):
            ax2.scatter(self.data_2d[kmeans_model.labels_ == i, 0], self.data_2d[kmeans_model.labels_ == i, 1], label=f"Cluster {i+1}")
        ax2.scatter(kmeans_model.cluster_centers_[:, 0], kmeans_model.cluster_centers_[:, 1], c='red', marker='X', s=200, label="Centers")
        ax2.legend()

        plt.show()

    def test_high_number_of_clusters(self):
        # Test with a large number of clusters
        n_clusters = 20
        model = KGroupsClustering(n_clusters=n_clusters, alpha=1, max_iter=100, tolerance=1e-3)
        model.fit(self.data_2d)
        self.assertEqual(len(np.unique(model.labels_)), n_clusters, "Should be able to handle 20 clusters")

    def test_different_initializations(self):
        # Run K-Groups clustering multiple times to ensure consistent convergence
        for i in range(3):  # Run three times to verify stability
            model = KGroupsClustering(n_clusters=5, alpha=1, max_iter=100, tolerance=1e-3)
            model.fit(self.data_2d)
            self.assertTrue(model.cluster_centers_ is not None, "Model should converge and produce centers each time")

    def test_visualize_multiple_alpha_values(self):
        # Test clustering with different alpha values and visualize
        for alpha in [0.5, 1, 1.5, 2]:  # Increasing alpha values
            model = KGroupsClustering(n_clusters=5, alpha=alpha)
            model.fit(self.data_2d)

            plt.figure(figsize=(8, 6))
            plt.title(f"K-Groups Clustering with alpha={alpha}")
            for i in range(5):
                plt.scatter(self.data_2d[model.labels_ == i, 0], self.data_2d[model.labels_ == i, 1], label=f"Cluster {i+1}")
            plt.scatter(model.cluster_centers_[:, 0], model.cluster_centers_[:, 1], c='red', marker='X', s=200, label="Centers")
            plt.xlabel("Feature 1")
            plt.ylabel("Feature 2")
            plt.legend()
            plt.show()

if __name__ == "__main__":
    unittest.main()
