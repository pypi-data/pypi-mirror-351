# Test Suite Organization

This directory contains the pytest-based test suite for evaluating regression models and partitioning strategies.

## Import Structure

Tests have been updated to use the new simplified import structure from the `fit_better` package. Instead of importing from submodules directly, most functionality is now accessible directly from the main package:

```python
# Old import structure
from fit_better.core.partitioning import PartitionMode
from fit_better.core.models import RegressorType
from fit_better.core.regression import RegressionFlow

# New import structure 
from fit_better import PartitionMode, RegressorType, RegressionFlow
```

This makes the code cleaner and more maintainable. Some specialized utilities that are not part of the main API are still imported from their specific submodules.

## Directory Structure

```
tests/
├── conftest.py          # Common test fixtures
├── pytest.ini          # Pytest configuration
├── custom/             # Original script modules used by tests
│   ├── __init__.py
│   ├── compare_partitions.py
│   ├── compare_regressors.py
│   ├── find_best_partition_and_algo.py
│   ├── generate_test_data.py
│   ├── parallel_partitioning.py
│   └── test_cpp_deployment.py
├── unittests/          # Unit tests for components
│   ├── __init__.py
│   ├── test_compare_partitions.py
│   ├── test_compare_regressors.py
│   ├── test_find_best_partition_and_algo.py
│   ├── test_generate_test_data.py
│   ├── test_parallel_partitioning.py
│   └── test_partition_utils.py
├── test_all.py         # Integration test
└── data_gen/           # Generated data and results
    ├── data/           # Test data files
    └── logs/           # Test execution logs
```

## Generated Results Structure

```
tests/
└── data_gen/                # Generated data and results directory
    ├── logs/               # Central location for all test logs
    │   ├── partition_comparison.log  # Latest partition comparison log
    │   ├── regressor_comparison.log # Latest regressor comparison log
    │   └── find_best_algo.log      # Latest algorithm finder log
    ├── data/              # Additional test datasets
    ├── partition_results/  # Partition comparison results
    ├── regressor_results/ # Regressor comparison results
    ├── archived_results/  # Historical test results
    └── visualization_results/ # Generated plots and visualizations
        ├── partitions/    # Partition comparison plots
        ├── regressors/    # Regressor comparison plots
        ├── parallel/      # Parallel processing test plots
        └── algorithms/    # Algorithm finder plots
```

## Generated Visualizations

When `--visualize` is enabled, generated plots include:

- Performance comparison plots
- Predictions vs actual values
- Error distributions
- Detailed regression reports

All visualizations are saved to the specified `--output-dir` under the `data_gen/visualization_results/` directory.

## Test Scripts

### test_all.py

The main test runner that executes all registered regression tests and validates their output.

**Usage:**

```bash
python test_all.py [--test TEST_NAME] [--timeout SECONDS] [--verbose]
```

**Options:**

- `--test TEST_NAME`: Run only the specified test (e.g., 'compare_partitions')
- `--timeout SECONDS`: Set custom timeout for tests (default: 300 seconds)
- `--verbose`: Show detailed output during test execution

**Example:**

```bash
python test_all.py --verbose
python test_all.py --test compare_regressors --timeout 600
```

### compare_partitions.py

Compares different data partitioning strategies for regression models.

**Usage:**

```bash
python compare_partitions.py [--parts N] [--visualize] [--output-dir DIR]
```

**Options:**

- `--parts N`: Number of partitions to use (default: 10)
- `--visualize`: Generate visualization plots
- `--output-dir DIR`: Directory to save visualization results (default: 'data_gen/partition_results')

**Example:**

```bash
python compare_partitions.py --parts 5 --visualize
```

### compare_regressors.py

Compares different regression model types.

**Usage:**

```bash
python compare_regressors.py [--visualize] [--output-dir DIR] [--n-jobs N]
```

**Options:**

- `--visualize`: Generate visualization plots
- `--output-dir DIR`: Directory to save visualization results (default: 'data_gen/regressor_results')
- `--n-jobs N`: Number of parallel jobs for model fitting (default: 1)

**Example:**

```bash
python compare_regressors.py --visualize --n-jobs 3
```

### find_best_partition_and_algo.py

Analyzes multiple datasets to find the best regression algorithm using KMeans partitioning.

**Usage:**

```bash
python find_best_partition_and_algo.py [--visualize]
```

**Features:**

- Tests multiple datasets (linear, sine wave, polynomial, complex)
- Uses KMeans partitioning with k=10
- Evaluates various regression algorithms
- Identifies best performing algorithm across all datasets

