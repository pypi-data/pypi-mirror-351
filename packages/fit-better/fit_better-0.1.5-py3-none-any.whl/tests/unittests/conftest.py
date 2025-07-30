"""
Fixtures for unit tests.

This module provides common test fixtures for unit tests in the fit_better package.
These fixtures ensure consistency across tests and reduce code duplication.

Key fixtures include:
- test_data_dir: Path to test data files
- visualization_dir: Temporary directory for test visualizations
- sample_data: Generated synthetic data for testing

The module also registers pytest markers to categorize tests.
"""

import os
import sys
import pytest
import numpy as np

# Add the usages directory to sys.path for imports
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "usages"),
)


# Register all custom marks used in tests
def pytest_configure(config):
    """
    Register custom pytest markers.

    This function registers the following markers:
    - unit: mark a test as a unit test
    - parallel: mark a test that tests parallel functionality
    - data: mark a test related to data handling
    - slow: mark a test as slow-running

    These markers can be used to run specific categories of tests:
    python -m pytest -m "parallel" tests/unittests/
    """
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line(
        "markers", "parallel: mark a test of parallel functionality"
    )
    config.addinivalue_line("markers", "data: mark a test related to data handling")
    config.addinivalue_line("markers", "slow: mark a test as slow-running")


@pytest.fixture
def test_data_dir():
    """
    Return the path to the test data directory.

    This fixture provides a consistent path to the test data directory,
    ensuring all tests use the same data location. The path is calculated
    relative to the test module location, making it robust against
    changes in the working directory.

    Returns:
        str: Path to the directory containing test data files
    """
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(tests_dir, "data_gen", "data")


@pytest.fixture
def visualization_dir(tmpdir):
    """
    Create and return a temporary directory for test visualizations.

    This fixture creates a temporary directory for storing visualizations
    generated during tests. This avoids polluting the real visualization
    directory during testing and ensures each test run has a clean slate.

    Args:
        tmpdir: pytest's built-in fixture for temporary directories

    Returns:
        str: Path to the temporary visualization directory
    """
    vis_dir = os.path.join(tmpdir, "data_gen", "visualization_results")
    os.makedirs(vis_dir, exist_ok=True)
    return vis_dir


@pytest.fixture
def sample_data():
    """
    Generate a small synthetic dataset for testing.

    This fixture creates a synthetic dataset with deterministic values
    to ensure consistent test results. The dataset consists of X values
    and corresponding y values with some controlled noise.

    Returns:
        tuple: (X, y) numpy arrays containing the synthetic dataset
    """
    # Use a fixed seed for reproducible tests
    np.random.seed(42)

    # Generate a small sample for fast test execution
    n_samples = 100
    X = np.linspace(0, 10, n_samples).reshape(-1, 1)
    y = 2 * X.flatten() + 3 + np.random.normal(0, 0.5, n_samples)

    return X, y
