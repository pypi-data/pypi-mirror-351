"""
Utility module for model evaluation.

This module combines functionality from partition_and_regressor_example.py and
best_partition_and_regressor_example.py to provide a unified interface for
model training, evaluation, and comparison.

Usage:
    from tests.utils.model_evaluation import train_and_evaluate_model, find_best_model
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime
from time import time
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Union, Optional, Any

from fit_better import (
    PartitionMode,
    RegressorType,
    RegressionFlow,
    train_models_on_partitions,
    predict_with_partitioned_models,
    save_model,
    calc_regression_statistics,
    create_regression_report_plots,
    CSVMgr,
    preprocess_data_for_regression,
)
from fit_better.utils.statistics import print_partition_statistics
from fit_better.utils.ascii import print_ascii_table
from fit_better.utils.plotting import visualize_partition_boundaries

# Import preprocessing modules
from sklearn.impute import SimpleImputer

# Set up logger (will be configured by the calling script)
import logging

logger = logging.getLogger(__name__)


def preprocess_data(
    X_train,
    y_train,
    X_test,
    y_test,
    impute_strategy="mean",
    impute_value=0,
    drop_na=False,
):
    """
    Preprocess the data by handling missing values and scaling features.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        impute_strategy: Strategy for imputing missing values ('mean', 'median', 'most_frequent', 'constant')
        impute_value: Value to use with 'constant' imputation strategy
        drop_na: Whether to drop rows with any NaN values

    Returns:
        Processed X_train, y_train, X_test, y_test
    """
    # Process categorical features
    logger.info("Preprocessing data...")
    X_train_processed, X_test_processed, encoder = preprocess_data_for_regression(
        X_train, X_test, categorical_encode_method="onehot"
    )

    # If we had categorical features, use the processed data
    if encoder is not None:
        logger.info(f"Processed categorical features with {type(encoder).__name__}")
        X_train = X_train_processed
        X_test = X_test_processed

    # Handle NaN values
    train_nas = np.isnan(X_train).sum().sum()
    test_nas = np.isnan(X_test).sum().sum()
    train_y_nas = np.isnan(y_train).sum()
    test_y_nas = np.isnan(y_test).sum()

    if train_nas > 0 or test_nas > 0 or train_y_nas > 0 or test_y_nas > 0:
        logger.info(
            f"Found NaN values: X_train: {train_nas}, X_test: {test_nas}, y_train: {train_y_nas}, y_test: {test_y_nas}"
        )

    if drop_na:
        # Drop rows with NaN values
        logger.info("Dropping rows with NaN values...")
        train_mask = ~np.isnan(X_train).any(axis=1) & ~np.isnan(y_train).any(axis=1)
        test_mask = ~np.isnan(X_test).any(axis=1) & ~np.isnan(y_test).any(axis=1)

        X_train = X_train[train_mask]
        y_train = y_train[train_mask]
        X_test = X_test[test_mask]
        y_test = y_test[test_mask]

        logger.info(
            f"After dropping: X_train {X_train.shape}, y_train {y_train.shape}, X_test {X_test.shape}, y_test {y_test.shape}"
        )
    else:
        # Impute missing values
        logger.info(f"Imputing missing values using '{impute_strategy}' strategy...")

        # Impute X_train and X_test
        if impute_strategy == "constant":
            imputer = SimpleImputer(strategy=impute_strategy, fill_value=impute_value)
        else:
            imputer = SimpleImputer(strategy=impute_strategy)

        if train_nas > 0 or test_nas > 0:
            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

        # Impute y_train and y_test if needed
        if train_y_nas > 0 or test_y_nas > 0:
            y_imputer = SimpleImputer(strategy=impute_strategy)
            y_train = y_imputer.fit_transform(y_train.reshape(-1, 1)).ravel()
            y_test = y_imputer.transform(y_test.reshape(-1, 1)).ravel()

    # Check for remaining NaN values
    if np.isnan(X_train).sum().sum() > 0 or np.isnan(X_test).sum().sum() > 0:
        raise ValueError(
            "Still found NaN values after preprocessing. Please check your data or preprocessing steps."
        )

    if np.isnan(y_train).sum() > 0 or np.isnan(y_test).sum() > 0:
        raise ValueError(
            "Still found NaN values in target data after preprocessing. Please check your data or preprocessing steps."
        )

    return X_train, y_train, X_test, y_test


def train_and_evaluate_model(
    X_train,
    y_train,
    X_test,
    y_test,
    partition_mode,
    n_partitions,
    regressor_type,
    n_jobs=1,
    output_dir=None,
    save_predictions=False,
    use_regression_flow=False,
    impute_strategy="mean",
    impute_value=0,
    drop_na=False,
) -> Dict[str, Any]:
    """
    Train and evaluate a model with the specified configuration.

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
        save_predictions: Whether to save predictions to CSV files
        use_regression_flow: Whether to use RegressionFlow for training
        impute_strategy: Strategy for imputing missing values
        impute_value: Value to use with 'constant' imputation strategy
        drop_na: Whether to drop rows with NaN values

    Returns:
        Dictionary with results
    """
    # Create output directories if necessary
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        if output_dir:
            plots_dir = os.path.join(output_dir, "plots")
            os.makedirs(plots_dir, exist_ok=True)

    # Preprocess data
    X_train, y_train, X_test, y_test = preprocess_data(
        X_train, y_train, X_test, y_test, impute_strategy, impute_value, drop_na
    )

    # Train and evaluate model
    if use_regression_flow:
        # Use RegressionFlow API
        flow = RegressionFlow()
        result = flow.find_best_strategy(
            X_train,
            y_train,
            X_test,
            y_test,
            partition_modes=[partition_mode],
            regressor_types=[regressor_type],
            n_partitions=n_partitions,
            n_jobs=n_jobs,
        )

        # Extract results
        metrics = result.metrics
        y_pred_test = flow.predict(X_test)
        y_pred_train = flow.predict(X_train)

        # Return results
        return {
            "model": result.model,
            "metrics": metrics,
            "y_pred_test": y_pred_test,
            "y_pred_train": y_pred_train,
            "partition_mode": partition_mode,
            "regressor_type": regressor_type,
            "n_partitions": n_partitions,
        }
    else:
        # Use standard API
        result = train_models_on_partitions(
            X_train,
            y_train,
            partition_mode=partition_mode,
            n_partitions=n_partitions,
            regressor_type=regressor_type,
            n_jobs=n_jobs,
        )

        # Handle both tuple and dict returns from train_models_on_partitions
        if isinstance(result, tuple):
            models, partitioner = result
        else:
            models = result.get("models", [])
            partitioner = result.get("partitioner", None)

        # Make predictions
        y_pred_test = predict_with_partitioned_models(models, X_test, partitioner)
        y_pred_train = predict_with_partitioned_models(models, X_train, partitioner)

        # Calculate metrics
        metrics = calc_regression_statistics(y_test, y_pred_test)

        # Save predictions if requested
        if save_predictions and output_dir:
            train_df = pd.DataFrame({"y_true": y_train, "y_pred": y_pred_train})
            test_df = pd.DataFrame({"y_true": y_test, "y_pred": y_pred_test})
            train_df.to_csv(
                os.path.join(output_dir, "train_predictions.csv"), index=False
            )
            test_df.to_csv(
                os.path.join(output_dir, "test_predictions.csv"), index=False
            )

        # Create plots if 1D data
        if X_train.shape[1] == 1 and output_dir:
            plots_dir = os.path.join(output_dir, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            # Create plots for training predictions
            create_regression_report_plots(
                y_true=y_train,
                y_pred=y_pred_train,
                output_dir=plots_dir,
                model_name=f"{partition_mode.name}_{regressor_type.name}_train",
            )
            # Create plots for test predictions
            create_regression_report_plots(
                y_true=y_test,
                y_pred=y_pred_test,
                output_dir=plots_dir,
                model_name=f"{partition_mode.name}_{regressor_type.name}_test",
            )

        # Return results
        return {
            "models": models,
            "partitioner": partitioner,
            "metrics": metrics,
            "y_pred_test": y_pred_test,
            "y_pred_train": y_pred_train,
            "partition_mode": partition_mode,
            "regressor_type": regressor_type,
            "n_partitions": n_partitions,
        }


def find_best_model(
    X_train,
    y_train,
    X_test,
    y_test,
    partition_modes=None,
    regressor_types=None,
    partition_counts=None,
    n_jobs=1,
    output_dir=None,
    test_mode=False,
) -> Dict[str, Any]:
    """
    Find the best model by trying different combinations of partition modes and regressor types.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        partition_modes: List of partition modes to try
        regressor_types: List of regressor types to try
        partition_counts: List of partition counts to try
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
        test_mode: Whether to run in test mode with fewer combinations

    Returns:
        Dictionary with the best model and its results
    """
    # Set default values
    if partition_modes is None:
        partition_modes = [
            PartitionMode.RANGE,
            PartitionMode.PERCENTILE,
            PartitionMode.KMEANS,
            PartitionMode.NONE,
        ]

    if regressor_types is None:
        regressor_types = [
            RegressorType.LINEAR,
            RegressorType.POLYNOMIAL_2,
            RegressorType.RANDOM_FOREST,
        ]

    if partition_counts is None:
        partition_counts = [3, 5, 8]

    # Initialize best model tracking
    best_r2 = -float("inf")
    best_model_results = None

    # Use RegressionFlow for an efficient search
    flow = RegressionFlow()
    result = flow.find_best_strategy(
        X_train,
        y_train,
        X_test,
        y_test,
        partition_modes=partition_modes,
        regressor_types=regressor_types,
        n_partitions=partition_counts[0] if len(partition_counts) == 1 else None,
        n_jobs=n_jobs,
    )

    # Save results to output directory if provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        # Save model results summary
        summary_df = pd.DataFrame(
            {
                "metric": list(result.metrics.keys()),
                "value": list(result.metrics.values()),
            }
        )
        summary_df.to_csv(
            os.path.join(output_dir, "best_model_metrics.csv"), index=False
        )

        # Create plots if 1D data
        if X_train.shape[1] == 1:
            plots_dir = os.path.join(output_dir, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            y_pred_test = flow.predict(X_test)
            y_pred_train = flow.predict(X_train)

            # Create plots for training predictions
            create_regression_report_plots(
                y_true=y_train,
                y_pred=y_pred_train,
                output_dir=plots_dir,
                model_name=f"{result.partition_mode.name}_{result.model_type.name}_train",
            )
            # Create plots for test predictions
            create_regression_report_plots(
                y_true=y_test,
                y_pred=y_pred_test,
                output_dir=plots_dir,
                model_name=f"{result.partition_mode.name}_{result.model_type.name}_test",
            )

    return {
        "model": result.model,
        "metrics": result.metrics,
        "partition_mode": result.partition_mode,
        "regressor_type": result.model_type,
        "n_partitions": result.n_partitions,
    }


def save_predictions_to_csv(y_train, y_train_pred, y_test, y_test_pred, output_dir):
    """
    Save predictions to CSV files.

    Args:
        y_train: Training targets
        y_train_pred: Training predictions
        y_test: Test targets
        y_test_pred: Test predictions
        output_dir: Directory to save CSV files
    """
    logger.info("Saving predictions...")

    # Create arrays for predictions and metrics
    train_pred_data = np.column_stack(
        [
            y_train,
            y_train_pred,
            y_train_pred - y_train,
            100 * (y_train_pred - y_train) / np.maximum(1e-10, np.abs(y_train)),
        ]
    )

    test_pred_data = np.column_stack(
        [
            y_test,
            y_test_pred,
            y_test_pred - y_test,
            100 * (y_test_pred - y_test) / np.maximum(1e-10, np.abs(y_test)),
        ]
    )

    # Use CSVMgr to save the predictions
    CSVMgr.array_to_csv(
        train_pred_data,
        os.path.join(output_dir, "training_predictions.csv"),
        headers=["actual", "predicted", "error", "error_pct"],
        include_header=True,
    )

    CSVMgr.array_to_csv(
        test_pred_data,
        os.path.join(output_dir, "test_predictions.csv"),
        headers=["actual", "predicted", "error", "error_pct"],
        include_header=True,
    )


def generate_comparison_visualizations(results_df, best_result, output_dir):
    """
    Generate visualizations comparing different partition strategies and regression algorithms.

    Args:
        results_df: DataFrame with results for all combinations
        best_result: Dictionary with results for the best combination
        output_dir: Directory to save visualizations
    """
    # Create a directory for visualizations
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Filter out combinations with poor performance for better visualization
    filtered_df = results_df[results_df["test_r2"] > 0]

    # Bar plot of test R² for different combinations
    plt.figure(figsize=(12, 8))

    # Create a new column for the x-axis labels
    filtered_df["combination"] = filtered_df.apply(
        lambda row: f"{row['partition_mode']}\n{row['n_partitions']} partitions\n{row['regressor_type']}",
        axis=1,
    )

    # Sort by test R²
    filtered_df = filtered_df.sort_values("test_r2", ascending=False)

    # Take top 15 combinations for readability
    top_df = filtered_df.head(15)

    # Create the bar plot
    bars = plt.bar(top_df["combination"], top_df["test_r2"])

    # Highlight the best combination
    best_combo = f"{best_result['partition_mode']}\n{best_result['n_partitions']} partitions\n{best_result['regressor_type']}"
    best_idx = (
        top_df["combination"].tolist().index(best_combo)
        if best_combo in top_df["combination"].tolist()
        else None
    )

    if best_idx is not None:
        bars[best_idx].set_color("red")

    plt.title("Top 15 Combinations by Test R²")
    plt.ylabel("Test R²")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save the figure
    plt.savefig(os.path.join(plots_dir, "top_combinations_test_r2.png"))
    plt.close()

    # Heatmap of test R² for different partition modes and regressor types
    plt.figure(figsize=(12, 8))

    # Calculate mean test R² for each partition mode and regressor type
    pivot_df = filtered_df.pivot_table(
        index="partition_mode",
        columns="regressor_type",
        values="test_r2",
        aggfunc="mean",
    )

    # Create the heatmap
    im = plt.imshow(pivot_df.values, cmap="YlGnBu")

    # Add colorbar
    plt.colorbar(im, label="Mean Test R²")

    # Add labels
    plt.xticks(range(len(pivot_df.columns)), pivot_df.columns, rotation=45, ha="right")
    plt.yticks(range(len(pivot_df.index)), pivot_df.index)

    # Add a title
    plt.title("Mean Test R² by Partition Mode and Regressor Type")

    # Add values to cells
    for i in range(len(pivot_df.index)):
        for j in range(len(pivot_df.columns)):
            plt.text(
                j,
                i,
                f"{pivot_df.iloc[i, j]:.3f}",
                ha="center",
                va="center",
                color="black",
            )

    plt.tight_layout()

    # Save the figure
    plt.savefig(os.path.join(plots_dir, "mean_test_r2_heatmap.png"))
    plt.close()

    # Scatter plot of train R² vs test R²
    plt.figure(figsize=(10, 8))

    # Create the scatter plot
    scatter = plt.scatter(
        filtered_df["train_r2"],
        filtered_df["test_r2"],
        c=filtered_df["partition_mode"].astype("category").cat.codes,
        alpha=0.7,
        s=50,
        cmap="viridis",
    )

    # Add a legend
    legend1 = plt.legend(
        scatter.legend_elements()[0],
        filtered_df["partition_mode"].unique(),
        title="Partition Mode",
        loc="upper left",
    )
    plt.gca().add_artist(legend1)

    # Add a diagonal line
    lims = [
        np.min([plt.gca().get_xlim(), plt.gca().get_ylim()]),
        np.max([plt.gca().get_xlim(), plt.gca().get_ylim()]),
    ]
    plt.plot(lims, lims, "k--", alpha=0.3, zorder=0)

    # Highlight the best combination
    best_point = plt.scatter(
        best_result["train_r2"],
        best_result["test_r2"],
        c="red",
        s=200,
        marker="*",
        edgecolors="black",
        label="Best Combination",
    )
    plt.legend([best_point], ["Best Combination"], loc="lower right")

    # Add labels and title
    plt.xlabel("Train R²")
    plt.ylabel("Test R²")
    plt.title("Train R² vs Test R² for Different Combinations")

    # Add text for the best combination
    plt.annotate(
        f"{best_result['partition_mode']}, {best_result['n_partitions']} partitions, {best_result['regressor_type']}",
        xy=(best_result["train_r2"], best_result["test_r2"]),
        xytext=(10, -30),
        textcoords="offset points",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.3"),
    )

    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save the figure
    plt.savefig(os.path.join(plots_dir, "train_vs_test_r2.png"))
    plt.close()
