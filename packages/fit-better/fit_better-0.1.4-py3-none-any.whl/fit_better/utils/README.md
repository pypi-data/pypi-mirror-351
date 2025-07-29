# Utility Modules

This directory contains utility modules that provide various functionality used throughout the fit_better package.

## plotting.py

The `plotting.py` module provides comprehensive visualization utilities for regression analysis and model evaluation. The module was created by merging previous separate visualization utilities to provide a unified and consistent interface.

### Key Features:

- **Basic Comparison Plots**: Compare actual vs predicted values using scatter plots.
- **Error Visualization**: Create histograms of errors and percentage errors.
- **Partition Visualization**: Visualize how data is partitioned in different partition modes.
- **Model Comparison**: Generate plots comparing different models or configurations.
- **Comprehensive Reports**: Create full regression evaluation reports with multiple plots.

### Usage Example:

```python
from fit_better.utils.plotting import (
    plot_versus, 
    plot_predictions_vs_actual,
    create_regression_report_plots
)

# Basic comparison
plot_versus(y_true, y_pred, title="Model Predictions")

# Create detailed prediction visualization
plot_predictions_vs_actual(y_true, y_pred, title="Model Performance")

# Generate comprehensive report with multiple plots
create_regression_report_plots(
    y_true, 
    y_pred, 
    output_dir='plots', 
    model_name='RandomForest'
)
```

### Design Principles:

1. **No External Dependencies**: The module uses only matplotlib and NumPy, avoiding dependencies on pandas or seaborn.
2. **Consistent Interface**: All plotting functions follow a consistent interface pattern.
3. **Flexibility**: Functions can either display or save plots, and accept customization options.
4. **Comprehensive Documentation**: All functions have detailed docstrings explaining their usage.

## statistics.py

The `statistics.py` module provides functions for calculating various regression statistics and error metrics.

## Other Utilities

- **logging_utils.py**: Utilities for setting up and configuring logging.
- **ascii.py**: Utilities for ASCII-based visualization and table formatting. 