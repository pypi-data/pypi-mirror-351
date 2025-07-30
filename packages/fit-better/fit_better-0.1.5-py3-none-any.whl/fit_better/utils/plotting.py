"""\nComprehensive Plotting Utilities for Regression Analysis\n=======================================================\n\nAuthor: hi@xlindo.com\nCreate Time: 2025-04-29\n\nThis module provides a suite of functions for generating a variety of plots\ncommonly used in regression analysis, model evaluation, and data visualization.\nIt aims to offer a standardized and easy-to-use interface for creating insightful\nvisualizations to understand data, model behavior, and performance.\n
It leverages Matplotlib for plotting and provides configurable plot settings.\nThe `matplotlib.use("Agg")` backend is set by default, meaning plots are rendered\nto files or buffers without requiring a GUI, suitable for server environments or batch processing.\n
Key Plotting Capabilities:\n--------------------------
\n*   **Actual vs. Predicted Plots (`plot_versus`, `plot_predictions_vs_actual`)**:\n    *   Scatter plots comparing true target values against model predictions.\n    *   Often include a y=x reference line for perfect prediction.\n    *   May highlight points with significant errors (e.g., >5% relative difference).\n    *   Typically display key performance metrics (MAE, Std(Res), etc.) on the plot.\n
*   **Error/Residual Analysis (`plot_error_distribution`)**:\n    *   Histograms or density plots of prediction errors (residuals = predicted - actual).\n    *   Helps to understand the distribution of errors (e.g., normality, skewness, outliers).\n    *   May include statistics like mean error, standard deviation of errors.\n
*   **Performance Comparison (`plot_performance_comparison`)**:\n    *   Bar charts to compare performance metrics (e.g., MAE, R², RMSE) across different models,\n        configurations, or partitioning strategies.\n    *   Highlights best and worst performers with distinct colors.\n    *   Displays metric values on top of bars for clarity.\n
*   **Partition Visualization (`visualize_partition_boundaries`, `plot_partition_results` in other files often call this)**:\n    *   Visualizes how data is segmented by different partitioning strategies.\n    *   For 1D or 2D features, can show data points colored by partition and the decision boundaries.\n    *   Helps in understanding if partitions are meaningful and how models adapt to them.\n
*   **Comprehensive Reports (`create_regression_report_plots`)**:\n    *   Generates a set of standard plots (e.g., actual vs. predicted, error distribution)\n        for a given model and saves them to a specified directory.\n    *   Useful for quickly producing a visual summary of a model's performance.\n
*   **Other Specialized Plots** (capabilities hinted by function names in `__init__.py` or full file):\n    *   `plot_feature_importance`: Bar charts of feature importances from models like Random Forest or Gradient Boosting.\n    *   `plot_learning_curve`: Shows training and validation scores as a function of training set size.\n    *   `plot_calibration_curve`: Assesses the calibration of probabilistic predictions.\n    *   `plot_data_distribution`: Histograms or density plots for individual features or the target variable.\n    *   `plot_correlation_matrix`: Heatmap of feature correlations.

Configuration and Style (`PLOT_SETTINGS`, `setup_plot_style`, `update_plot_settings`):\n-------------------------------------------------------------------------------------
\n*   `PLOT_SETTINGS`: A global dictionary defining default figure size, font size, DPI, colors for different\n    elements (primary, best, worst, reference, warning), and base Matplotlib style.\n*   `setup_plot_style()`: Applies some of the `PLOT_SETTINGS` to `plt.rcParams` for consistent styling.\n    (Note: The current `setup_plot_style` only sets figure size and font size, could be expanded.)
*   `update_plot_settings(new_settings)`: Allows users to override default plot settings globally.\n
Usage Example:\n--------------
```python
import numpy as np
from fit_better.utils.plotting import plot_predictions_vs_actual, plot_error_distribution, update_plot_settings
from fit_better.utils.logging_utils import setup_logging # For logger in plotting
import logging
import os

# Setup basic logging for the plotting module to show messages
setup_logging(level=logging.INFO)

# Sample data
np.random.seed(42)
y_true = np.random.rand(100) * 10
y_pred = y_true + np.random.normal(0, 1, 100)

# Customize plot settings (optional)
update_plot_settings({"figure_size": (10, 6), "font_size": 10, "colors": {"primary": "purple"}})

output_dir = "plotting_examples"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Plot actual vs. predicted
plot_predictions_vs_actual(y_true, y_pred,
                             title="Sample Model Performance",
                             save_path=os.path.join(output_dir, "actual_vs_pred.png"))
print(f"Saved actual vs. predicted plot to {output_dir}/actual_vs_pred.png")

# Plot error distribution
plot_error_distribution(y_true, y_pred,
                          title="Sample Error Distribution",
                          save_path=os.path.join(output_dir, "error_dist.png"))
print(f"Saved error distribution plot to {output_dir}/error_dist.png")

# Example of comparing results (assuming 'results' list is populated from model runs)
# results_data = [
#     {"regressor_name": "Model A", "mae": 0.5, "r2": 0.9},
#     {"regressor_name": "Model B", "mae": 0.4, "r2": 0.92},
#     {"regressor_name": "Model C", "mae": 0.6, "r2": 0.88},
# ]
# plot_performance_comparison(results_data, metric="mae", save_path=os.path.join(output_dir, "mae_comparison.png"))
# plot_performance_comparison(results_data, metric="r2", save_path=os.path.join(output_dir, "r2_comparison.png"))
```

This module aims to be a one-stop-shop for common visualizations in the `fit_better` workflow.
"""

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import logging
from typing import Dict, List, Tuple, Any, Optional, Union