**Data Files:**
The script uses standardized data files in the `data_gen/data/` directory:

- `linear_X.txt`, `linear_y.txt` (training) and `linear_X_test.txt`, `linear_y_test.txt` (testing)
- `sine_X.txt`, `sine_y.txt` (training) and `sine_X_test.txt`, `sine_y_test.txt` (testing)
- `polynomial_X.txt`, `polynomial_y.txt` (training) and `polynomial_X_test.txt`, `polynomial_y_test.txt` (testing)
- `complex_X.txt`, `complex_y.txt` (training) and `complex_X_test.txt`, `complex_y_test.txt` (testing)

Missing data files are automatically generated with synthetic test data.

### parallel_partitioning.py

Tests the parallel processing capabilities of the partition utilities.

**Usage:**

```bash
python parallel_partitioning.py [--n-jobs N] [--n-samples N]
```

**Features:**

- Tests parallel processing in:
  - KNeighborsRegressor with adaptive n_neighbors
  - KMeans clustering
  - KMedoids clustering
  - Full model training with different partition modes
- Measures execution times for performance comparison
- Uses synthetic test data for consistent evaluation

**Options:**

- `--n-jobs N`: Number of parallel jobs (default: 3)
- `--n-samples N`: Number of test samples to generate (default: 1000)

### test_cpp_deployment.py

Tests the C++ deployment capabilities of the fit-better package.

**Usage:**

```bash
python test_cpp_deployment.py [--model-type MODEL_TYPE] [--output-dir DIR]
```

**Features:**

- Trains models in Python
- Exports models to JSON format
- Runs C++ unit tests to validate model loading and prediction
- Compares Python and C++ prediction results for consistency
- Measures prediction performance in both languages

**Options:**

- `--model-type MODEL_TYPE`: Type of model to test (default: 'linear')
- `--output-dir DIR`: Directory to save test results (default: 'data_gen/cpp_deployment')

## Visualization

Visualizations are handled by the `fit_better.plot_utils` module, which provides functions for creating performance comparisons, prediction vs. actual plots, and error distributions. The main visualization functions include:

- `plot_versus`: Creates scatter plots for comparing two sets of data
- `plot_performance_comparison`: Creates bar charts for comparing model performance metrics
- `plot_predictions_vs_actual`: Creates scatter plots of predicted vs actual values
- `plot_error_distribution`: Creates histograms of prediction errors
- `create_regression_report_plots`: Creates a comprehensive set of visualization plots for a regression model

## Test Data

The `data_gen/test_data/` directory contains sample data files for testing:

- `X.txt`: Training features
- `y.txt`: Training targets
- `X_new.txt`: Test features
- `y_new.txt`: Test targets

## Using the Framework

The recommended workflow is to:

1. Run individual comparison tests with visualization:

   ```bash
   python compare_partitions.py --visualize
   python compare_regressors.py --visualize
   ```

2. Run the full test suite to validate all components:

   ```bash
   python test_all.py
   ```

3. Clean up generated data (optional):

   ```bash
   ./run_all_tests.sh --cleanup
   ```

## Utility Modules

The `tests/utils/` directory contains utility modules that provide reusable functions to reduce code duplication across test scripts:

### argparse_utils.py

Provides standardized argument parsing functionality for test scripts:

```python
from tests.utils import get_default_parser, add_io_args, add_model_args

# Get a default parser with all standard argument groups
parser = get_default_parser(description="My test script")

# Or create a custom parser with specific argument groups
parser = argparse.ArgumentParser(description="My custom test script")
add_io_args(parser)
add_model_args(parser)
```

Main functions:
- `get_default_parser()`: Creates a parser with all standard argument groups
- `add_io_args()`: Adds input/output file arguments
- `add_model_args()`: Adds model parameter arguments
- `add_output_args()`: Adds output directory arguments
- `add_preprocessing_args()`: Adds data preprocessing arguments
- `add_logging_args()`: Adds logging configuration arguments

### data_utils.py

Provides utilities for loading and generating data:

```python
from tests.utils import load_test_data, generate_synthetic_data

# Load data from files or generate if not available
X_train, y_train, X_test, y_test = load_test_data(args)

# Generate synthetic data with custom parameters
X_train, y_train, X_test, y_test = generate_synthetic_data(
    n_samples_train=1000,
    n_samples_test=200,
    n_features=5
)
```

Main functions:
- `load_test_data()`: Loads data from files or generates synthetic data if not available
- `generate_synthetic_data()`: Generates synthetic data with customizable parameters
- `save_data_multiple_formats()`: Saves data in multiple formats (CSV, NPY)

