#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-12
Description: Example script for generating synthetic data and training models with various partition strategies.

This script demonstrates how to:
1. Generate synthetic data using fit_better's built-in data generation utilities
2. Save logs to data_gen/logs directory
3. Train models with different partition strategies
4. Display detailed partition boundaries and statistics
5. Use fit_better methods throughout the process

Usage:
    python synthetic_partition_example.py [options]

Options:
    --output-dir DIR     Base directory for all outputs (default: data_gen)
    --n-samples INT      Number of samples to generate (default: 10000)
    --model-type STR     Type of synthetic data model (linear, sine, polynomial) (default: sine)
    --noise STD          Noise standard deviation to add to data (default: 0.5)
    --partition-mode     Partition mode to use (default: KMEANS)
    --n-partitions INT   Number of partitions to create (default: 5)
    --regressor-type     Regressor type to use (default: RANDOM_FOREST)
    --n-jobs N           Number of parallel jobs (default: 1)
    --seed INT           Random seed for reproducibility (default: 42)
    --save-plots         Save visualization plots
"""

import os
import sys
import argparse
import logging
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import from fit_better
from fit_better import (
    # Core components
    PartitionMode,
    RegressorType,
    # Data generation utilities
    generate_synthetic_data,
    generate_train_test_data,
    generate_synthetic_data_by_function,
    # Model training and prediction
    train_models_on_partitions,
    predict_with_partitioned_models,
    save_model,
    # Preprocessing
    preprocess_data_for_regression,
    # Utilities
    calc_regression_statistics,
    plot_predictions_vs_actual,
    plot_versus,
    plot_error_distribution,
    create_regression_report_plots,
    # Data handling
    save_data_to_files,
    CSVMgr,
    array_to_csv,
    arrays_to_csv,
    save_xy_data,
    # Logging
    setup_logging,
)


def create_output_directories(base_dir):
    """Create all required output directories."""
    paths = {
        "logs": os.path.join(base_dir, "logs"),
        "data": os.path.join(base_dir, "data"),
        "results": os.path.join(base_dir, "model_results"),
        "plots": os.path.join(base_dir, "plots"),
    }

    # Create directories
    for dir_path in paths.values():
        os.makedirs(dir_path, exist_ok=True)

    return paths


def generate_data(
    data_dir, n_samples=10000, model_type="sine", noise_std=0.5, seed=42, n_features=3
):
    """
    Generate synthetic training and test datasets using fit_better's utilities.

    Args:
        data_dir: Directory to save data files
        n_samples: Number of samples to generate for each dataset
        model_type: Type of model to generate data for (linear, sine, polynomial)
        noise_std: Standard deviation of noise to add
        seed: Random seed for reproducibility
        n_features: Number of input features to generate

    Returns:
        X_train, y_train, X_test, y_test as numpy arrays
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Generating synthetic {model_type} data with {n_samples} samples")

    # Paths for numpy arrays
    X_train_path = os.path.join(data_dir, "X_train.npy")
    y_train_path = os.path.join(data_dir, "y_train.npy")
    X_test_path = os.path.join(data_dir, "X_test.npy")
    y_test_path = os.path.join(data_dir, "y_test.npy")

    # Generate synthetic data with multiple features using built-in function
    if model_type == "linear":
        # Create a function to generate multi-feature linear data
        def linear_function(X):
            return 2.0 * X[:, 0] - 1.5 * X[:, 1] + 0.5 * X[:, 2] + 1.0

        X_train, X_test, y_train, y_test = generate_synthetic_data_by_function(
            function=linear_function,
            n_samples_train=n_samples,
            n_samples_test=int(n_samples * 0.3),
            n_features=n_features,
            noise_std=noise_std,
            add_outliers=True,
            random_state=seed,
        )

    elif model_type == "sine":
        # Create a function to generate multi-feature sine data
        def sine_function(X):
            return 3.0 * np.sin(2.0 * X[:, 0] + 0.5) + 1.5 * np.cos(X[:, 1]) - X[:, 2]

        X_train, X_test, y_train, y_test = generate_synthetic_data_by_function(
            function=sine_function,
            n_samples_train=n_samples,
            n_samples_test=int(n_samples * 0.3),
            n_features=n_features,
            noise_std=noise_std,
            add_outliers=True,
            random_state=seed,
        )

    elif model_type == "polynomial":
        # Create a function to generate multi-feature polynomial data
        def polynomial_function(X):
            return (
                0.5 * X[:, 0] ** 3
                - 1.2 * X[:, 0] ** 2
                + 2.0 * X[:, 0]
                + 0.7 * X[:, 1] ** 2
                - 1.1 * X[:, 1]
                + 0.3 * X[:, 2]
            )

        X_train, X_test, y_train, y_test = generate_synthetic_data_by_function(
            function=polynomial_function,
            n_samples_train=n_samples,
            n_samples_test=int(n_samples * 0.3),
            n_features=n_features,
            noise_std=noise_std,
            add_outliers=True,
            random_state=seed,
        )

    else:
        raise ValueError(f"Unknown model type: {model_type}")

    # Save the generated data
    np.save(X_train_path, X_train)
    np.save(y_train_path, y_train)
    np.save(X_test_path, X_test)
    np.save(y_test_path, y_test)

    logger.info(f"Data shapes: X_train {X_train.shape}, X_test {X_test.shape}")

    # Also save as CSV for easier inspection using fit_better's utilities

    # Option 1: Using save_data_to_files for all files at once
    save_data_to_files(
        output_dir=data_dir,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        format="csv",
        include_header=True,
    )

    # Option 2: Alternative way to save results with custom headers using save_xy_data
    feature_headers = [f"Feature_{i+1}" for i in range(X_train.shape[1])]
    CSVMgr.save_xy_data(
        X=X_train,
        y=y_train,
        x_filepath=os.path.join(data_dir, "X_train_with_headers.csv"),
        y_filepath=os.path.join(data_dir, "y_train_with_headers.csv"),
        x_headers=feature_headers,
        y_header="Target",
        include_header=True,
    )

    return X_train, y_train, X_test, y_test


