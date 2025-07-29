"""\nGeneral Utilities for the Fit Better Package\n==============================================\n\nThe `fit_better.utils` module provides a collection of helper functions and classes\nthat support various operations across the `fit_better` package. These utilities\nare not specific to core regression logic or data handling but offer common\nfunctionalities like logging configuration, statistical calculations, plotting,\nand other miscellaneous tasks.\n\nKey Submodules and Functionalities:\n-----------------------------------\n\n*   **`logging_utils.py`**: Configures and manages logging throughout the `fit_better`\n    package. It typically includes functions to:\n    *   Get a pre-configured logger instance (`get_logger`).\n    *   Set up logging for main processes and worker processes (e.g., in parallel execution).\n    *   Control log levels and output formats (console, file).\n
*   **`plotting.py`**: Contains functions for generating various plots to visualize data,\n    model performance, and results. Examples might include:\n    *   Plotting actual vs. predicted values.\n    *   Visualizing data distributions or partitions.\n    *   Displaying learning curves or feature importance.\n    *   (Often uses libraries like Matplotlib or Seaborn).

*   **`statistics.py`**: Provides statistical helper functions that might be used in\n    evaluation, data analysis, or within specific algorithms. This could include:\n    *   Calculating confidence intervals.\n    *   Performing statistical tests.\n    *   Computing custom metrics not directly available in scikit-learn.\n
*   **`ascii.py`**: (Potentially) Utilities for generating ASCII art, tables, or simple text-based\n    visualizations, perhaps for console output or simple reports.\n
*   **`README.md`**: Provides specific documentation for the utils module itself.\n
This module helps keep the rest of the `fit_better` codebase clean by centralizing\ncommon, reusable helper functions.
"""

from .statistics import (
    calc_regression_statistics,
    print_partition_statistics,
    calculate_total_performance,
    get_error_percentiles,
    format_statistics_table,
    compare_model_statistics,
)
from .ascii import print_ascii_table
from .plotting import (
    plot_performance_comparison,
    plot_versus,
    plot_predictions_vs_actual,
    plot_error_distribution,
    create_regression_report_plots,
    visualize_partition_boundaries as plot_partition_boundaries,
)
from ..data.csv_manager import CSVMgr

# Re-export CSV utilities from CSVMgr as functions for backward compatibility
array_to_csv = CSVMgr.array_to_csv
arrays_to_csv = CSVMgr.arrays_to_csv
csv_to_array = CSVMgr.csv_to_array
save_xy_data = CSVMgr.save_xy_data

# Re-export key components for easier access
from .logging_utils import get_logger, setup_logging, setup_worker_logging

__all__ = [
    "calc_regression_statistics",
    "print_ascii_table",
    "plot_performance_comparison",
    "plot_versus",
    "plot_predictions_vs_actual",
    "plot_error_distribution",
    "create_regression_report_plots",
    "array_to_csv",
    "arrays_to_csv",
    "csv_to_array",
    "save_xy_data",
    "get_logger",
    "setup_logging",
    "setup_worker_logging",
    "plot_partition_boundaries",
    "print_partition_statistics",
    "calculate_total_performance",
    "get_error_percentiles",
    "format_statistics_table",
    "compare_model_statistics",
]