matplotlib.use("Agg")  # Set non-interactive backend before importing pyplot

# Default visualization settings - can be modified by user apps
PLOT_SETTINGS = {
    "figure_size": (12, 8),
    "font_size": 12,
    "dpi": 100,
    "colors": {
        "primary": "#2c7bb6",
        "best": "#1a9850",
        "worst": "#d73027",
        "reference": "gray",
        "warning": "red",
    },
    "style": "default",
}

# Get logger for this module
logger = logging.getLogger(__name__)


def plot_versus(
    golden,
    compared,
    title="Versus Plot",
    ax=None,
    golden_label="Golden",
    compared_label="Compared",
    save_path=None,
):
    """
    Create a comparison scatter plot between golden/reference data and compared data.

    Args:
        golden: Reference data (numpy array or list)
        compared: Data to be compared against golden (numpy array or list)
        title: Plot title
        ax: Optional matplotlib axis to plot on (if None, creates a new figure)
        golden_label: Label for golden data
        compared_label: Label for compared data
        save_path: Path to save the figure (if None, figure is not saved)

    Returns:
        The matplotlib axis object
    """
    golden = np.array(golden).flatten()
    compared = np.array(compared).flatten()
    rel_res = np.abs(compared - golden) / (np.abs(golden) + 1e-12)
    mask_red = rel_res > 0.05
    mask_ok = ~mask_red
    show_plot = False

    if ax is None:
        fig, ax = plt.subplots(
            figsize=PLOT_SETTINGS["figure_size"], dpi=PLOT_SETTINGS["dpi"]
        )
        show_plot = True

    ax.scatter(
        golden[mask_ok],
        compared[mask_ok],
        s=1,
        alpha=0.5,
        label=f"{compared_label} vs {golden_label}",
    )

    if np.any(mask_red):
        ax.scatter(
            golden[mask_red],
            compared[mask_red],
            s=2,
            color=PLOT_SETTINGS["colors"]["warning"],
            alpha=0.7,
            label=f"{compared_label} vs {golden_label} (>5% diff)",
        )

    minv = min(golden.min(), compared.min())
    maxv = max(golden.max(), compared.max())
    ax.plot(
        [minv, maxv],
        [minv, maxv],
        color=PLOT_SETTINGS["colors"]["reference"],
        linewidth=2,
        label=f"{compared_label} = {golden_label} (reference)",
    )

    ax.set_xlabel(golden_label)
    ax.set_ylabel(compared_label)
    ax.set_title(title)
    ax.legend(loc="upper left")
    ax.set_aspect("equal", adjustable="box")

    # Stats table
    stats = _get_statistics_table(golden, compared)
    stat_str = "\n".join(f"{row[0]}: {row[1]}" for row in stats)
    ax.text(
        0.98,
        0.02,
        stat_str,
        fontsize=10,
        va="bottom",
        ha="right",
        transform=ax.transAxes,
        bbox=dict(facecolor="white", alpha=0.7, edgecolor="gray"),
    )

    if show_plot:
        plt.tight_layout()

    # Save the plot if a save path is provided
    if save_path:
        plt.savefig(save_path, dpi=PLOT_SETTINGS["dpi"], bbox_inches="tight")

    return ax


