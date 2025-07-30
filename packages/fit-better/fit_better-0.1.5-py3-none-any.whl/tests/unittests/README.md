# Unit Tests Documentation

This directory contains all unit tests for the fit-better package. These tests ensure that individual components of the package work correctly in isolation.

## Overview

The unit tests are organized by module and functionality, using the pytest framework. Each test file corresponds to a specific aspect of the fit-better package.

## Test Files

| Test File | Description |
|-----------|-------------|
| `test_io_export.py` | Tests for model export and serialization functionality |
| `test_synthetic_data.py` | Tests for synthetic data generation utilities |
| `test_model_io.py` | Tests for model saving, loading, and versioning |
| `test_compare_regressors.py` | Tests for regression algorithm comparison utilities |
| `test_parallel_partitioning.py` | Tests for parallel processing in partitioning algorithms |
| `test_find_best_partition_and_algo.py` | Tests for the automatic strategy finder |
| `test_partition_utils.py` | Tests for data partitioning utilities |
| `test_compare_partitions.py` | Tests for partition strategy comparison utilities |
| `test_visualization_utils.py` | Tests for visualization components |
| `test_csv_operations.py` | Tests for CSV file operations |
| `test_regression_flow.py` | Tests for the main RegressionFlow class |
| `test_csv_manager.py` | Tests for the CSVManager utility |
| `test_plotting_utils.py` | Tests for plotting utilities |
| `test_data_preprocessing.py` | Tests for data preprocessing components |
| `test_model_utils.py` | Tests for model utility functions |

## Running Tests

To run all unit tests:

```bash
cd tests
pytest unittests
```

To run a specific test file:

```bash
cd tests
pytest unittests/test_regression_flow.py
```

To run tests with verbose output:

```bash
cd tests
pytest unittests -v
```

## Code Coverage

The test suite is designed to maximize code coverage for the fit-better package. Each test focuses on specific functionality to ensure robust error handling and correct behavior under various conditions.

## Test Fixtures

Common test fixtures are defined in `conftest.py`, which provides:

- Sample data for testing
- Commonly used model instances
- Helper functions for test setup and teardown
- Temporary file and directory management

## Adding New Tests

When adding new functionality to the fit-better package:

1. Create a new test file if it's a new module or a significant feature
2. Follow the naming convention: `test_[module_name].py`
3. Use pytest fixtures when possible to minimize code duplication
4. Test both normal operation and error handling cases
5. Ensure all public API functions are covered by tests 