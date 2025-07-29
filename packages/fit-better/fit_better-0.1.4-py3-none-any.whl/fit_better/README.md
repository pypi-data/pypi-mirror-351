# Fit Better Core Module

**Author:** hi@xlindo.com  
**Update Date:** 2025-05-10

This package provides a comprehensive suite of Python and C++ utilities for intelligent regression modeling, data generation, evaluation, model management, and deployment. It is designed for flexible experimentation and robust logging, with modular components for each stage of the regression workflow. The package supports both Python and C++ deployment, with cross-language testing to ensure consistency.

## Core Components

- **model_utils.py**: Contains utilities for model training, selection, and evaluation
- **partition_utils.py**: Implements data partitioning strategies
- **sklearn_utils.py**: Provides enhanced scikit-learn integration with transformers and meta-estimators
- **plot_utils.py**: Contains visualization utilities
- **stats_utils.py**: Provides statistical analysis utilities
- **data_utils.py**: Contains data loading and preparation utilities
- **io.py**: Handles model serialization, export, and import operations
- **cpp_export.py**: Manages C++ deployment and code generation

## Primary API

The package exposes a simplified API for ease of use:

```python
from fit_better import RegressionFlow, PartitionMode, RegressorType, Metric
```

## Modules in Detail

### model_utils.py

- Enumerations for regressor types and evaluation metrics
- Functions for fitting various regression models
- Model selection based on performance metrics
- Hyperparameter optimization utilities

### partition_utils.py

- Implementations of different data partitioning strategies
- Functions for training models on partitioned data
- Boundary determination and validation
- Partition visualization and analysis

### sklearn_utils.py

- Scikit-learn compatible transformers and estimators
- Pipeline integration for streamlined workflows
- Ensemble modeling (voting, stacking) with partitioning
- Advanced cross-validation and hyperparameter tuning

Key components:
- `PartitionTransformer`: A transformer that partitions data based on feature values, with support for random_state to ensure reproducible clustering results
- `AdaptivePartitionRegressor`: A meta-estimator for adaptive partitioning
- `PolyPartitionPipeline`: A pipeline that combines polynomial features with partitioning
- Helpers for creating ensemble and stacking models

### plot_utils.py

- Visualization of model performance
- Comparison of different partitioning strategies
- Regression report generation
- Interactive plot generation with plotly support

### stats_utils.py

- Calculation of regression statistics
- Error metrics computation
- Statistical tests for model comparison
- Outlier detection and analysis

### data_utils.py

- Functions for loading data from various sources
- Data preprocessing utilities
- Synthetic data generation for testing and validation
- Cross-validation data splitting

### io.py

- Model serialization and deserialization
- Export models to JSON format for C++ deployment
- Import models from JSON format
- Model version management

### ascii_utils.py

- Utilities for generating and printing ASCII tables from column labels and row data
- Formatting options for console output
- Progress bar implementations

### model_predict_utils.py

- Utilities for saving, loading, and predicting with regression models
- Support for transformers in prediction pipelines
- Batch prediction utilities for large datasets

### cpp_export.py

- Utilities for exporting models to C++ format
- Code generation for C++ model implementation
- Cross-language testing utilities

## Usage Examples

### Basic RegressionFlow API

```python
from fit_better import RegressionFlow, PartitionMode, RegressorType

# Initialize the regression flow
flow = RegressionFlow()

# Find the best regression strategy
result = flow.find_best_strategy(
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    partition_mode=PartitionMode.KMEANS,
    regressor_type=RegressorType.AUTO,
    n_partitions=5,
    n_jobs=-1
)

# Make predictions
predictions = flow.predict(X_new)

# Export model for C++ deployment
from fit_better.io import export_model_to_json
export_model_to_json(result.best_model, "best_model.json")
```

### Enhanced scikit-learn API

```python
from fit_better.sklearn_utils import AdaptivePartitionRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Create a sklearn-compatible pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('regressor', AdaptivePartitionRegressor(
        n_partitions=5,
        partition_mode='kmeans',
        regressor_type='xgboost',
        n_jobs=-1
    ))
])

# Fit and predict using sklearn API
pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
```

### Ensemble Approach

```python
from fit_better.sklearn_utils import create_ensemble_model

# Create an ensemble model combining multiple partition strategies
ensemble = create_ensemble_model(
    X_train, y_train,
    n_partitions=5,
    partition_modes=['kmeans', 'percentile', 'equal_width'],
    regressor_types=['lightgbm', 'random_forest'],
    n_jobs=-1
)

# Make predictions with the ensemble
predictions = ensemble.predict(X_test)
```

## C++ Deployment & Cross-Language Testing

The package includes a C++ implementation for core regression algorithms and preprocessing. C++ deployment is managed via CMake, and unit tests are provided using Google Test (GTest). Cross-language tests compare Python and C++ results to ensure consistency.

### Building and Testing C++

1. Install dependencies: CMake, GTest, Boost, and a C++17 compiler.
2. Build the C++ project:
   ```bash
   cd cpp
   mkdir -p build && cd build
   cmake ..
   make
   ```
3. Run C++ unit tests:
   ```bash
   ctest
   # or
   ./tests/fit_better_tests
   ```
4. Run cross-language deployment check from Python:
   ```bash
   python tests/custom/test_cpp_deployment.py
   ```

## Documentation

Complete API documentation is available at [https://fit-better.readthedocs.io](https://fit-better.readthedocs.io)

## License

This project is licensed under a Proprietary License. Please contact the authors for licensing details.