def _get_statistics_table(golden, compared):
    """
    Calculate statistics comparing golden and compared data.

    Args:
        golden: Reference data array
        compared: Data array to compare

    Returns:
        List of statistics rows (label, value)
    """
    golden = np.array(golden).flatten()
    compared = np.array(compared).flatten()
    residuals = compared - golden
    mae = np.mean(np.abs(residuals))
    std_res = np.std(residuals)
    max_res = np.max(residuals)
    min_res = np.min(residuals)
    rel_res = np.abs(residuals) / (np.abs(golden) + 1e-12)
    pct_3 = np.mean(rel_res <= 0.03) * 100
    pct_5 = np.mean(rel_res <= 0.05) * 100
    pct_10 = np.mean(rel_res <= 0.10) * 100

    return [
        ["MAE", f"{mae:.4f}"],
        ["Std(Res)", f"{std_res:.4f}"],
        ["Max(Res)", f"{max_res:.4f}"],
        ["Min(Res)", f"{min_res:.4f}"],
        ["RelRes<=3%", f"{pct_3:.2f}%"],
        ["RelRes<=5%", f"{pct_5:.2f}%"],
        ["RelRes<=10%", f"{pct_10:.2f}%"],
    ]


def setup_plot_style():
    """Setup a consistent style for all plots."""
    plt.rcParams["figure.figsize"] = PLOT_SETTINGS["figure_size"]
    plt.rcParams["font.size"] = PLOT_SETTINGS["font_size"]


def plot_performance_comparison(results, metric="mae", title=None, save_path=None):
    """
    Create a bar chart comparing performance metrics of different models/methods.

    Args:
        results: List of dictionaries with performance metrics
        metric: The metric to plot (default: 'mae')
        title: Optional title for the plot
        save_path: Path to save the figure (if None, figure is displayed)

    Returns:
        The matplotlib figure object
    """
    setup_plot_style()

    # Extract the relevant data
    names = [
        r.get("regressor_name", r.get("partition_mode", f"Model {i}"))
        for i, r in enumerate(results)
    ]
    values = [r.get(metric, 0) for r in results]

    # Sort by performance (ascending for error metrics, descending for R2)
    if metric.lower() in ["r2", "pct_within_5pct"]:
        sorted_indices = np.argsort(values)[::-1]  # Descending
    else:
        sorted_indices = np.argsort(values)  # Ascending for error metrics

    sorted_names = [names[i] for i in sorted_indices]
    sorted_values = [values[i] for i in sorted_indices]

    # Create the figure
    fig, ax = plt.subplots(
        figsize=PLOT_SETTINGS["figure_size"], dpi=PLOT_SETTINGS["dpi"]
    )

    # Use different colors for best/worst performers
    colors = [PLOT_SETTINGS["colors"]["primary"]] * len(sorted_values)
    colors[0] = PLOT_SETTINGS["colors"]["best"]  # Green for best
    if len(colors) > 1:
        colors[-1] = PLOT_SETTINGS["colors"]["worst"]  # Red for worst

    # Plot the bars
    bars = ax.bar(sorted_names, sorted_values, color=colors)

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.4f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    # Set the title and labels
    if title:
        ax.set_title(title)
    else:
        ax.set_title(f"Model Performance Comparison ({metric})")

    ax.set_ylabel(metric.upper() if metric in ["mae", "rmse"] else metric)
    ax.set_xlabel("Model")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=PLOT_SETTINGS["dpi"])

    return fig


