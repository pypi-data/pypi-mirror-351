"""
Utility functions for visualization in test scripts.

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use fit_better.utils.plotting directly instead.

Examples:
    # Instead of:
    from tests.utils.viz_utils import create_performance_plots

    # Use:
    from fit_better.utils.plotting import create_regression_report_plots
"""

import os
import warnings
import numpy as np
import matplotlib.pyplot as plt
import logging
from typing import Dict, Any, Optional, Union, List

from fit_better.utils.plotting import (
    visualize_partition_boundaries,
    create_regression_report_plots,
    visualize_results_comparison as _visualize_results_comparison,
)

logger = logging.getLogger(__name__)

# Emit deprecation warning
warnings.warn(
    "The viz_utils module is deprecated and will be removed in a future version. "
    "Please use fit_better.utils.plotting directly instead.",
    DeprecationWarning,
    stacklevel=2,
)


def create_performance_plots(
    y_true, y_pred, output_dir, model_name="model", create_subdir=True
):
    """
    Create comprehensive performance plots for regression results.

    DEPRECATED: Use fit_better.utils.plotting.create_regression_report_plots instead.

    Args:
        y_true: True target values
        y_pred: Predicted target values
        output_dir: Directory to save plots
        model_name: Name of the model for file naming
        create_subdir: Whether to create a subdirectory for the plots
    """
    warnings.warn(
        "create_performance_plots is deprecated. Use create_regression_report_plots instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    if not create_subdir:
        # Original function used output_dir directly when create_subdir=False
        # Create a temporary subdir and then move files to maintain compatibility
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        figures = create_regression_report_plots(y_true, y_pred, temp_dir, model_name)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Move files from subdirectory to main directory
        for filename in os.listdir(os.path.join(temp_dir, f"{model_name}_plots")):
            src = os.path.join(temp_dir, f"{model_name}_plots", filename)
            dst = os.path.join(output_dir, filename)
            shutil.copy2(src, dst)

        # Clean up temporary directory
        shutil.rmtree(temp_dir)
    else:
        figures = create_regression_report_plots(y_true, y_pred, output_dir, model_name)

    return figures


def visualize_results_comparison(results_df, output_dir, metrics=None, top_n=10):
    """
    Visualize comparison of results across different model configurations.

    DEPRECATED: Use fit_better.utils.plotting.visualize_results_comparison instead.

    Args:
        results_df: DataFrame containing results for different configurations
        output_dir: Directory to save plots
        metrics: List of metrics to visualize (default: ['test_r2', 'test_rmse', 'test_mae'])
        top_n: Number of top configurations to highlight
    """
    warnings.warn(
        "This function is deprecated. Use fit_better.utils.plotting.visualize_results_comparison instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return _visualize_results_comparison(results_df, output_dir, metrics, top_n)