### eval_utils.py

Provides model evaluation utilities:

```python
from tests.utils import evaluate_model, evaluate_multiple_configurations

# Evaluate a single model configuration
results = evaluate_model(
    X_train, y_train, X_test, y_test,
    partition_mode=PartitionMode.KMEANS,
    n_partitions=5,
    regressor_type=RegressorType.RANDOM_FOREST
)

# Evaluate multiple configurations and find the best
results = evaluate_multiple_configurations(
    X_train, y_train, X_test, y_test,
    partition_modes=[PartitionMode.KMEANS, PartitionMode.RANGE],
    regressor_types=[RegressorType.LINEAR, RegressorType.RANDOM_FOREST],
    partition_counts=[3, 5, 10]
)
```

Main functions:
- `evaluate_model()`: Evaluates a single model configuration
- `print_evaluation_report()`: Prints a standardized evaluation report
- `evaluate_multiple_configurations()`: Evaluates multiple model configurations

### viz_utils.py

Provides visualization utilities:

```python
from tests.utils import create_performance_plots, visualize_results_comparison

# Create performance plots for a model
create_performance_plots(y_true, y_pred, output_dir="plots", model_name="my_model")

# Compare results across different configurations
visualize_results_comparison(results_df, output_dir="comparison_plots")
```

Main functions:
- `create_performance_plots()`: Creates comprehensive performance plots for regression results
- `visualize_results_comparison()`: Visualizes comparison of results across different configurations

### Example: Simplified Model Evaluation

The `simplified_model_evaluation.py` script demonstrates how to use these utility modules:

```bash
# Run with default settings (single model configuration)
python simplified_model_evaluation.py

# Find the best model configuration
python simplified_model_evaluation.py --evaluation-mode best

# Run in test mode with fewer combinations
python simplified_model_evaluation.py --evaluation-mode multiple --test-mode
```

A shell script for running this example is provided:

```bash
# Run the simplified model evaluation script
./run/run_simplified_model_evaluation.sh

# Find the best model configuration with 4 parallel jobs
./run/run_simplified_model_evaluation.sh --evaluation-mode best --n-jobs 4

# Run in test mode
./run/run_simplified_model_evaluation.sh --test-mode
```

## Logging System

All test scripts write logs to the `data_gen/logs/` directory with the following convention:

- Each log file is timestamped: `<test_name>_YYYYMMDD_HHMMSS.log`
- Example: `partition_comparison_20230508_150747.log`

# Tests Directory

This directory contains tests for the `fit_better` package, organized into several subdirectories:

## Directory Structure

- **unittests/**: Contains unit tests for individual modules and functions
  - Tests are organized by module (e.g., `test_file_loader.py` tests the `file_loader.py` module)
  - Run with pytest: `pytest tests/unittests`

- **integration/**: Contains integration tests that verify different parts of the system work together
  - Tests end-to-end flows with multiple components
  - Run with pytest: `pytest tests/integration`

- **usages/**: Contains example scripts showing how to use the package
  - These are runnable examples demonstrating common usage patterns
  - Run directly: `python tests/usages/simplified_model_evaluation.py`

- **utils/**: Contains utility functions used by tests
  - `model_evaluation.py`: Utilities for model training and evaluation
  - `argparse_utils.py`: Command-line argument utilities for test scripts
  - `viz_utils.py`: [DEPRECATED] - Visualization utilities (use `fit_better.utils.plotting` instead)

## Running Tests

### Running All Tests

```bash
# Run all tests
pytest

# Run with more detailed output
pytest -v
```

### Running Specific Tests

```bash
# Run unit tests only
pytest tests/unittests

# Run a specific test file
pytest tests/unittests/test_file_loader.py

# Run a specific test function
pytest tests/unittests/test_file_loader.py::TestFileLoader::test_load_file_to_array
```

### Running Test Scripts

The usage examples can be run directly as Python scripts:

```bash
# Run a basic model evaluation example
python tests/usages/simplified_model_evaluation.py --evaluation-mode single --partition-mode KMEANS --regressor-type RANDOM_FOREST
```

## Recent Improvements

1. **Consolidated Visualization**: All visualization utilities have been moved from `tests/utils/viz_utils.py` to the main package in `fit_better/utils/plotting.py`. The old module is kept for backward compatibility but is deprecated.

2. **Improved Documentation**: Usage examples have been added to all test scripts and utilities.

3. **Reduced Dependencies**: Removed dependencies on pandas and seaborn for visualization, using only NumPy and matplotlib.

4. **Standardized Interfaces**: Test utilities now follow consistent naming and parameter conventions.
