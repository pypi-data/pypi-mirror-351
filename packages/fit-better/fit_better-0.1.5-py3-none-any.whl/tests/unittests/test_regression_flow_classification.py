"""
Unit tests for RegressionFlow with classification tasks.

This test suite validates:
- Using RegressionFlow with LogisticRegression for classification
- Input validation for classification data
- Finding best strategies for binary and multiclass problems
- Integration between RegressorType.LOGISTIC and RegressionFlow
"""

import os
import sys
import pytest
import numpy as np

from fit_better import RegressionFlow, PartitionMode, RegressorType, Metric


@pytest.fixture
def binary_classification_data():
    """Create a binary classification dataset for testing."""
    np.random.seed(42)
    n_samples = 200
    X = np.random.rand(n_samples, 2) * 10  # 2 features

    # Create a linear decision boundary: 2*x1 - x2 + 3 > 0
    boundary = 2 * X[:, 0] - X[:, 1] + 3
    y = (boundary > 0).astype(int)

    # Add some noise
    noise_idx = np.random.choice(n_samples, int(0.1 * n_samples), replace=False)
    y[noise_idx] = 1 - y[noise_idx]  # Flip labels for noise points

    # Split into train and test
    split_idx = int(0.8 * n_samples)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    return X_train, y_train, X_test, y_test


@pytest.fixture
def multiclass_classification_data():
    """Create a multiclass classification dataset for testing."""
    from sklearn.datasets import make_classification

    # Create a multiclass dataset with 3 classes
    X, y = make_classification(
        n_samples=200,
        n_features=4,
        n_informative=3,
        n_redundant=0,
        n_classes=3,
        random_state=42,
    )

    # Split into train and test
    split_idx = 160
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    return X_train, y_train, X_test, y_test


@pytest.mark.unit
class TestRegressionFlowClassification:
    """Test RegressionFlow with classification tasks."""

    def test_binary_classification(self, binary_classification_data):
        """Test using RegressionFlow for binary classification."""
        X_train, y_train, X_test, y_test = binary_classification_data

        # Initialize flow
        flow = RegressionFlow()

        # Find best strategy with logistic regression
        result = flow.find_best_strategy(
            X_train,
            y_train,
            X_test,
            y_test,
            regressor_types=[RegressorType.LOGISTIC],
            partition_modes=[
                PartitionMode.NONE
            ],  # Start with no partitioning for simplicity
            n_jobs=1,
        )

        # Check result fields
        assert result is not None, "Result should not be None"
        assert (
            result.model_type == RegressorType.LOGISTIC
        ), "Model type should be LOGISTIC"
        assert hasattr(result, "metrics"), "Result should have metrics attribute"

        # Make predictions
        predictions = flow.predict(X_test)
        assert len(predictions) == len(
            y_test
        ), "Predictions length should match test data"

        # Calculate accuracy
        accuracy = np.mean(predictions.round() == y_test)
        assert accuracy >= 0.7, f"Accuracy should be >= 0.7, got {accuracy}"

    def test_multiclass_classification(self, multiclass_classification_data):
        """Test using RegressionFlow for multiclass classification."""
        X_train, y_train, X_test, y_test = multiclass_classification_data

        # Initialize flow
        flow = RegressionFlow()

        # Find best strategy with logistic regression
        result = flow.find_best_strategy(
            X_train,
            y_train,
            X_test,
            y_test,
            regressor_types=[RegressorType.LOGISTIC],
            partition_modes=[PartitionMode.NONE],  # Start with no partitioning
            n_jobs=1,
        )

        # Check result fields
        assert result is not None, "Result should not be None"
        assert (
            result.model_type == RegressorType.LOGISTIC
        ), "Model type should be LOGISTIC"
        assert hasattr(result, "metrics"), "Result should have metrics attribute"

        # Make predictions
        predictions = flow.predict(X_test)
        assert len(predictions) == len(
            y_test
        ), "Predictions length should match test data"

        # Check predictions are in the expected range of classes (0, 1, 2)
        unique_classes = np.unique(predictions.round().astype(int))
        for cls in range(3):
            assert cls in unique_classes, f"Class {cls} should be in predictions"

    def test_partitioned_classification(self, binary_classification_data):
        """Test using partitioning with classification tasks."""
        X_train, y_train, X_test, y_test = binary_classification_data

        # Initialize flow
        flow = RegressionFlow()

        # Find best strategy with logistic regression and partitioning
        result = flow.find_best_strategy(
            X_train,
            y_train,
            X_test,
            y_test,
            regressor_types=[RegressorType.LOGISTIC],
            partition_modes=[PartitionMode.KMEANS],
            n_partitions=3,
            n_jobs=1,
        )

        # Check result fields
        assert result is not None, "Result should not be None"
        assert (
            result.model_type == RegressorType.LOGISTIC
        ), "Model type should be LOGISTIC"
        assert hasattr(
            result, "partition_mode"
        ), "Result should have partition_mode attribute"

        # Make predictions
        predictions = flow.predict(X_test)
        assert len(predictions) == len(
            y_test
        ), "Predictions length should match test data"

        # Calculate accuracy
        accuracy = np.mean((predictions > 0.5) == y_test)
        assert accuracy > 0.6, f"Accuracy should be > 0.6, got {accuracy}"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
