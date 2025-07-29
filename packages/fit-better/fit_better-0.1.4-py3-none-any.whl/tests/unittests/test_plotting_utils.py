"""
Unit tests for plotting utilities.

This test suite validates:
- Plot creation functions
- Formatting and styling options
- Figure saving functionality
- Multiple plot types (comparison, error distribution, etc.)
"""

import os
import sys
import pytest
import numpy as np
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

from fit_better.utils.plotting import (
    plot_versus,
    plot_performance_comparison,
    plot_predictions_vs_actual,
    plot_error_distribution,
    create_regression_report_plots,
)


@pytest.fixture
def sample_prediction_data():
    """Create sample prediction data for plotting tests."""
    np.random.seed(42)
    X = np.linspace(0, 10, 100)
    y_true = 2 * X + 3 + np.random.normal(0, 1, 100)
    y_pred1 = 2.1 * X + 2.9 + np.random.normal(0, 0.5, 100)  # Model 1
    y_pred2 = 1.9 * X + 3.1 + np.random.normal(0, 1.5, 100)  # Model 2
    return X, y_true, y_pred1, y_pred2


@pytest.fixture
def multiple_model_results():
    """Create sample model results for performance comparison."""
    # Using list of dictionaries as per the implementation
    return [
        {
            "regressor_name": "Linear",
            "mae": 0.8,
            "rmse": 1.2,
            "r2": 0.85,
            "pct_within_5pct": 75,
        },
        {
            "regressor_name": "Polynomial",
            "mae": 0.7,
            "rmse": 1.0,
            "r2": 0.89,
            "pct_within_5pct": 80,
        },
        {
            "partition_mode": "RF",
            "mae": 0.6,
            "rmse": 0.9,
            "r2": 0.92,
            "pct_within_5pct": 85,
        },
    ]