def plot_predictions_vs_actual(y_true, y_pred, title=None, save_path=None):
    """
    Create a scatter plot of predicted vs actual values.

    Args:
        y_true: True target values
        y_pred: Predicted target values
        title: Optional title for the plot
        save_path: Path to save the figure (if None, figure is displayed)

    Returns:
        The matplotlib figure object
    """
    setup_plot_style()

    fig, ax = plt.subplots(
        figsize=PLOT_SETTINGS["figure_size"], dpi=PLOT_SETTINGS["dpi"]
    )

    # Create the scatter plot
    ax.scatter(y_true, y_pred, alpha=0.5)

    # Add the perfect prediction line
    min_val = min(np.min(y_true), np.min(y_pred))
    max_val = max(np.max(y_true), np.max(y_pred))
    ax.plot([min_val, max_val], [min_val, max_val], "r--", label="Perfect prediction")

    # Add labels and title
    ax.set_xlabel("Actual values")
    ax.set_ylabel("Predicted values")
    ax.set_title(title or "Predicted vs Actual Values")

    # Add metrics to the plot
    mae = np.mean(np.abs(y_pred - y_true))
    rmse = np.sqrt(np.mean((y_pred - y_true) ** 2))
    ax.text(
        0.05,
        0.95,
        f"MAE: {mae:.4f}\nRMSE: {rmse:.4f}",
        transform=ax.transAxes,
        verticalalignment="top",
    )

    if save_path:
        plt.savefig(save_path, dpi=PLOT_SETTINGS["dpi"])

    return fig


def plot_error_distribution(y_true, y_pred, title=None, save_path=None):
    """
    Create a histogram of prediction errors.

    Args:
        y_true: True target values
        y_pred: Predicted target values
        title: Optional title for the plot
        save_path: Path to save the figure (if None, figure is displayed)

    Returns:
        The matplotlib figure object
    """
    setup_plot_style()

    errors = y_pred - y_true

    fig, ax = plt.subplots(
        figsize=PLOT_SETTINGS["figure_size"], dpi=PLOT_SETTINGS["dpi"]
    )

    # Create the histogram
    n, bins, patches = ax.hist(
        errors, bins=30, alpha=0.7, color=PLOT_SETTINGS["colors"]["primary"]
    )

    # Add a vertical line at zero error
    ax.axvline(x=0, color="red", linestyle="--", alpha=0.8, label="Zero Error")

    # Add labels and title
    ax.set_xlabel("Prediction Error (y_pred - y_true)")
    ax.set_ylabel("Frequency")
    ax.set_title(title or "Distribution of Prediction Errors")

    # Add statistics
    mean_error = np.mean(errors)
    std_error = np.std(errors)
    ax.text(
        0.02,
        0.95,
        f"Mean Error: {mean_error:.4f}\nStd Dev: {std_error:.4f}",
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=dict(facecolor="white", alpha=0.7),
    )

    ax.legend()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=PLOT_SETTINGS["dpi"])

    return fig


def create_regression_report_plots(y_true, y_pred, output_dir, model_name="model"):
    """
    Create a set of standard regression evaluation plots and save them to the specified directory.

    Args:
        y_true: True target values
        y_pred: Predicted target values
        output_dir: Directory to save plots
        model_name: Name of the model for plot titles and file names

    Returns:
        Dictionary of created figure objects
    """
    os.makedirs(output_dir, exist_ok=True)
    figures = {}

    # Create plots directory
    plots_dir = os.path.join(output_dir, f"{model_name}_plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Calculate errors and percentage errors
    errors = y_pred - y_true
    pct_errors = 100 * errors / np.maximum(1e-10, np.abs(y_true))

    # 1. Scatter plot of actual vs predicted values
    fig1 = plot_predictions_vs_actual(
        y_true,
        y_pred,
        title=f"{model_name}: Predicted vs Actual Values",
        save_path=os.path.join(plots_dir, f"{model_name}_pred_vs_actual.png"),
    )
    figures["pred_vs_actual"] = fig1

    # 2. Error Distribution Plot
    fig2 = plot_error_distribution(
        y_true,
        y_pred,
        title=f"{model_name}: Error Distribution",
        save_path=os.path.join(plots_dir, f"{model_name}_error_distribution.png"),
    )
    figures["error_distribution"] = fig2

    # 3. Error vs Predicted Plot
    fig3, ax3 = plt.subplots(
        figsize=PLOT_SETTINGS["figure_size"], dpi=PLOT_SETTINGS["dpi"]
    )
    ax3.scatter(y_pred, y_pred - y_true, alpha=0.5)
    ax3.axhline(y=0, color="red", linestyle="--")
    ax3.set_xlabel("Predicted Values")
    ax3.set_ylabel("Error (Predicted - Actual)")
    ax3.set_title(f"{model_name}: Error vs Predicted Values")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f"{model_name}_error_vs_predicted.png"))
    figures["error_vs_pred"] = fig3

    # 4. Percentage error vs actual value
    plt.figure(figsize=(10, 6))
    # Filter out extreme percentage errors for better visualization
    filtered_pct = pct_errors[np.abs(pct_errors) < 50]
    plt.scatter(y_true[np.abs(pct_errors) < 50], filtered_pct, alpha=0.5)
    plt.axhline(y=0, color="r", linestyle="--")
    plt.title(f"{model_name}: Percentage Error vs Actual Value")
    plt.xlabel("Actual Value")
    plt.ylabel("Error (%)")
    plt.gca().yaxis.set_major_formatter(PercentFormatter())
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(plots_dir, f"{model_name}_pct_error_vs_actual.png"), dpi=300
    )
    fig4 = plt.gcf()
    figures["pct_error_vs_actual"] = fig4
    plt.close()

    # 5. Histogram of percentage errors
    plt.figure(figsize=(10, 6))
    # Filter out extreme percentage errors for better visualization
    n, bins, patches = plt.hist(
        filtered_pct, bins=30, alpha=0.7, color=PLOT_SETTINGS["colors"]["primary"]
    )
    plt.axvline(x=0, color="r", linestyle="--")
    plt.title(f"{model_name}: Distribution of Percentage Errors")
    plt.xlabel("Error (%)")
    plt.gca().xaxis.set_major_formatter(PercentFormatter())
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(plots_dir, f"{model_name}_pct_error_distribution.png"), dpi=300
    )
    fig5 = plt.gcf()
    figures["pct_error_distribution"] = fig5
    plt.close()

    return figures