def visualize_partition_boundaries(
    models, X_train, y_train, partition_mode, output_dir=None, feature_idx=0
):
    """
    Create visualizations of partition boundaries for different partition modes.

    Args:
        models: List of trained models
        X_train: Training features
        y_train: Training targets
        partition_mode: The partition mode used
        output_dir: Directory to save output plots
        feature_idx: Which feature to use for visualization (0-based index)
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Visualizing partition boundaries for {partition_mode}")

    # Set up plotting
    plt.figure(figsize=(12, 8))

    # Extract data for the selected feature
    X_feature = X_train[:, feature_idx]

    # Set up colors for different partitions
    colors = plt.cm.viridis(np.linspace(0, 1, len(models)))

    # Different visualization based on partition type
    if (
        partition_mode == PartitionMode.RANGE
        or partition_mode == PartitionMode.QUANTILE
    ):
        # These partition modes divide the data based on input feature values

        # Sort data points by the selected feature for clearer visualization
        sort_idx = np.argsort(X_feature)
        X_sorted = X_feature[sort_idx]
        y_sorted = y_train[sort_idx]

        # Plot all data points
        plt.scatter(X_sorted, y_sorted, s=2, color="gray", alpha=0.3, label="All data")

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
            plt.axvline(x=boundary, color="red", linestyle="--", alpha=0.7)

        # Annotate partition ranges
        y_max = np.max(y_train) + 0.1 * (np.max(y_train) - np.min(y_train))

        for i, model_info in enumerate(models):
            if "partition_range" in model_info:
                p_range = model_info["partition_range"]
                min_val = p_range[0] if p_range[0] is not None else np.min(X_feature)
                max_val = p_range[1] if p_range[1] is not None else np.max(X_feature)

                # Add range text
                mid_point = (min_val + max_val) / 2
                plt.text(
                    mid_point,
                    y_max,
                    f"P{i}",
                    horizontalalignment="center",
                    bbox=dict(boxstyle="round,pad=0.3", fc=colors[i], alpha=0.5),
                )

    elif partition_mode in [PartitionMode.KMEANS, PartitionMode.KMEDOIDS]:
        # For clustering-based partitions, use a scatter plot with the model's predictions

        # Get model predictions to determine cluster assignments
        y_pred = np.zeros_like(y_train)
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
            plt.scatter(
                X_train[mask, feature_idx],
                y_train[mask],
                s=10,
                color=colors[i],
                label=f"Partition {i}",
                alpha=0.7,
            )

    else:
        # For other partition modes, just show the data
        plt.scatter(X_feature, y_train, s=5, alpha=0.5)

    # Set plot labels and title
    plt.xlabel(f"Feature {feature_idx}")
    plt.ylabel("Target")
    plt.title(f"Data Partitioning with {partition_mode}")
    plt.legend()
    plt.grid(True, alpha=0.3)

    if output_dir:
        # Save the plot
        plt.savefig(
            os.path.join(output_dir, f"{partition_mode}_boundaries.png"),
            dpi=300,
            bbox_inches="tight",
        )

    plt.close()


def print_partition_statistics(
    models, X_train, y_train, X_test, y_test, partition_mode, regressor_type
):
    """
    Print detailed statistics and boundaries for each partition.

    Args:
        models: List of trained models
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        partition_mode: Partition mode used
        regressor_type: Regressor type used
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Analyzing {len(models)} partitions using {partition_mode}")

    # Extract partition boundaries and details
    partition_info = []

    for idx, model_info in enumerate(models):
        # Get partition range
        if "partition_range" in model_info:
            p_range = model_info["partition_range"]
        else:
            # Default range (approximation for missing range info)
            p_range = (None, None)

            # For range-based partitions with known structure
            if partition_mode == PartitionMode.RANGE:
                # Approximate ranges based on partition index and count
                partition_count = len(models)
                min_value = np.min(X_train[:, 0])
                max_value = np.max(X_train[:, 0])
                step = (max_value - min_value) / partition_count

                # Calculate approximate range
                if idx == 0:
                    p_range = (None, min_value + step)
                elif idx == partition_count - 1:
                    p_range = (min_value + step * idx, None)
                else:
                    p_range = (min_value + step * idx, min_value + step * (idx + 1))

        # Get the specific model type if available
        model_name = str(regressor_type)
        if hasattr(model_info["model"], "__class__"):
            model_name = model_info["model"].__class__.__name__

        # Get additional partition information if available
        extra_info = {}

        # For clustering partitions, try to get the cluster centers
        if partition_mode in [PartitionMode.KMEANS, PartitionMode.KMEDOIDS]:
            if "cluster_model" in model_info:
                cluster_model = model_info["cluster_model"]
                if hasattr(cluster_model, "cluster_centers_"):
                    extra_info["center"] = cluster_model.cluster_centers_[idx]

        # Record hyperparameters or important model attributes
        if hasattr(model_info["model"], "get_params"):
            try:
                params = model_info["model"].get_params()
                important_params = {}

                # Filter to keep only the most useful parameters depending on model type
                if model_name.lower().find("randomforest") >= 0:
                    important_params = {
                        "n_estimators": params.get("n_estimators", "N/A"),
                        "max_depth": params.get("max_depth", "N/A"),
                        "min_samples_leaf": params.get("min_samples_leaf", "N/A"),
                    }
                elif model_name.lower().find("linear") >= 0:
                    if hasattr(model_info["model"], "coef_"):
                        important_params["coefficients"] = model_info["model"].coef_
                elif (
                    model_name.lower().find("gbdt") >= 0
                    or model_name.lower().find("boost") >= 0
                ):
                    important_params = {
                        "n_estimators": params.get("n_estimators", "N/A"),
                        "learning_rate": params.get("learning_rate", "N/A"),
                    }

                if important_params:
                    extra_info["params"] = important_params
            except Exception as e:
                logger.warning(f"Could not extract model parameters: {str(e)}")

        # Store information about any preprocessing transformer
        if "transformer" in model_info and model_info["transformer"] is not None:
            transformer = model_info["transformer"]
            transformer_type = transformer.__class__.__name__
            extra_info["transformer"] = transformer_type

            # Extract transformer parameters if available
            if hasattr(transformer, "get_params"):
                try:
                    t_params = transformer.get_params()
                    extra_info["transformer_params"] = t_params
                except Exception as e:
                    logger.warning(
                        f"Could not extract transformer parameters: {str(e)}"
                    )

        partition_info.append(
            {
                "idx": idx,
                "range": p_range,
                "model": model_info["model"],
                "model_name": model_name,
                "transformer": model_info.get("transformer", None),
                "extra_info": extra_info,
            }
        )

    # Sort by partition index
    partition_info.sort(key=lambda x: x["idx"])

    # Prepare for consolidated statistics
    consolidated_stats = []

    # For each partition, calculate statistics
    for info in partition_info:
        # Get partition range
        p_min, p_max = info["range"]

        # Count data points in this partition for training data
        if partition_mode in [PartitionMode.KMEANS, PartitionMode.KMEDOIDS]:
            # For clustering-based partitions
            if "cluster_model" in models[info["idx"]]:
                cluster_model = models[info["idx"]]["cluster_model"]
                if hasattr(cluster_model, "predict"):
                    # If we can use the model's predict method to get cluster assignments
                    train_predictions = cluster_model.predict(X_train)
                    train_mask = train_predictions == info["idx"]

                    test_predictions = cluster_model.predict(X_test)
                    test_mask = test_predictions == info["idx"]
                else:
                    # Fallback method
                    total_partitions = len(partition_info)
                    sorted_indices = np.argsort(X_train[:, 0])
                    partition_size = len(sorted_indices) // total_partitions

                    start_idx = info["idx"] * partition_size
                    end_idx = (
                        (info["idx"] + 1) * partition_size
                        if info["idx"] < total_partitions - 1
                        else len(sorted_indices)
                    )

                    train_mask = np.zeros(len(X_train), dtype=bool)
                    train_mask[sorted_indices[start_idx:end_idx]] = True

                    # Do the same for test data
                    sorted_test_indices = np.argsort(X_test[:, 0])
                    test_partition_size = len(sorted_test_indices) // total_partitions
                    test_start_idx = info["idx"] * test_partition_size
                    test_end_idx = (
                        (info["idx"] + 1) * test_partition_size
                        if info["idx"] < total_partitions - 1
                        else len(sorted_test_indices)
                    )
                    test_mask = np.zeros(len(X_test), dtype=bool)
                    test_mask[sorted_test_indices[test_start_idx:test_end_idx]] = True
            else:
                # Fallback method if no cluster model is available
                total_partitions = len(partition_info)
                sorted_indices = np.argsort(X_train[:, 0])
                partition_size = len(sorted_indices) // total_partitions

                start_idx = info["idx"] * partition_size
                end_idx = (
                    (info["idx"] + 1) * partition_size
                    if info["idx"] < total_partitions - 1
                    else len(sorted_indices)
                )

                train_mask = np.zeros(len(X_train), dtype=bool)
                train_mask[sorted_indices[start_idx:end_idx]] = True

                # Do the same for test data
                sorted_test_indices = np.argsort(X_test[:, 0])
                test_partition_size = len(sorted_test_indices) // total_partitions
                test_start_idx = info["idx"] * test_partition_size
                test_end_idx = (
                    (info["idx"] + 1) * test_partition_size
                    if info["idx"] < total_partitions - 1
                    else len(sorted_test_indices)
                )
                test_mask = np.zeros(len(X_test), dtype=bool)
                test_mask[sorted_test_indices[test_start_idx:test_end_idx]] = True
        else:
            # For range-based partitions
            if p_min is None and p_max is not None:
                train_mask = X_train[:, 0] <= p_max
                test_mask = X_test[:, 0] <= p_max
            elif p_max is None and p_min is not None:
                train_mask = X_train[:, 0] > p_min
                test_mask = X_test[:, 0] > p_min
            elif p_min is not None and p_max is not None:
                train_mask = (X_train[:, 0] > p_min) & (X_train[:, 0] <= p_max)
                test_mask = (X_test[:, 0] > p_min) & (X_test[:, 0] <= p_max)
            else:
                # Both p_min and p_max are None, include all data points
                train_mask = np.ones(len(X_train), dtype=bool)
                test_mask = np.ones(len(X_test), dtype=bool)

        train_count = np.sum(train_mask)
        test_count = np.sum(test_mask)

        # Format the range for display as actual boundary values
        min_str = f"{p_min:.4f}" if p_min is not None else "Min"
        max_str = f"{p_max:.4f}" if p_max is not None else "Max"
        range_str = f"{min_str} - {max_str}"

        # Add additional info if available
        extra_display = ""
        if "extra_info" in info and info["extra_info"]:
            if "center" in info["extra_info"]:
                centers = info["extra_info"]["center"]
                if len(centers) <= 3:  # Limit to first 3 dimensions for display
                    center_str = ", ".join([f"{c:.4f}" for c in centers])
                    extra_display += f" | Center: [{center_str}]"
                else:
                    center_str = ", ".join([f"{c:.4f}" for c in centers[:3]])
                    extra_display += f" | Center: [{center_str}, ...]"

        # Initialize stats dictionary
        stats = {
            "partition": f"P{info['idx']}",
            "range": range_str + extra_display,
            "model_name": info["model_name"],
            "train_count": train_count,
            "test_count": test_count,
            "train_metrics": None,
            "test_metrics": None,
        }

        # Calculate statistics for training data if there are data points
        if train_count > 0:
            X_train_part = X_train[train_mask]
            y_train_part = y_train[train_mask]
            # Use the model to predict
            if info["transformer"] is not None:
                X_train_part_transformed = info["transformer"].transform(X_train_part)
                y_train_pred_part = info["model"].predict(X_train_part_transformed)
            else:
                y_train_pred_part = info["model"].predict(X_train_part)

            # Calculate metrics
            stats["train_metrics"] = calc_regression_statistics(
                y_train_part, y_train_pred_part
            )
        else:
            stats["train_metrics"] = {
                "mae": float("nan"),
                "rmse": float("nan"),
                "r2": float("nan"),
                "pct_within_3pct": 0,
            }

        # Calculate statistics for test data if there are data points
        if test_count > 0:
            X_test_part = X_test[test_mask]
            y_test_part = y_test[test_mask]
            # Use the model to predict
            if info["transformer"] is not None:
                X_test_part_transformed = info["transformer"].transform(X_test_part)
                y_test_pred_part = info["model"].predict(X_test_part_transformed)
            else:
                y_test_pred_part = info["model"].predict(X_test_part)

            # Calculate metrics
            stats["test_metrics"] = calc_regression_statistics(
                y_test_part, y_test_pred_part
            )
        else:
            stats["test_metrics"] = {
                "mae": float("nan"),
                "rmse": float("nan"),
                "r2": float("nan"),
                "pct_within_3pct": 0,
            }

        consolidated_stats.append(stats)

    # Print summary header
    logger.info(f"\nPartition Statistics Summary ({partition_mode}, {regressor_type}):")

    # Print partition boundaries and sample counts
    logger.info("\nPartition Boundaries and Sample Distribution:")
    for stat in consolidated_stats:
        logger.info(f"Partition {stat['partition']}: {stat['range']}")
        logger.info(
            f"  Training Samples: {stat['train_count']} ({stat['train_count']/len(X_train):.1%})"
        )
        logger.info(
            f"  Test Samples: {stat['test_count']} ({stat['test_count']/len(X_test):.1%})"
        )

    # Print model details
    logger.info("\nModel Details by Partition:")
    for idx, info in enumerate(partition_info):
        logger.info(f"Partition {idx}: {info['model_name']}")

        # Print model hyperparameters if available
        if "extra_info" in info and "params" in info["extra_info"]:
            params = info["extra_info"]["params"]
            for param_name, param_value in params.items():
                if param_name == "coefficients" and isinstance(param_value, np.ndarray):
                    if len(param_value) <= 5:
                        logger.info(f"  {param_name}: {param_value}")
                    else:
                        logger.info(f"  {param_name}: {param_value[:5]}...")
                else:
                    logger.info(f"  {param_name}: {param_value}")

        # Print transformer info if available
        if "extra_info" in info and "transformer" in info["extra_info"]:
            logger.info(f"  Transformer: {info['extra_info']['transformer']}")

    # Create and print a metrics table
    logger.info("\nPerformance Metrics by Partition:")
    header = "| Partition | Train Count | Train MAE | Train RMSE | Train R² | Train Within 3% | Test Count | Test MAE | Test RMSE | Test R² | Test Within 3% |"
    separator = "|" + "-" * (len(header) - 2) + "|"

    logger.info(separator)
    logger.info(header)
    logger.info(separator)

    for stat in consolidated_stats:
        row = (
            f"| {stat['partition']} | "
            f"{stat['train_count']:^11} | "
            f"{stat['train_metrics']['mae']:^9.4f} | "
            f"{stat['train_metrics']['rmse']:^10.4f} | "
            f"{stat['train_metrics']['r2']:^8.4f} | "
            f"{stat['train_metrics'].get('pct_within_3pct', 0):^15.2f}% | "
            f"{stat['test_count']:^10} | "
            f"{stat['test_metrics']['mae']:^8.4f} | "
            f"{stat['test_metrics']['rmse']:^9.4f} | "
            f"{stat['test_metrics']['r2']:^7.4f} | "
            f"{stat['test_metrics'].get('pct_within_3pct', 0):^14.2f}% |"
        )
        logger.info(row)

    logger.info(separator)


