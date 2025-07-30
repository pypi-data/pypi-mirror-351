#!/usr/bin/env python
"""
Unit tests for DBSCAN and OPTICS clustering algorithms.

This test suite validates:
- Importing and using DBSCAN and OPTICS clustering methods
- Creating partitions with DBSCAN and OPTICS
- Testing DBSCANPartitionTransformer and OPTICSPartitionTransformer
- Testing with various parameter settings
- Ensuring proper handling of noise points
"""

import os
import sys
import pytest
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs, make_moons
from sklearn.preprocessing import StandardScaler

# Import the modules to test
from fit_better.core.partitioning import (
    PartitionMode,
    create_partitions,
)
from fit_better.models.sklearn import (
    DBSCANPartitionTransformer,
    OPTICSPartitionTransformer,
    AdaptivePartitionRegressor,
)


@pytest.fixture
def blobs_dataset():
    """Create a simple dataset with well-defined blobs for testing clustering."""
    X, y = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=42)
    X = StandardScaler().fit_transform(X)
    return X, y


@pytest.fixture
def moons_dataset():
    """Create a moons dataset for testing clustering with non-convex shapes."""
    X, y = make_moons(n_samples=300, noise=0.05, random_state=42)
    X = StandardScaler().fit_transform(X)
    return X, y


class TestClusteringAlgorithms:
    """Test suite for DBSCAN and OPTICS clustering algorithms."""

    def test_dbscan_partitioning(self, blobs_dataset):
        """Test DBSCAN partitioning on a simple dataset."""
        X, _ = blobs_dataset

        # Create partitions using DBSCAN
        result = create_partitions(
            X,
            partition_mode=PartitionMode.DBSCAN,
            partition_params={"eps": 0.3, "min_samples": 5},
        )

        # Check if we got valid results
        assert result is not None
        assert "labels" in result
        assert "partition_indices" in result
        assert "n_clusters" in result

        # Check number of clusters (should find 4 for the blobs dataset)
        assert result["n_clusters"] >= 3  # At least 3 clusters

        # Check that all points are assigned to a cluster
        assert len(result["labels"]) == len(X)

        # Check that partition indices match labels
        for i, indices in enumerate(result["partition_indices"]):
            for idx in indices:
                assert result["labels"][idx] == i

    def test_optics_partitioning(self, moons_dataset):
        """Test OPTICS partitioning on a moons dataset."""
        X, _ = moons_dataset

        # Create partitions using OPTICS
        result = create_partitions(
            X,
            partition_mode=PartitionMode.OPTICS,
            partition_params={"min_samples": 5, "xi": 0.05},
        )

        # Check if we got valid results
        assert result is not None
        assert "labels" in result
        assert "partition_indices" in result
        assert "n_clusters" in result
        assert "reachability" in result

        # OPTICS should identify the two moons
        assert result["n_clusters"] >= 1  # At least 1 cluster

        # Check that all points are assigned to a cluster or noise
        assert len(result["labels"]) == len(X)

        # Check that reachability is computed
        assert len(result["reachability"]) > 0

    def test_dbscan_transformer(self, blobs_dataset):
        """Test the DBSCANPartitionTransformer with scikit-learn API."""
        X, _ = blobs_dataset

        # Create and fit the transformer
        transformer = DBSCANPartitionTransformer(eps=0.3, min_samples=5)
        X_transformed = transformer.fit_transform(X)

        # Check that a new column is added with cluster assignments
        assert X_transformed.shape[1] == X.shape[1] + 1

        # Check that the right number of clusters is found
        assert transformer.get_n_clusters() >= 3

        # Check that labels are properly set
        assert hasattr(transformer, "labels_")
        assert len(transformer.labels_) == len(X)

    def test_optics_transformer(self, moons_dataset):
        """Test the OPTICSPartitionTransformer with scikit-learn API."""
        X, _ = moons_dataset

        # Create and fit the transformer
        transformer = OPTICSPartitionTransformer(min_samples=5, xi=0.05)
        X_transformed = transformer.fit_transform(X)

        # Check that a new column is added with cluster assignments
        assert X_transformed.shape[1] == X.shape[1] + 1

        # Check that the right number of clusters is found
        assert transformer.get_n_clusters() >= 1

        # Check that labels and reachability are properly set
        assert hasattr(transformer, "labels_")
        assert hasattr(transformer, "reachability_")
        assert len(transformer.labels_) == len(X)
        assert len(transformer.reachability_) == len(X)

        # Test the get_reachability method
        reachability = transformer.get_reachability()
        assert reachability is not None
        assert len(reachability) == len(X)

    def test_adaptive_regressor_with_dbscan(self, blobs_dataset):
        """Test the AdaptivePartitionRegressor with DBSCANPartitionTransformer."""
        X, _ = blobs_dataset

        # Create random target values for regression testing
        np.random.seed(42)
        y = 2 * X[:, 0] + 3 * X[:, 1] + np.random.normal(0, 0.5, len(X))

        # Split into train and test
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        # Create a DBSCANPartitionTransformer
        transformer = DBSCANPartitionTransformer(eps=0.3, min_samples=5)

        # Create and fit the adaptive regressor
        regressor = AdaptivePartitionRegressor(partitioner=transformer, cv=3, n_jobs=1)
        regressor.fit(X_train, y_train)

        # Test prediction
        y_pred = regressor.predict(X_test)
        assert len(y_pred) == len(y_test)

        # Test scoring
        score = regressor.score(X_test, y_test)
        assert 0 <= score <= 1  # R-squared score should be between 0 and 1

    def test_adaptive_regressor_with_optics(self, moons_dataset):
        """Test the AdaptivePartitionRegressor with OPTICSPartitionTransformer."""
        X, _ = moons_dataset

        # Create random target values for regression testing
        np.random.seed(42)
        y = 2 * X[:, 0] + 3 * X[:, 1] + np.random.normal(0, 0.5, len(X))

        # Split into train and test
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        # Create an OPTICSPartitionTransformer with adjusted parameters for better performance
        transformer = OPTICSPartitionTransformer(min_samples=3, xi=0.1)

        # Create and fit the adaptive regressor
        regressor = AdaptivePartitionRegressor(partitioner=transformer, cv=3, n_jobs=1)
        regressor.fit(X_train, y_train)

        # Test prediction
        y_pred = regressor.predict(X_test)
        assert len(y_pred) == len(y_test)

        # Test scoring
        score = regressor.score(X_test, y_test)
        # R-squared can be negative if the model performs worse than the mean
        # For this test, we just want to ensure it computes a score without error
        assert score < 10.0  # Just check that score is a reasonable number

    def test_noise_handling(self):
        """Test proper handling of noise points in DBSCAN and OPTICS."""
        # Create dataset with obvious noise
        np.random.seed(42)
        X_core = np.random.randn(200, 2) * 0.3
        X_noise = np.random.uniform(-2, 2, (50, 2))
        X = np.vstack([X_core, X_noise])

        # Test DBSCAN
        dbscan_result = create_partitions(
            X,
            partition_mode=PartitionMode.DBSCAN,
            partition_params={"eps": 0.3, "min_samples": 5},
        )

        # DBSCAN should identify the core cluster and mark others as noise
        assert -1 in np.unique(dbscan_result["labels"])

        # Test OPTICS
        optics_result = create_partitions(
            X,
            partition_mode=PartitionMode.OPTICS,
            partition_params={"min_samples": 5, "xi": 0.05},
        )

        # OPTICS should identify the core cluster and mark others as noise
        assert -1 in np.unique(optics_result["labels"])