def update_plot_settings(new_settings):
    """
    Update the default plot settings with user-provided settings.

    Args:
        new_settings: Dictionary of settings to update

    Example:
        update_plot_settings({
            'figure_size': (10, 6),
            'font_size': 14,
            'colors': {'primary': 'blue'}
        })
    """
    global PLOT_SETTINGS

    # Update top-level settings
    for key, value in new_settings.items():
        if key in PLOT_SETTINGS:
            if isinstance(PLOT_SETTINGS[key], dict) and isinstance(value, dict):
                # Merge nested dictionaries
                PLOT_SETTINGS[key].update(value)
            else:
                # Replace simple values
                PLOT_SETTINGS[key] = value


def visualize_partition_boundaries(
    models,
    X_train,
    y_train,
    partition_mode,
    output_dir=None,
    feature_idx=0,
    title=None,
    show_stats=True,
):
    """
    Create visualizations of partition boundaries for different partition modes.

    Args:
        models: List of trained models (output from train_models_on_partitions)
        X_train: Training features (numpy array)
        y_train: Training targets (numpy array)
        partition_mode: The partition mode used (PartitionMode enum)
        output_dir: Directory to save output plots (if None, plot is only shown)
        feature_idx: Which feature to use for visualization (0-based index)
        title: Custom title for the plot (default: auto-generated based on partition_mode)
        show_stats: Whether to show partition statistics on the plot

    Returns:
        The matplotlib figure object
    """
    setup_plot_style()

    # Set up plotting
    fig, ax = plt.subplots(
        figsize=PLOT_SETTINGS["figure_size"], dpi=PLOT_SETTINGS["dpi"]
    )

    # Extract data for the selected feature
    X_feature = X_train[:, feature_idx]

    # Set up colors for different partitions
    colors = plt.cm.viridis(np.linspace(0, 1, len(models)))

    # Different visualization based on partition type
    if hasattr(partition_mode, "name") and partition_mode.name in ["RANGE", "QUANTILE"]:
        # These partition modes divide the data based on input feature values

        # Sort data points by the selected feature for clearer visualization
        sort_idx = np.argsort(X_feature)
        X_sorted = X_feature[sort_idx]
        y_sorted = y_train[sort_idx]

        # Plot all data points
        ax.scatter(X_sorted, y_sorted, s=2, color="gray", alpha=0.3, label="All data")

        # Get boundaries for visualization
        boundaries = []

        for i, model_info in enumerate(models):
            if "partition_range" in model_info:
                p_range = model_info["partition_range"]
                if p_range[0] is not None:
                    boundaries.append(p_range[0])
                if p_range[1] is not None:
                    boundaries.append(p_range[1])

        # Sort and remove duplicates
        boundaries = sorted(list(set(boundaries)))

        # Plot partition boundaries
        for boundary in boundaries:
            ax.axvline(x=boundary, color="red", linestyle="--", alpha=0.7)

        # Annotate partition ranges
        y_max = np.max(y_train) + 0.1 * (np.max(y_train) - np.min(y_train))

        for i, model_info in enumerate(models):
            if "partition_range" in model_info:
                p_range = model_info["partition_range"]
                min_val = p_range[0] if p_range[0] is not None else np.min(X_feature)
                max_val = p_range[1] if p_range[1] is not None else np.max(X_feature)

                # Add range text
                mid_point = (min_val + max_val) / 2
                ax.text(
                    mid_point,
                    y_max,
                    f"P{i}",
                    horizontalalignment="center",
                    bbox=dict(boxstyle="round,pad=0.3", fc=colors[i], alpha=0.5),
                )

    elif hasattr(partition_mode, "name") and partition_mode.name in [
        "KMEANS",
        "KMEDOIDS",
        "AGGLOMERATIVE",
    ]:
        # For clustering-based partitions, use a scatter plot with the model's predictions

        # Get model predictions to determine cluster assignments
        mask = np.zeros(len(X_train), dtype=bool)

        # Create a colored scatter plot
        for i, model_info in enumerate(models):
            if "cluster_model" in model_info:
                # If we have the actual clustering model, use it
                cluster_model = model_info["cluster_model"]
                if hasattr(cluster_model, "predict"):
                    cluster_assignments = cluster_model.predict(X_train)
                    mask = cluster_assignments == i
            else:
                # Fallback: use the model to predict and check which one gives the best prediction
                if i == 0:
                    # For first model, just take first N samples as approximation
                    partition_size = len(X_train) // len(models)
                    mask = np.zeros(len(X_train), dtype=bool)
                    mask[:partition_size] = True
                else:
                    # For other models, try to estimate assignment using prediction accuracy
                    all_errors = []
                    for j, m_info in enumerate(models):
                        if (
                            "transformer" in m_info
                            and m_info["transformer"] is not None
                        ):
                            X_transformed = m_info["transformer"].transform(X_train)
                            preds = m_info["model"].predict(X_transformed)
                        else:
                            preds = m_info["model"].predict(X_train)
                        errors = np.abs(preds - y_train)
                        all_errors.append(errors)

                    # Find which model gives the lowest error for each sample
                    all_errors = np.column_stack(all_errors)
                    best_model = np.argmin(all_errors, axis=1)
                    mask = best_model == i

            # Plot the data points for this partition
            ax.scatter(
                X_train[mask, feature_idx],
                y_train[mask],
                s=10,
                color=colors[i],
                label=f"Partition {i}",
                alpha=0.7,
            )

    else:
        # For other partition modes, just show the data
        ax.scatter(X_feature, y_train, s=5, alpha=0.5)

    # Set plot labels and title
    ax.set_xlabel(f"Feature {feature_idx}")
    ax.set_ylabel("Target")

    if title:
        ax.set_title(title)
    else:
        ax.set_title(f"Data Partitioning with {partition_mode}")

    # Add stats if requested
    if show_stats:
        partition_counts = [
            f"P{i}: {len([m for m in models if m.get('partition_idx') == i])}"
            for i in range(len(models))
        ]
        stats_str = "\n".join(partition_counts)
        ax.text(
            0.02,
            0.98,
            f"Total Partitions: {len(models)}\n{stats_str if len(partition_counts) < 10 else ''}",
            transform=ax.transAxes,
            va="top",
            bbox=dict(facecolor="white", alpha=0.7),
        )

    ax.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if output_dir:
        # Save the plot
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        plt.savefig(
            os.path.join(output_dir, f"{partition_mode}_boundaries.png"),
            dpi=300,
            bbox_inches="tight",
        )

    return fig


