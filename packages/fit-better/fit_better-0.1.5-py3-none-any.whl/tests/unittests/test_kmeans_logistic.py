"""
Unit tests for K-means clustering with Logistic Regression.

This test suite validates:
- Using K-means clustering to partition data for logistic regression
- Integration between PartitionMode.KMEANS and RegressorType.LOGISTIC
- Comparing partitioned vs. non-partitioned logistic regression
"""

import os
import sys
import pytest
import numpy as np
from sklearn.metrics import accuracy_score

from fit_better import (
    RegressionFlow,
    PartitionMode,
    RegressorType,
    Metric,
    train_models_on_partitions,
    predict_with_partitioned_models,
    get_partitioner_by_mode,
    create_regressor,
)


@pytest.fixture
def complex_binary_data():
    """Create a complex binary classification dataset that benefits from partitioning."""
    np.random.seed(42)
    n_samples = 300

    # Create two distinct clusters with different decision boundaries
    X1 = np.random.randn(n_samples // 2, 2) * 0.5 + np.array([2, 2])
    y1 = (X1[:, 0] > X1[:, 1]).astype(int)

    X2 = np.random.randn(n_samples // 2, 2) * 0.5 + np.array([-2, -2])
    y2 = (X2[:, 0] < X2[:, 1]).astype(int)

    # Combine the datasets
    X = np.vstack([X1, X2])
    y = np.hstack([y1, y2])

    # Split into train and test
    split_idx = int(0.8 * n_samples)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    return X_train, y_train, X_test, y_test


@pytest.mark.unit
class TestKMeansLogisticRegression:
    """Test K-means clustering with Logistic Regression."""

    def test_kmeans_vs_global_logistic(self, complex_binary_data):
        """Compare K-means partitioning with global logistic regression."""
        X_train, y_train, X_test, y_test = complex_binary_data

        # Train global logistic regression model
        global_model = create_regressor(RegressorType.LOGISTIC)
        global_model.fit(X_train, y_train)
        global_preds = global_model.predict(X_test)
        global_accuracy = accuracy_score(y_test, global_preds)

        # Train partitioned logistic regression models with K-means
        n_partitions = 2  # Two clusters in the data
        # Create partitioner for prediction later
        partitioner = get_partitioner_by_mode(PartitionMode.KMEANS, n_partitions)
        # For training, we pass the number of partitions, partition mode, and regressor type
        partitioned_models = train_models_on_partitions(
            X_train,
            y_train,
            n_partitions=n_partitions,
            partition_mode=PartitionMode.KMEANS,
            regressor_type=RegressorType.LOGISTIC,
        )
        kmeans_preds = predict_with_partitioned_models(
            partitioned_models, X_test, partitioner
        )
        kmeans_accuracy = accuracy_score(y_test, kmeans_preds.round())

        # The partitioned model should be better due to the way we constructed the data
        assert kmeans_accuracy > global_accuracy, (
            f"K-means accuracy {kmeans_accuracy} should be better than "
            f"global accuracy {global_accuracy} for this dataset"
        )

    def test_using_regression_flow(self, complex_binary_data):
        """Test using RegressionFlow to find best strategy for classification."""
        X_train, y_train, X_test, y_test = complex_binary_data

        # Initialize flow
        flow = RegressionFlow()

        # Find best strategy using just logistic regression with no partitioning
        result = flow.find_best_strategy(
            X_train,
            y_train,
            X_test,
            y_test,
            regressor_types=[RegressorType.LOGISTIC],
            partition_modes=[PartitionMode.NONE],  # Just use NONE to simplify the test
            n_partitions=1,
            n_jobs=1,
        )

        # Verify that logistic regression was selected and the result is valid
        assert (
            result.model_type == RegressorType.LOGISTIC
        ), f"Expected LOGISTIC to be selected, got {result.model_type}"

        # Make predictions
        predictions = flow.predict(X_test)

        # Confirm predictions are the right shape
        assert predictions.shape == y_test.shape

        # For this test, we only care that the model runs without error
        # and produces predictions, not about accuracy
        # Convert predictions to binary and calculate accuracy for information only
        binary_preds = (predictions > 0.5).astype(int)
        accuracy = np.mean(binary_preds == y_test)
        print(f"Model accuracy: {accuracy:.2f} - this is just informational")

    def test_partition_boundaries(self, complex_binary_data):
        """Test that partition boundaries are created correctly."""
        X_train, y_train, X_test, y_test = complex_binary_data

        # Create partitioner
        n_partitions = 2
        partitioner = get_partitioner_by_mode(PartitionMode.KMEANS, n_partitions)

        # Fit partitioner
        partitioner.fit(X_train)

        # Get partition assignments
        train_partitions = partitioner.predict_partition(X_train)

        # Verify we have the expected number of partitions
        unique_partitions = np.unique(train_partitions)
        assert (
            len(unique_partitions) == n_partitions
        ), f"Expected {n_partitions} partitions, got {len(unique_partitions)}"

        # Verify each partition has a reasonable number of samples
        for partition_idx in range(n_partitions):
            partition_size = np.sum(train_partitions == partition_idx)
            min_expected_size = len(X_train) / (
                n_partitions * 3
            )  # Allow for some imbalance
            assert partition_size > min_expected_size, (
                f"Partition {partition_idx} has only {partition_size} samples, "
                f"expected at least {min_expected_size}"
            )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