def train_and_evaluate_models(
    X_train,
    y_train,
    X_test,
    y_test,
    partition_mode,
    n_partitions,
    regressor_type,
    n_jobs=1,
    output_dir=None,
    save_plots=False,
):
    """
    Train models with the specified partition mode and regressor type, and evaluate them.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        partition_mode: Partition mode to use
        n_partitions: Number of partitions to create
        regressor_type: Regressor type to use
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
        save_plots: Whether to save visualization plots

    Returns:
        Dictionary with models, predictions, and metrics
    """
    logger = logging.getLogger(__name__)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        plots_dir = os.path.join(output_dir, "plots")
        os.makedirs(plots_dir, exist_ok=True)

    logger.info(
        f"Training models with {partition_mode} partitioning and {regressor_type} regressor..."
    )

    # Train models on partitions
    models = train_models_on_partitions(
        X_train,
        y_train,
        partition_mode=partition_mode,
        n_partitions=n_partitions,
        regressor_type=regressor_type,
        n_jobs=n_jobs,
    )

    # Get actual number of partitions
    actual_n_parts = len(models)
    logger.info(f"Created {actual_n_parts} partitions")

    # Print partition boundaries and statistics
    print_partition_statistics(
        models, X_train, y_train, X_test, y_test, partition_mode, regressor_type
    )

    # Visualize partition boundaries
    if save_plots:
        visualize_partition_boundaries(
            models,
            X_train,
            y_train,
            partition_mode,
            output_dir=os.path.join(output_dir, "plots") if output_dir else None,
        )

    # Make predictions on training data
    logger.info("Making predictions on training data...")
    y_train_pred = predict_with_partitioned_models(models, X_train, n_jobs=n_jobs)

    # Make predictions on test data
    logger.info("Making predictions on test data...")
    y_test_pred = predict_with_partitioned_models(models, X_test, n_jobs=n_jobs)

    # Calculate metrics for training data
    train_metrics = calc_regression_statistics(y_train, y_train_pred)

    # Calculate metrics for test data
    test_metrics = calc_regression_statistics(y_test, y_test_pred)

    # Print summary metrics
    logger.info("\nOverall Model Performance:")
    logger.info(
        f"Training: MAE={train_metrics['mae']:.4f}, RMSE={train_metrics['rmse']:.4f}, R²={train_metrics['r2']:.4f}, Within 3%={train_metrics.get('pct_within_3pct', 0):.2f}%"
    )
    logger.info(
        f"Test: MAE={test_metrics['mae']:.4f}, RMSE={test_metrics['rmse']:.4f}, R²={test_metrics['r2']:.4f}, Within 3%={test_metrics.get('pct_within_3pct', 0):.2f}%"
    )

    # Save results and visualizations if output directory provided
    if output_dir and save_plots:
        logger.info("Generating plots...")

        # Create comprehensive regression report plots
        create_regression_report_plots(
            y_train,
            y_train_pred,
            y_test,
            y_test_pred,
            title_prefix=f"{partition_mode} with {actual_n_parts} partitions ({regressor_type})",
            save_dir=os.path.join(output_dir, "plots"),
        )

    # Save the trained models if output directory is provided
    if output_dir:
        model_save_path = os.path.join(
            output_dir, f"{partition_mode}_{regressor_type}_model.pkl"
        )
        save_model(models, model_save_path)
        logger.info(f"Model saved to {model_save_path}")

    # Return results
    return {
        "models": models,
        "n_partitions": actual_n_parts,
        "train_predictions": y_train_pred,
        "test_predictions": y_test_pred,
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
    }


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate synthetic data and train models with various partition strategies"
    )

    # Base directory
    tests_dir = Path(__file__).resolve().parent.parent
    default_output_dir = str(tests_dir / "data_gen")

    parser.add_argument(
        "--output-dir",
        type=str,
        default=default_output_dir,
        help="Base directory for all outputs",
    )
    parser.add_argument(
        "--n-samples", type=int, default=10000, help="Number of samples to generate"
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="sine",
        choices=["linear", "sine", "polynomial"],
        help="Type of synthetic data model",
    )
    parser.add_argument(
        "--noise",
        type=float,
        default=0.5,
        help="Noise standard deviation to add to data",
    )
    parser.add_argument(
        "--partition-mode",
        type=str,
        default="KMEANS",
        choices=[mode.name for mode in PartitionMode],
        help="Partition mode to use",
    )
    parser.add_argument(
        "--n-partitions", type=int, default=5, help="Number of partitions to create"
    )
    parser.add_argument(
        "--regressor-type",
        type=str,
        default="RANDOM_FOREST",
        choices=[regressor.name for regressor in RegressorType],
        help="Regressor type to use",
    )
    parser.add_argument("--n-jobs", type=int, default=1, help="Number of parallel jobs")
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--save-plots", action="store_true", help="Save visualization plots"
    )

    args = parser.parse_args()

    try:
        # Create output directories
        paths = create_output_directories(args.output_dir)

        # Set up logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(
            paths["logs"],
            f"{args.partition_mode}_{args.regressor_type}_{timestamp}.log",
        )
        logger = setup_logging(log_file, level=logging.INFO)

        logger.info(f"Starting synthetic data generation and model training")
        logger.info(f"Configuration: {vars(args)}")

        # Generate synthetic data
        X_train, y_train, X_test, y_test = generate_data(
            paths["data"],
            n_samples=args.n_samples,
            model_type=args.model_type,
            noise_std=args.noise,
            seed=args.seed,
        )

        # Preprocess the data if needed (handle string or categorical features)
        X_train, X_test, _ = preprocess_data_for_regression(
            X_train, X_test, categorical_encode_method="onehot"
        )

        # Convert partition mode and regressor type strings to enum values
        partition_mode = PartitionMode[args.partition_mode]
        regressor_type = RegressorType[args.regressor_type]

        # Train and evaluate models
        results = train_and_evaluate_models(
            X_train,
            y_train,
            X_test,
            y_test,
            partition_mode,
            args.n_partitions,
            regressor_type,
            n_jobs=args.n_jobs,
            output_dir=paths["results"],
            save_plots=args.save_plots,
        )

        logger.info(f"Process completed successfully!")

    except Exception as e:
        logger.error(f"Error in execution: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