def visualize_results_comparison(results_df, output_dir, metrics=None, top_n=10):
    """
    Visualize comparison of results across different model configurations.

    Args:
        results_df: Dictionary or DataFrame containing results for different configurations
        output_dir: Directory to save plots
        metrics: List of metrics to visualize (default: ['test_r2', 'test_rmse', 'test_mae'])
        top_n: Number of top configurations to highlight

    Returns:
        List of created figure objects
    """
    import numpy as np  # Required for array operations

    # Convert dictionary to DataFrame-like structure if needed
    if not hasattr(results_df, "columns"):
        import pandas as pd

        results_df = pd.DataFrame(results_df)

    os.makedirs(output_dir, exist_ok=True)
    figures = []

    if metrics is None:
        metrics = ["test_r2", "test_rmse", "test_mae"]

    # Ensure metrics exist in the DataFrame
    available_metrics = [m for m in metrics if m in results_df.columns]
    if not available_metrics:
        logger.warning("None of the specified metrics found in results DataFrame")
        return figures

    # Filter out rows with poor performance for better visualization
    if "test_r2" in results_df.columns:
        filtered_df = results_df[results_df["test_r2"] > 0]
    else:
        filtered_df = results_df

    # Create identifier column for each configuration
    if not "config" in filtered_df.columns:
        filtered_df["config"] = filtered_df.apply(
            lambda row: f"{row.get('partition_mode', '')}-{row.get('n_partitions', '')}-{row.get('regressor_type', '')}",
            axis=1,
        )

    # For each metric, create a bar plot of the top configurations
    for metric in available_metrics:
        # Sort by the metric (ascending or descending based on metric)
        ascending = metric.endswith("rmse") or metric.endswith("mae")
        top_configs = filtered_df.sort_values(by=metric, ascending=ascending).head(
            top_n
        )

        plt.figure(figsize=(12, 8))
        colors = plt.cm.viridis(np.linspace(0, 1, len(top_configs)))

        # Create bar plot
        plt.bar(range(len(top_configs)), top_configs[metric], color=colors)
        plt.xticks(
            range(len(top_configs)), top_configs["config"], rotation=45, ha="right"
        )

        plt.title(f"Top {top_n} Configurations by {metric}")
        plt.xlabel("Configuration (Partition-Count-Regressor)")
        plt.ylabel(metric)

        # Add values on top of bars
        for i, v in enumerate(top_configs[metric]):
            plt.text(i, v, f"{v:.4f}", ha="center", va="bottom" if ascending else "top")

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"top_{top_n}_by_{metric}.png"), dpi=300)
        figures.append(plt.gcf())
        plt.close()

    # Create correlation matrix visualization if multiple metrics available
    if len(available_metrics) > 1:
        correlation_matrix = filtered_df[available_metrics].corr()

        plt.figure(figsize=(10, 8))
        plt.imshow(correlation_matrix, cmap="coolwarm", vmin=-1, vmax=1)
        plt.colorbar()

        # Add text annotations
        for i in range(len(correlation_matrix)):
            for j in range(len(correlation_matrix)):
                plt.text(
                    j,
                    i,
                    f"{correlation_matrix.iloc[i, j]:.2f}",
                    ha="center",
                    va="center",
                    color=(
                        "white" if abs(correlation_matrix.iloc[i, j]) > 0.5 else "black"
                    ),
                )

        plt.xticks(
            range(len(correlation_matrix)),
            correlation_matrix.columns,
            rotation=45,
            ha="right",
        )
        plt.yticks(range(len(correlation_matrix)), correlation_matrix.index)
        plt.title("Correlation Between Metrics")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "metrics_correlation.png"), dpi=300)
        figures.append(plt.gcf())
        plt.close()

    # Create scatter plots for pairs of metrics
    if len(available_metrics) >= 2:
        for i, metric1 in enumerate(available_metrics[:-1]):
            for metric2 in available_metrics[i + 1 :]:
                plt.figure(figsize=(10, 6))

                # Create scatter plot with different colors based on category if available
                if "partition_mode" in filtered_df.columns:
                    categories = filtered_df["partition_mode"].unique()
                    for cat_idx, category in enumerate(categories):
                        cat_data = filtered_df[
                            filtered_df["partition_mode"] == category
                        ]
                        plt.scatter(
                            cat_data[metric1],
                            cat_data[metric2],
                            label=category,
                            alpha=0.7,
                            s=100,
                        )
                    plt.legend()
                else:
                    plt.scatter(
                        filtered_df[metric1], filtered_df[metric2], alpha=0.7, s=100
                    )

                plt.title(f"Relationship: {metric1} vs {metric2}")
                plt.xlabel(metric1)
                plt.ylabel(metric2)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(
                    os.path.join(output_dir, f"{metric1}_vs_{metric2}.png"), dpi=300
                )
                figures.append(plt.gcf())
                plt.close()

    # Create box plots for performance by category
    for category in ["partition_mode", "regressor_type"]:
        if category in filtered_df.columns and "test_r2" in filtered_df.columns:
            plt.figure(figsize=(12, 8))

            # Prepare data for box plot
            categories = filtered_df[category].unique()
            data = [
                filtered_df[filtered_df[category] == c]["test_r2"] for c in categories
            ]

            # Create box plot
            plt.boxplot(data, labels=categories)

            plt.title(f'R² Score by {category.replace("_", " ").title()}')
            plt.xlabel(category.replace("_", " ").title())
            plt.ylabel("Test R²")

            if category == "regressor_type":
                plt.xticks(rotation=45, ha="right")

            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"r2_by_{category}.png"), dpi=300)
            figures.append(plt.gcf())
            plt.close()

    return figures


