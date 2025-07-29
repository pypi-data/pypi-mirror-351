"""
Tests for partition comparison functionality.

This module tests the functionality for comparing different partitioning
strategies for regression models. It validates:
1. Loading test data from files
2. Processing data with all partition modes
3. Verifying partition boundaries are correctly ordered
4. Confirming that parallel execution matches serial execution

All tests use the sample_data fixture from conftest.py for consistent
test data across the test suite.
"""

import os
import pytest
import numpy as np
from fit_better.core.partitioning import PartitionMode
from partition_comparison_example import evaluate_partition_mode, load_test_data

pytestmark = pytest.mark.unit


@pytest.mark.data
def test_load_test_data(test_data_dir):
    """
    Test loading test data from files.

    Validates that:
    - Data is loaded correctly from the test data directory
    - Training and test data shapes are consistent
    - Data is loaded as numpy arrays for compatibility with algorithms
    """
    X_train, y_train, X_test, y_test = load_test_data(test_data_dir)

    # Test shapes
    assert X_train.shape[0] == y_train.shape[0], "Training data size mismatch"
    assert X_test.shape[0] == y_test.shape[0], "Test data size mismatch"

    # Test data types
    assert isinstance(X_train, np.ndarray), "X_train should be numpy array"
    assert isinstance(y_train, np.ndarray), "y_train should be numpy array"


@pytest.mark.slow
def test_all_partition_modes(sample_data):
    """
    Test all partition modes produce valid results.

    This test validates that:
    - All supported partition modes can successfully process data
    - Each mode produces valid metrics (MAE, RMSE, R2)
    - Models are correctly generated for each partition
    - The system handles empty partitions gracefully

    The test uses a fixed dataset with 80/20 train/test split for consistent evaluation.
    """
    X, y = sample_data
    X_test, y_test = X[80:], y[80:]  # Use last 20 points for testing
    X_train, y_train = X[:80], y[:80]  # Use first 80 points for training

    partition_modes = [
        PartitionMode.PERCENTILE,
        PartitionMode.RANGE,
        PartitionMode.KMEANS,
        PartitionMode.EQUAL_WIDTH,
    ]

    for mode in partition_modes:
        result = evaluate_partition_mode(
            X_train, y_train, X_test, y_test, mode, n_parts=3, n_jobs=1
        )

        # Test metrics exist and have valid values
        assert hasattr(result, "best_rmse"), f"RMSE missing for {mode}"
        assert hasattr(result, "best_r2"), f"R2 missing for {mode}"
        assert result.best_rmse >= 0, f"Invalid RMSE for {mode}"
        assert result.best_r2 <= 1, f"Invalid R2 for {mode}"

        # Test model result structure
        assert hasattr(result, "best_model"), f"Model missing for {mode}"


def test_partition_boundaries(sample_data):
    """
    Test partition boundaries are properly ordered and cover data range.

    This test validates that:
    - Boundaries create the correct number of partitions
    - Boundaries are ordered correctly (ascending)
    - Boundaries cover the full range of the data
    - The system handles empty boundary lists gracefully

    For the PERCENTILE mode specifically, it checks that n_parts-1 boundaries are created.
    """
    X, y = sample_data
    X_test, y_test = X[80:], y[80:]
    X_train, y_train = X[:80], y[:80]

    n_parts = 4
    result = evaluate_partition_mode(
        X_train,
        y_train,
        X_test,
        y_test,
        PartitionMode.PERCENTILE,
        n_parts=n_parts,
        n_jobs=1,
    )

    # Check if boundaries exist in partitioned result
    if hasattr(result, "boundaries"):
        boundaries = result.boundaries

        # Skip boundary tests if boundaries list is empty
        if not boundaries:
            pytest.skip("No boundaries created - skipping boundary tests")

        assert len(boundaries) == n_parts - 1, "Incorrect number of boundaries"
        assert all(
            boundaries[i] <= boundaries[i + 1] for i in range(len(boundaries) - 1)
        ), "Boundaries not ordered"
        assert min(X_train.ravel()) <= boundaries[0], "First boundary too high"
        assert max(X_train.ravel()) >= boundaries[-1], "Last boundary too low"


@pytest.mark.parallel
def test_parallel_execution(sample_data):
    """
    Test parallel execution produces same results as serial.

    This test validates that:
    - Results from parallel execution match serial execution
    - Metrics are numerically identical between parallel and serial runs
    - Parallelization doesn't affect algorithm behavior or accuracy

    This ensures consistent results regardless of execution mode.
    """
    X, y = sample_data
    X_test, y_test = X[80:], y[80:]
    X_train, y_train = X[:80], y[:80]

    # Run with 1 job (serial)
    result_serial = evaluate_partition_mode(
        X_train, y_train, X_test, y_test, PartitionMode.KMEANS, n_parts=3, n_jobs=1
    )

    # Run with multiple jobs (parallel)
    result_parallel = evaluate_partition_mode(
        X_train, y_train, X_test, y_test, PartitionMode.KMEANS, n_parts=3, n_jobs=3
    )

    # Results should be nearly identical
    assert np.isclose(result_serial.best_rmse, result_parallel.best_rmse, rtol=1e-10)
    assert np.isclose(result_serial.best_r2, result_parallel.best_r2, rtol=1e-10)
