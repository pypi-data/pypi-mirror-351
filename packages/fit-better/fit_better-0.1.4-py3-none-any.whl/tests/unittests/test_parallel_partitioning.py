"""
Tests for parallel partitioning functionality.
"""

import os
import pytest
import numpy as np
from fit_better.core.models import RegressorType, Metric
from fit_better.core.partitioning import (
    PartitionMode,
    train_models_on_partitions,
    predict_with_partitioned_models,
)
from partition_algorithm_finder_example import load_dataset

pytestmark = [pytest.mark.parallel, pytest.mark.unit]


@pytest.fixture
def parallel_test_data(test_data_dir):
    """Load sample dataset for parallel testing."""
    X_train, y_train, X_test, y_test = load_dataset("linear", test_data_dir)
    return X_train, y_train, X_test, y_test


def test_load_dataset(test_data_dir):
    """Test dataset loading functionality."""
    X_train, y_train, X_test, y_test = load_dataset("linear", test_data_dir)

    # Test data shapes and types
    assert isinstance(X_train, np.ndarray), "X_train should be numpy array"
    assert isinstance(y_train, np.ndarray), "y_train should be numpy array"
    assert X_train.shape[0] == y_train.shape[0], "Training data size mismatch"
    assert X_test.shape[0] == y_test.shape[0], "Test data size mismatch"


@pytest.mark.parametrize("n_jobs", [1, 2])
def test_parallel_training(parallel_test_data, n_jobs):
    """Test parallel training with different numbers of jobs."""
    X_train, y_train, X_test, y_test = parallel_test_data

    # Train with different n_jobs values
    models = train_models_on_partitions(
        X_train,
        y_train,
        n_partitions=3,
        n_jobs=n_jobs,
        partition_mode=PartitionMode.RANGE,
        regressor_type=RegressorType.LINEAR,
        test_compatibility_mode=True,
    )

    # Check if model was trained successfully
    assert isinstance(models, list), "Result should be a list of models"
    assert len(models) > 0, "No models in result"

    # Test predictions
    model = models[0]["model"]
    if X_test.ndim == 1:
        X_test = X_test.reshape(-1, 1)

    y_pred = model.predict(X_test[:5].reshape(-1, 1))  # Test on a few samples
    assert y_pred.shape[0] == 5, "Wrong prediction shape"
    assert np.all(np.isfinite(y_pred)), "Predictions should be finite"


@pytest.mark.parametrize("n_partitions", [2, 3, 5])
def test_partition_counts(parallel_test_data, n_partitions):
    """Test different numbers of partitions."""
    X_train, y_train, X_test, y_test = parallel_test_data

    # Train with different partition counts
    models = train_models_on_partitions(
        X_train,
        y_train,
        n_partitions=n_partitions,
        n_jobs=1,
        partition_mode=PartitionMode.RANGE,
        regressor_type=RegressorType.LINEAR,
        test_compatibility_mode=True,
    )

    # Test number of models matches partitions
    assert isinstance(models, list), "Result should be a list of models"
    assert len(models) == n_partitions, f"Expected {n_partitions} models"

    # Test predictions from each model
    for model_data in models:
        model = model_data["model"]
        if X_test.ndim == 1:
            X_test = X_test.reshape(-1, 1)

        y_pred = model.predict(X_test.reshape(-1, 1))
        assert y_pred.shape[0] == y_test.shape[0], "Wrong prediction shape"


def test_prediction_evaluation(parallel_test_data):
    """Test prediction evaluation metrics."""
    X_train, y_train, X_test, y_test = parallel_test_data

    # Train models
    models = train_models_on_partitions(
        X_train,
        y_train,
        n_partitions=3,
        n_jobs=1,
        partition_mode=PartitionMode.RANGE,
        regressor_type=RegressorType.LINEAR,
        test_compatibility_mode=True,
    )

    # Check models
    assert isinstance(models, list), "Result should be a list of models"
    assert len(models) > 0, "No models in result"

    # Check that models have the expected structure
    for model_data in models:
        assert "model" in model_data, "Model object missing from model data"
        assert "stats" in model_data, "Stats missing from model data"
        assert "mae" in model_data["stats"], "MAE missing from stats"
        assert "n_samples" in model_data, "Sample count missing from model data"

    # Verify model works
    for model_data in models:
        model = model_data["model"]
        if X_test.ndim == 1:
            X_test = X_test.reshape(-1, 1)

        y_pred = model.predict(X_test.reshape(-1, 1))
        assert y_pred.shape[0] == y_test.shape[0]
        assert np.all(np.isfinite(y_pred))


@pytest.mark.parametrize(
    "regressor_type",
    [
        RegressorType.LINEAR,
        RegressorType.SVR_RBF,
    ],
)
def test_regressor_types(parallel_test_data, regressor_type):
    """Test different regressor types in parallel."""
    X_train, y_train, X_test, y_test = parallel_test_data

    # Train with different regressor types
    models = train_models_on_partitions(
        X_train,
        y_train,
        n_partitions=2,
        n_jobs=1,
        partition_mode=PartitionMode.RANGE,
        regressor_type=regressor_type,
        test_compatibility_mode=True,
    )

    # Test models
    assert isinstance(models, list), "Result should be a list of models"
    assert len(models) == 2, "Should have 2 models"
    for model_data in models:
        model = model_data["model"]
        if X_test.ndim == 1:
            X_test = X_test.reshape(-1, 1)

        y_pred = model.predict(X_test.reshape(-1, 1))
        assert y_pred.shape[0] == y_test.shape[0]
        assert np.all(np.isfinite(y_pred))
