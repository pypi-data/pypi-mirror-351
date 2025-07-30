# Test Utilities

This directory contains utility modules to reduce code duplication and improve code organization across test scripts in the fit-better library.

## Key Improvements

1. **Reduced Code Redundancy**
   - Consolidated similar functionality from multiple test scripts
   - Created reusable utility functions for common operations
   - Standardized argument parsing across all test scripts

2. **Better Code Organization**
   - Organized utilities into logical modules
   - Added proper documentation and type hints
   - Made imports consistent and intuitive

3. **Unified Model Evaluation**
   - Created a single, versatile model evaluation interface
   - Combined functionality from multiple scripts
   - Added options to control behavior without duplicating code

## Utility Modules

### `argparse_utils.py`

Standardized argument parsing for all test scripts:
- `get_default_parser()`: Creates a parser with all standard argument groups
- `add_io_args()`: Adds input/output file arguments
- `add_model_args()`: Adds model parameter arguments
- `add_output_args()`: Adds output directory arguments
- `add_preprocessing_args()`: Adds data preprocessing arguments
- `add_logging_args()`: Adds logging configuration arguments

### `data_utils.py`

Utilities for data loading and generation:
- `load_test_data()`: Loads data from files or generates synthetic data
- `generate_synthetic_data()`: Generates synthetic data with customizable parameters
- `save_data_multiple_formats()`: Saves data in multiple formats (CSV, NPY)

### `eval_utils.py`

Model evaluation utilities:
- `evaluate_model()`: Evaluates a single model configuration
- `print_evaluation_report()`: Prints a standardized evaluation report
- `evaluate_multiple_configurations()`: Evaluates multiple model configurations

### `viz_utils.py`

Visualization utilities:
- `create_performance_plots()`: Creates comprehensive performance plots for regression results
- `visualize_results_comparison()`: Visualizes comparison of results across different configurations

### `model_evaluation.py` (New)

Unified model evaluation interface:
- `train_and_evaluate_model()`: Trains and evaluates a single model
- `find_best_model()`: Tests multiple configurations to find the best model
- `save_predictions_to_csv()`: Saves model predictions to CSV files
- `generate_comparison_visualizations()`: Creates comparison visualizations

## Usage Examples

### Single Model Evaluation

```python
from tests.utils.model_evaluation import train_and_evaluate_model
from fit_better import PartitionMode, RegressorType

results = train_and_evaluate_model(
    X_train, y_train, X_test, y_test,
    partition_mode=PartitionMode.KMEANS,
    n_partitions=5,
    regressor_type=RegressorType.RANDOM_FOREST,
    n_jobs=4,
    output_dir="./results"
)
```

### Finding Best Model

```python
from tests.utils.model_evaluation import find_best_model

best_result = find_best_model(
    X_train, y_train, X_test, y_test,
    n_jobs=4,
    output_dir="./best_model_results",
    test_mode=True
)
```

### Using Unified Script

```bash
# Single model evaluation
python tests/usages/unified_model_evaluation.py --partition-mode KMEANS --regressor-type RANDOM_FOREST

# Find best model
python tests/usages/unified_model_evaluation.py --evaluation-mode find_best --test-mode
```

## Additional Notes

- All functions include proper type hints and documentation
- Most functions follow a consistent pattern and parameter naming
- When possible, these utilities leverage the built-in functions of the fit-better library rather than reimplementing them 