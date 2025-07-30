#!/usr/bin/env python
"""
Unit tests for MLPRegressor and KMEANS_PLUS_PLUS clustering.

This test suite validates:
- Using MLPRegressor as a model type
- Using KMEANS_PLUS_PLUS for partitioning
- Integration of MLPRegressor with partitioning
"""

import os
import sys
import pytest
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs, make_moons
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Import the modules to test
from fit_better.core.partitioning import (
    PartitionMode,
    create_partitions,
    train_models_on_partitions,
    predict_with_partitioned_models,
    create_kmeans_plus_plus_boundaries,
)
from fit_better.core.models import (
    RegressorType,
    fit_all_regressors,
    select_best_model,
    Metric,
)
from fit_better.models.sklearn import (
    PartitionTransformer,
    AdaptivePartitionRegressor,
)


@pytest.fixture
def regression_dataset():
    """Create a dataset with multiple clusters for testing."""
    # Create 4 clusters of different densities with non-linear relationships
    np.random.seed(42)
    n_samples = 1000
    X = np.random.randn(n_samples, 2) * 2

    # Create a non-linear target with different patterns in different regions
    y = np.zeros(n_samples)

    # Quadratic relationship in one region
    mask1 = (X[:, 0] > 0) & (X[:, 1] > 0)
    y[mask1] = 2 * X[mask1, 0] ** 2 + X[mask1, 1] + np.random.randn(np.sum(mask1)) * 0.5

    # Linear relationship in second region
    mask2 = (X[:, 0] <= 0) & (X[:, 1] > 0)
    y[mask2] = 3 * X[mask2, 0] + 2 * X[mask2, 1] + np.random.randn(np.sum(mask2)) * 0.3

    # Sinusoidal relationship in third region
    mask3 = (X[:, 0] > 0) & (X[:, 1] <= 0)
    y[mask3] = (
        np.sin(X[mask3, 0]) + 0.5 * X[mask3, 1] + np.random.randn(np.sum(mask3)) * 0.4
    )

    # Exponential relationship in fourth region
    mask4 = (X[:, 0] <= 0) & (X[:, 1] <= 0)
    y[mask4] = (
        np.exp(0.5 * X[mask4, 0]) + X[mask4, 1] + np.random.randn(np.sum(mask4)) * 0.6
    )

    return X, y


class TestMLPAndKmeansPlusPlus:
    """Test suite for MLPRegressor and KMEANS_PLUS_PLUS partitioning."""

    def test_mlp_regressor_creation(self):
        """Test creating an MLPRegressor model."""
        from fit_better.core.models import create_regressor

        # Create MLPRegressor
        model = create_regressor(RegressorType.MLP)

        # Check that the model is of the right type
        from sklearn.neural_network import MLPRegressor

        assert isinstance(model, MLPRegressor)

        # Check that the model has the expected parameters
        assert model.hidden_layer_sizes == (100, 50)
        assert model.activation == "relu"
        assert model.solver == "adam"
        assert model.random_state == 42
        assert model.early_stopping

    def test_mlp_regressor_fitting(self, regression_dataset):
        """Test fitting an MLPRegressor on a dataset."""
        X, y = regression_dataset

        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        # Create and fit MLPRegressor
        from fit_better.core.models import create_regressor

        model = create_regressor(RegressorType.MLP)
        model.fit(X_train, y_train)

        # Check that the model makes predictions
        y_pred = model.predict(X_test)
        assert len(y_pred) == len(y_test)

        # Check that the model has reasonable R2 score
        r2 = model.score(X_test, y_test)
        assert -1.0 <= r2 <= 1.0  # R2 can be negative for bad fits

    def test_kmeans_plus_plus_partitioning(self, regression_dataset):
        """Test KMEANS_PLUS_PLUS partitioning."""
        X, y = regression_dataset

        # Create partitions using KMEANS_PLUS_PLUS
        result = create_partitions(
            X, partition_mode=PartitionMode.KMEANS_PLUS_PLUS, n_partitions=4
        )

        # Check if we got valid results
        assert result is not None
        assert "labels" in result
        assert "partition_indices" in result
        assert "n_clusters" in result

        # Check number of clusters (should find 4 for our dataset)
        assert result["n_clusters"] >= 3  # At least 3 clusters

        # Check that all points are assigned to a cluster
        assert len(result["labels"]) == len(X)

        # Check that partition indices match labels
        for i, indices in enumerate(result["partition_indices"]):
            for idx in indices:
                assert result["labels"][idx] == i

    def test_create_kmeans_plus_plus_boundaries(self, regression_dataset):
        """Test the utility function for creating KMEANS_PLUS_PLUS boundaries."""
        X, _ = regression_dataset

        # Create boundaries
        boundaries = create_kmeans_plus_plus_boundaries(X, k=4)

        # Check that we got valid boundaries
        assert boundaries is not None
        assert (
            len(boundaries) <= 3
        )  # For 4 partitions, we should have at most 3 boundaries

    def test_integrated_mlp_with_kmeans_plus_plus(self, regression_dataset):
        """Test using MLPRegressor with KMEANS_PLUS_PLUS partitioning."""
        X, y = regression_dataset

        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        # Train models on partitions
        partition_results = train_models_on_partitions(
            X_train,
            y_train,
            n_parts=4,
            partition_mode=PartitionMode.KMEANS_PLUS_PLUS,
            regressor_type=RegressorType.MLP,
            n_jobs=1,
        )

        # Check that we got valid results
        assert isinstance(partition_results, dict)
        assert "models" in partition_results
        assert len(partition_results["models"]) > 0

        # Make predictions on test data
        y_pred = predict_with_partitioned_models(partition_results, X_test, n_jobs=1)

        # Check that we got valid predictions
        assert len(y_pred) == len(y_test)

        # Calculate R2 score manually
        from sklearn.metrics import r2_score

        r2 = r2_score(y_test, y_pred)
        assert -1.0 <= r2 <= 1.0

    def test_adaptive_regressor_with_kmeans_plus_plus(self, regression_dataset):
        """Test AdaptivePartitionRegressor with KMEANS_PLUS_PLUS."""
        X, y = regression_dataset

        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        # Create a PartitionTransformer with KMEANS_PLUS_PLUS
        transformer = PartitionTransformer(n_parts=4, partition_mode="kmeans++")

        # Create and fit AdaptivePartitionRegressor with MLPRegressor as base estimator
        from sklearn.neural_network import MLPRegressor

        regressor = AdaptivePartitionRegressor(
            base_estimator=MLPRegressor(
                hidden_layer_sizes=(50,), max_iter=200, random_state=42
            ),
            partitioner=transformer,
            cv=3,
            n_jobs=1,
        )
        regressor.fit(X_train, y_train)

        # Test prediction
        y_pred = regressor.predict(X_test)
        assert len(y_pred) == len(y_test)

        # Test scoring
        score = regressor.score(X_test, y_test)
        assert -1.0 <= score <= 1.0  # R2 score can be negative for bad fits