def visualize_partitioned_data(
    X,
    y=None,
    partition_mode=None,
    n_parts=None,
    save_path=None,
    title=None,
    figsize=None,
):
    """
    Create a simple visualization of data with optional partitioning information.

    Args:
        X: Features array (1D or 2D)
        y: Optional target values
        partition_mode: Optional PartitionMode to describe the partitioning
        n_parts: Number of partitions used
        save_path: Path to save the plot
        title: Title for the plot
        figsize: Size of the figure (tuple)
    """
    import matplotlib.pyplot as plt
    import numpy as np

    # Ensure X is 2D
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    if figsize is None:
        figsize = PLOT_SETTINGS["figure_size"]

    fig, ax = plt.subplots(figsize=figsize, dpi=PLOT_SETTINGS["dpi"])

    # Generate title if not provided
    if title is None:
        if partition_mode:
            title = (
                f"Data with {partition_mode.value} partitioning ({n_parts} partitions)"
            )
        else:
            title = "Data Visualization"

    # For 1D features
    if X.shape[1] == 1:
        if y is not None:
            # Scatter plot of X vs y
            ax.scatter(
                X.flatten(),
                y,
                alpha=0.6,
                color=PLOT_SETTINGS["colors"]["primary"],
                s=20,
            )
            ax.set_xlabel("Feature")
            ax.set_ylabel("Target")
        else:
            # Histogram of X values
            ax.hist(
                X.flatten(),
                bins=30,
                alpha=0.7,
                color=PLOT_SETTINGS["colors"]["primary"],
            )
            ax.set_xlabel("Feature")
            ax.set_ylabel("Count")

    # For 2D features
    elif X.shape[1] == 2:
        if y is not None:
            # Scatter plot of X[0] vs X[1], colored by y
            scatter = ax.scatter(X[:, 0], X[:, 1], c=y, alpha=0.6, cmap="viridis")
            plt.colorbar(scatter, ax=ax, label="Target")
        else:
            # Simple scatter plot of X[0] vs X[1]
            ax.scatter(
                X[:, 0], X[:, 1], alpha=0.6, color=PLOT_SETTINGS["colors"]["primary"]
            )
        ax.set_xlabel("Feature 1")
        ax.set_ylabel("Feature 2")

    # For higher dimensional data, just show a pair plot of the first 2 dimensions
    else:
        if y is not None:
            # Scatter plot of first two features, colored by y
            scatter = ax.scatter(X[:, 0], X[:, 1], c=y, alpha=0.6, cmap="viridis")
            plt.colorbar(scatter, ax=ax, label="Target")
        else:
            # Simple scatter plot of first two features
            ax.scatter(
                X[:, 0], X[:, 1], alpha=0.6, color=PLOT_SETTINGS["colors"]["primary"]
            )
        ax.set_xlabel("Feature 1")
        ax.set_ylabel("Feature 2")
        title += " (Showing first 2 dimensions only)"

    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    # Save the plot if a path is provided
    if save_path:
        plt.savefig(save_path)
        plt.close(fig)
        return save_path

    return ax
