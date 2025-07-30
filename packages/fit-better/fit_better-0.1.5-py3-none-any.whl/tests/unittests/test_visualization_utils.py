#!/usr/bin/env python3
"""
Test script for fit_better visualization utilities.

This script tests various visualization functions provided by fit_better:
- Simple 2D plots of data
- Regression performance visualization
- Error distribution plots
- Comparison charts for different models
- Learning curve plots
"""

import os
import sys
import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Set up paths for importing fit_better
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

grandparent_dir = os.path.dirname(parent_dir)
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

# Import visualization utilities from fit_better
from fit_better.utils.plotting import (
    plot_versus,
    plot_performance_comparison,
    plot_predictions_vs_actual,
    plot_error_distribution,
    create_regression_report_plots,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_test_data(n_samples=200):
    """Generate data for visualization tests."""
    np.random.seed(42)
    X = np.linspace(0, 10, n_samples)

    # Generate multiple model predictions
    y_true = 2 * X + 3 + np.random.normal(0, 1, n_samples)
    y_pred1 = 2.1 * X + 2.9 + np.random.normal(0, 0.8, n_samples)  # Good model
    y_pred2 = 1.8 * X + 3.5 + np.random.normal(0, 1.5, n_samples)  # Medium model
    y_pred3 = 1.2 * X + 5 + np.random.normal(0, 2, n_samples)  # Poor model

    return X, y_true, y_pred1, y_pred2, y_pred3


def test_plot_versus():
    """Test basic x vs y plotting function."""
    logger.info("Testing plot_versus function...")

    X, y_true, y_pred, _, _ = generate_test_data()

    # Create basic plot
    ax = plot_versus(
        golden=y_true,
        compared=y_pred,
        title="Basic Versus Plot",
        golden_label="True Values",
        compared_label="Predicted Values",
    )

    # Get the figure from the axis
    fig = ax.figure

    # Save the figure - make sure we're using the tests/data_gen path
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(tests_dir, "data_gen", "visualization_results")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "plot_versus.png")
    fig.savefig(output_path)

    # Close the figure to avoid warnings
    plt.close(fig)

    logger.info(f"Saved plot to {output_path}")
    assert os.path.exists(output_path), "Plot file should exist"


def test_predictions_vs_actual():
    """Test predictions vs actual plotting function."""
    logger.info("Testing plot_predictions_vs_actual function...")

    _, y_true, y_pred1, _, _ = generate_test_data()

    # Create predictions vs actual plot
    fig = plot_predictions_vs_actual(
        y_true=y_true, y_pred=y_pred1, title="Predictions vs Actual Values"
    )

    # Save the figure - make sure we're using the tests/data_gen path
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(tests_dir, "data_gen", "visualization_results")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "predictions_vs_actual.png")
    fig.savefig(output_path)

    # Close the figure to avoid warnings
    plt.close(fig)

    logger.info(f"Saved plot to {output_path}")
    assert os.path.exists(output_path), "Plot file should exist"


def test_error_distribution():
    """Test error distribution plotting function."""
    logger.info("Testing plot_error_distribution function...")

    _, y_true, y_pred1, _, _ = generate_test_data()

    # Create error distribution plot
    fig = plot_error_distribution(
        y_true=y_true, y_pred=y_pred1, title="Error Distribution"
    )

    # Save the figure - make sure we're using the tests/data_gen path
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(tests_dir, "data_gen", "visualization_results")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "error_distribution.png")
    fig.savefig(output_path)

    # Close the figure to avoid warnings
    plt.close(fig)

    logger.info(f"Saved plot to {output_path}")
    assert os.path.exists(output_path), "Plot file should exist"


def test_performance_comparison():
    """Test model performance comparison plotting function."""
    logger.info("Testing plot_performance_comparison function...")

    _, y_true, y_pred1, y_pred2, y_pred3 = generate_test_data()

    # Calculate metrics for each model
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    def calc_metrics(y_true, y_pred):
        return {
            "mae": mean_absolute_error(y_true, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            "r2": r2_score(y_true, y_pred),
            "pct_within_10pct": 100 * np.mean(np.abs((y_true - y_pred) / y_true) < 0.1),
        }

    # Create list of results for the performance comparison
    model_results = [
        {"regressor_name": "Model 1 (Good)", **calc_metrics(y_true, y_pred1)},
        {"regressor_name": "Model 2 (Medium)", **calc_metrics(y_true, y_pred2)},
        {"regressor_name": "Model 3 (Poor)", **calc_metrics(y_true, y_pred3)},
    ]

    # Create performance comparison plot
    fig = plot_performance_comparison(
        results=model_results, metric="mae", title="Model Performance Comparison"
    )

    # Save the figure - make sure we're using the tests/data_gen path
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(tests_dir, "data_gen", "visualization_results")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "performance_comparison.png")
    fig.savefig(output_path)

    # Close the figure to avoid warnings
    plt.close(fig)

    logger.info(f"Saved plot to {output_path}")
    assert os.path.exists(output_path), "Plot file should exist"


def test_regression_report():
    """Test creating a complete regression report with multiple plots."""
    logger.info("Testing create_regression_report_plots function...")

    _, y_true, y_pred1, _, _ = generate_test_data()

    # Create output directory - make sure we're using the tests/data_gen path
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(
        tests_dir, "data_gen", "visualization_results", "regression_report"
    )
    os.makedirs(output_dir, exist_ok=True)

    # Create regression report plots
    model_name = "TestModel"
    result = create_regression_report_plots(
        y_true=y_true, y_pred=y_pred1, model_name=model_name, output_dir=output_dir
    )

    # Check that the returned result contains the expected figure keys
    expected_keys = ["pred_vs_actual", "error_distribution", "error_vs_pred"]
    result_has_all_keys = all(key in result for key in expected_keys)
    assert result_has_all_keys, "Result should contain all expected figure keys"

    # Check that all figures in the result are valid matplotlib figures
    assert all(
        isinstance(fig, plt.Figure) for fig in result.values()
    ), "All results should be matplotlib figures"

    logger.info(f"Successfully created regression report in {output_dir}")


def main():
    """Run all visualization tests."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"Starting visualization tests at {timestamp}")

    # Create main output directory - make sure we're using the tests/data_gen path
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(tests_dir, "data_gen", "visualization_results")
    os.makedirs(output_dir, exist_ok=True)

    # Run all tests
    test_functions = [
        test_plot_versus,
        test_predictions_vs_actual,
        test_error_distribution,
        test_performance_comparison,
        test_regression_report,
    ]

    results = []
    for test_func in test_functions:
        try:
            result = test_func()
            # Convert None to False to handle functions that don't return a value
            results.append(True)  # All test functions now use assertions
            status = "PASS"
            logger.info(f"{test_func.__name__}: {status}")
        except Exception as e:
            logger.error(f"{test_func.__name__} failed with error: {str(e)}")
            results.append(False)

    # Print overall summary
    n_passed = sum(1 for r in results if r)
    n_total = len(results)
    logger.info(f"Test Summary: {n_passed}/{n_total} tests passed")

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