@pytest.mark.unit
class TestPlottingUtils:
    """Test suite for plotting utilities."""

    def test_plot_versus(self, sample_prediction_data, tmp_path):
        """Test the plot_versus function."""
        X, y_true, y_pred, _ = sample_prediction_data

        # Create a plot
        ax = plot_versus(
            golden=y_true,
            compared=y_pred,
            title="Test Versus Plot",
            golden_label="True",
            compared_label="Predicted",
        )

        # Check that ax is a valid matplotlib axes
        assert isinstance(ax, plt.Axes), "Result should be a matplotlib Axes"

        # Save the figure to test saving functionality
        output_path = os.path.join(tmp_path, "versus_plot.png")
        ax.figure.savefig(output_path)

        # Check that the file was created
        assert os.path.exists(output_path), "Output plot file should exist"
        assert os.path.getsize(output_path) > 0, "Output plot file should not be empty"

        # Close the figure to avoid warnings
        plt.close(ax.figure)

    def test_plot_predictions_vs_actual(self, sample_prediction_data, tmp_path):
        """Test the plot_predictions_vs_actual function."""
        _, y_true, y_pred, _ = sample_prediction_data

        # Create a plot
        fig = plot_predictions_vs_actual(
            y_true=y_true, y_pred=y_pred, title="Test Predictions vs Actual"
        )

        # Check that fig is a valid matplotlib figure
        assert isinstance(fig, plt.Figure), "Result should be a matplotlib Figure"

        # Save the figure to test saving functionality
        output_path = os.path.join(tmp_path, "pred_vs_actual.png")
        fig.savefig(output_path)

        # Check that the file was created
        assert os.path.exists(output_path), "Output plot file should exist"
        assert os.path.getsize(output_path) > 0, "Output plot file should not be empty"

        # Close the figure to avoid warnings
        plt.close(fig)

    def test_plot_error_distribution(self, sample_prediction_data, tmp_path):
        """Test the plot_error_distribution function."""
        _, y_true, y_pred, _ = sample_prediction_data

        # Create a plot
        fig = plot_error_distribution(
            y_true=y_true, y_pred=y_pred, title="Test Error Distribution"
        )

        # Check that fig is a valid matplotlib figure
        assert isinstance(fig, plt.Figure), "Result should be a matplotlib Figure"

        # Save the figure to test saving functionality
        output_path = os.path.join(tmp_path, "error_distribution.png")
        fig.savefig(output_path)

        # Check that the file was created
        assert os.path.exists(output_path), "Output plot file should exist"
        assert os.path.getsize(output_path) > 0, "Output plot file should not be empty"

        # Close the figure to avoid warnings
        plt.close(fig)

    def test_plot_performance_comparison(self, multiple_model_results, tmp_path):
        """Test the plot_performance_comparison function."""
        # Create a plot
        fig = plot_performance_comparison(
            results=multiple_model_results,
            metric="mae",
            title="Test Performance Comparison",
        )

        # Check that fig is a valid matplotlib figure
        assert isinstance(fig, plt.Figure), "Result should be a matplotlib Figure"

        # Save the figure to test saving functionality
        output_path = os.path.join(tmp_path, "perf_comparison.png")
        fig.savefig(output_path)

        # Check that the file was created
        assert os.path.exists(output_path), "Output plot file should exist"
        assert os.path.getsize(output_path) > 0, "Output plot file should not be empty"

        # Close the figure to avoid warnings
        plt.close(fig)

    def test_create_regression_report_plots(self, sample_prediction_data, tmp_path):
        """Test the create_regression_report_plots function."""
        _, y_true, y_pred, _ = sample_prediction_data

        # Create output directory
        output_dir = os.path.join(tmp_path, "regression_report")
        os.makedirs(output_dir, exist_ok=True)

        # Create report plots
        result = create_regression_report_plots(
            y_true=y_true, y_pred=y_pred, model_name="TestModel", output_dir=output_dir
        )

        # Check that the function returned a dictionary of figures
        assert isinstance(
            result, dict
        ), "Function should return a dictionary of figures"
        assert len(result) == 5, "Should create 5 figures"

        # Check that plot files were created with the correct names in the model_name_plots subdirectory
        plots_dir = os.path.join(output_dir, "TestModel_plots")
        expected_files = [
            "TestModel_pred_vs_actual.png",
            "TestModel_error_distribution.png",
            "TestModel_error_vs_predicted.png",
            "TestModel_pct_error_vs_actual.png",
            "TestModel_pct_error_distribution.png",
        ]

        for filename in expected_files:
            file_path = os.path.join(plots_dir, filename)
            assert os.path.exists(
                file_path
            ), f"Output plot file {filename} should exist"
            assert (
                os.path.getsize(file_path) > 0
            ), f"Output plot file {filename} should not be empty"

    def test_plot_customization(self, sample_prediction_data, tmp_path):
        """Test customization options for plotting functions."""
        X, y_true, y_pred, _ = sample_prediction_data

        # Test custom title
        ax = plot_versus(
            golden=y_true,
            compared=y_pred,
            title="Custom Title",
            golden_label="True Values",
            compared_label="Predicted Values",
        )

        # Check that the title was set
        assert ax.get_title() == "Custom Title", "Custom title should be set"

        # Check that the axis labels were set
        assert ax.get_xlabel() == "True Values", "X-axis label should be set"
        assert ax.get_ylabel() == "Predicted Values", "Y-axis label should be set"

        # Save and close the figure
        output_path = os.path.join(tmp_path, "custom_plot.png")
        ax.figure.savefig(output_path)
        plt.close(ax.figure)

    def test_multiple_plots_overlay(self, sample_prediction_data, tmp_path):
        """Test creating multiple plots on the same figure."""
        _, y_true, y_pred1, y_pred2 = sample_prediction_data

        # Create a figure with two plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Plot first comparison
        ax1 = plot_versus(
            golden=y_true,
            compared=y_pred1,
            title="Model 1",
            golden_label="True",
            compared_label="Pred1",
            ax=ax1,
        )

        # Plot second comparison
        ax2 = plot_versus(
            golden=y_true,
            compared=y_pred2,
            title="Model 2",
            golden_label="True",
            compared_label="Pred2",
            ax=ax2,
        )

        # Check that both axes were created
        assert isinstance(ax1, plt.Axes), "First axes should be created"
        assert isinstance(ax2, plt.Axes), "Second axes should be created"

        # Save the figure with both plots
        output_path = os.path.join(tmp_path, "multiple_plots.png")
        fig.savefig(output_path)

        # Check that the file was created
        assert os.path.exists(output_path), "Output plot file should exist"
        assert os.path.getsize(output_path) > 0, "Output plot file should not be empty"

        # Close the figure
        plt.close(fig)
