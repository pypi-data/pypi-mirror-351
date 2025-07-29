import numpy as np
from scipy.spatial.distance import cdist

class KGroupsClustering:
    def __init__(self, n_clusters=3, alpha=1, max_iter=100, tolerance=1e-4):
        """
        Initializes the K-groups clustering model.
        Parameters:
            n_clusters (int): Number of clusters.
            alpha (float): Exponent for distance calculation.
            max_iter (int): Maximum number of iterations.
            tolerance (float): Threshold for stopping criterion.
        """
        self.n_clusters = n_clusters
        self.alpha = alpha
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.labels_ = None
        self.cluster_centers_ = None

    def _calculate_within_dispersion(self, X, labels):
        """
        Calculates the within-cluster dispersion for given data and labels.
        Parameters:
            X (np.ndarray): Data points.
            labels (np.ndarray): Cluster labels for each point.
        Returns:
            float: Within-cluster dispersion.
        """
        dispersion = 0
        for k in range(self.n_clusters):
            cluster_points = X[labels == k]
            if len(cluster_points) > 1:
                distances = cdist(cluster_points, cluster_points, metric='minkowski', p=self.alpha)
                dispersion += np.sum(distances) / (2 * len(cluster_points))
        return dispersion

    def fit(self, X):
        """
        Fits the K-groups clustering model to the data.
        Parameters:
            X (np.ndarray): Data points.
        """
        n_samples = X.shape[0]
        # Randomly assign points to clusters
        self.labels_ = np.random.randint(0, self.n_clusters, n_samples)
        dispersion_prev = float('inf')

        for iteration in range(self.max_iter):
            dispersion = self._calculate_within_dispersion(X, self.labels_)
            
            # Check for convergence
            if abs(dispersion_prev - dispersion) < self.tolerance:
                print(f"Converged at iteration {iteration}")
                break

            dispersion_prev = dispersion

            # Reassign points to minimize within-cluster dispersion
            for i in range(n_samples):
                best_label = self.labels_[i]
                best_dispersion = dispersion
                
                # Test moving point i to each cluster
                for k in range(self.n_clusters):
                    if self.labels_[i] == k:
                        continue
                    
                    old_label = self.labels_[i]
                    self.labels_[i] = k
                    new_dispersion = self._calculate_within_dispersion(X, self.labels_)
                    
                    # Revert change if dispersion does not decrease
                    if new_dispersion < best_dispersion:
                        best_dispersion = new_dispersion
                        best_label = k
                    self.labels_[i] = old_label
                
                # Update label for point i
                self.labels_[i] = best_label

        # Calculate final cluster centers
        self.cluster_centers_ = np.array([X[self.labels_ == k].mean(axis=0) for k in range(self.n_clusters)])

    def predict(self, X):
        """
        Predicts cluster labels for new data points.
        Parameters:
            X (np.ndarray): Data points.
        Returns:
            np.ndarray: Cluster labels.
        """
        distances = np.array([
            np.sum(cdist(X, self.cluster_centers_[k].reshape(1, -1), metric='minkowski', p=self.alpha), axis=1)
            for k in range(self.n_clusters)
        ])
        return np.argmin(distances, axis=0)
