"""
Unit tests for finding best partition and algorithm.

This module tests:
- Loading test datasets
- Evaluating partition modes
- Partitioning with different numbers of parts
- Evaluating regressor types
- Using multiple datasets
"""

import os
import pytest
import numpy as np
from tests.usages.partition_algorithm_finder_example import (
    find_best_partition_and_algo,
    load_dataset,
    evaluate_partition_mode,
    _test_regressor_types,
    find_best_partition_algorithm_combination,
)
from fit_better.core.models import RegressorType, Metric
from fit_better.core.partitioning import PartitionMode

pytestmark = pytest.mark.unit


def test_load_dataset(test_data_dir):
    """Test loading a dataset from files."""
    X_train, y_train, X_test, y_test = load_dataset("linear", test_data_dir)

    # Test data shapes and types
    assert isinstance(X_train, np.ndarray), "X_train should be numpy array"
    assert isinstance(y_train, np.ndarray), "y_train should be numpy array"
    assert X_train.shape[0] == y_train.shape[0], "Training data size mismatch"
    assert X_test.shape[0] == y_test.shape[0], "Test data size mismatch"

    # Test data validity
    assert np.all(np.isfinite(X_train)), "Training features should be finite"
    assert np.all(np.isfinite(y_train)), "Training labels should be finite"
    assert np.all(np.isfinite(X_test)), "Test features should be finite"
    assert np.all(np.isfinite(y_test)), "Test labels should be finite"


@pytest.mark.parametrize(
    "partition_mode",
    [
        PartitionMode.PERCENTILE,
        PartitionMode.RANGE,
        PartitionMode.KMEANS,
    ],
)
def test_evaluate_partition_mode(partition_mode):
    """Test evaluating individual partition modes."""
    X_train, y_train, X_test, y_test = load_dataset()

    # Test single partition mode evaluation
    result = find_best_partition_algorithm_combination(
        X_train,
        y_train,
        X_test,
        y_test,
        n_jobs=1,
        output_dir=None,
        partition_modes=[partition_mode],
        regressor_types=[RegressorType.LINEAR],
        partition_counts=[3],
    )

    # Check result structure
    assert isinstance(result, dict), "Result should be a dictionary"
    assert (
        "best_strategy" in result or "metrics" in result
    ), "Result should have metrics field"


@pytest.mark.parametrize("n_partitions", [2, 3, 5])
def test_partition_counts(n_partitions):
    """Test evaluating different partition counts."""
    X_train, y_train, X_test, y_test = load_dataset()

    # Test single partition count
    result = find_best_partition_algorithm_combination(
        X_train,
        y_train,
        X_test,
        y_test,
        n_jobs=1,
        output_dir=None,
        partition_modes=[PartitionMode.RANGE],
        regressor_types=[RegressorType.LINEAR],
        partition_counts=[n_partitions],
    )

    # Check basic result structure
    assert isinstance(result, dict), "Result should be a dictionary"

    # Check that some result was found, without requiring a specific n_partitions
    # Since the algorithm may fall back to a global model
    assert (
        "best_strategy" in result or "metrics" in result
    ), "Result should contain metrics or strategy"


def test_regressor_evaluation(test_data_dir):
    """Test regressor type evaluation."""
    X_train, y_train, X_test, y_test = load_dataset("linear", test_data_dir)

    results = _test_regressor_types(
        X_train,
        y_train,
        X_test,
        y_test,
        regressor_types=[RegressorType.LINEAR, RegressorType.SVR_RBF],
        n_jobs=1,
    )

    # Test results
    assert isinstance(results, dict), "Results should be a dict"
    assert len(results) > 0, "Results should have data"
    # Check that there are metric results for each regressor
    for regressor_type in [RegressorType.LINEAR, RegressorType.SVR_RBF]:
        assert regressor_type in results, f"Missing results for {regressor_type}"
        assert "metrics" in results[regressor_type], "Missing metrics in results"


@pytest.mark.parametrize("dataset_prefix", ["linear", "sine"])
def test_multiple_datasets(test_data_dir, dataset_prefix):
    """Test evaluation across different datasets."""
    X_train, y_train, X_test, y_test = load_dataset(dataset_prefix, test_data_dir)

    results = _test_regressor_types(
        X_train,
        y_train,
        X_test,
        y_test,
        regressor_types=[RegressorType.LINEAR, RegressorType.SVR_RBF],
        n_jobs=1,
    )

    # Check results for each dataset
    assert isinstance(results, dict), "Results should be dict"
    # Check for results for each regressor
    for regressor_type in [RegressorType.LINEAR, RegressorType.SVR_RBF]:
        assert regressor_type in results, f"Missing results for {regressor_type}"
        assert "metrics" in results[regressor_type], "Missing metrics in results"
